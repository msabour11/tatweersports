# Copyright (c) 2026, Mohamed AbdElsabour and contributors
# For license information, please see license.txt


import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {"fieldname": "date", "label": _("Date"), "fieldtype": "Date", "width": 100},
        {
            "fieldname": "salesperson",
            "label": _("Salesperson"),
            "fieldtype": "Data",
            "width": 150,
        },
        # {
        #     "fieldname": "pos_profile",
        #     "label": _("POS Profile"),
        #     "fieldtype": "Link",
        #     "options": "POS Profile",
        #     "width": 150,
        # },
        {
            "fieldname": "warehouse",
            "label": _("Car Number"),
            "fieldtype": "Link",
            "options": "Warehouse",
            "width": 150,
        },
        {
            "fieldname": "vlona_200",
            "label": _("Vlona 200"),
            "fieldtype": "Int",
            "width": 100,
        },
        {
            "fieldname": "vlona_330",
            "label": _("Vlona 330"),
            "fieldtype": "Int",
            "width": 100,
        },
        {
            "fieldname": "vlona_600",
            "label": _("Vlona 600"),
            "fieldtype": "Int",
            "width": 100,
        },
        {
            "fieldname": "sale_qty",
            "label": _("Sale Qty"),
            "fieldtype": "Int",
            "width": 100,
        },
        {
            "fieldname": "total_sale_amount",
            "label": _("Total Sale Amount"),
            "fieldtype": "Currency",
            "width": 150,
        },
        {
            "fieldname": "cash_sale",
            "label": _("Cash"),
            "fieldtype": "Currency",
            "width": 150,
        },
        {
            "fieldname": "card_sale",
            "label": _("Card"),
            "fieldtype": "Currency",
            "width": 120,
        },
        {
            "fieldname": "credit_sale",
            "label": _("Credit Sale"),
            "fieldtype": "Currency",
            "width": 120,
        },
        # {
        #     "fieldname": "overpaid",
        #     "label": _("Overpaid / Mistaken Invoices"),
        #     "fieldtype": "Currency",
        #     "width": 180,
        # },
        {
            "fieldname": "cash_collection",
            "label": _("Cash Collection"),
            "fieldtype": "Currency",
            "width": 140,
        },
        {
            "fieldname": "online_transfer",
            "label": _("Card Collection"),
            "fieldtype": "Currency",
            "width": 140,
        },
        {
            "fieldname": "total_cash",
            "label": _("Total Collection"),
            "fieldtype": "Currency",
            "width": 120,
        },
    ]


def get_data(filters):
    from_date = filters.get("from_date")
    to_date = filters.get("to_date")

    if not from_date or not to_date:
        frappe.throw(_("Please select From Date and To Date"))

    # Get all sales invoices with basic info
    invoices = frappe.db.sql(
        """
        SELECT 
            si.name,
            DATE(si.posting_date) as posting_date,
            si.pos_profile,
            si.status,
            si.outstanding_amount,
            si.grand_total
        FROM `tabSales Invoice` si
        WHERE si.docstatus = 1
            AND IFNULL(si.is_return, 0) = 0
            AND si.posting_date BETWEEN %s AND %s
        ORDER BY si.posting_date, si.pos_profile
    """,
        (from_date, to_date),
        as_dict=1,
    )

    # Get all salespersons for POS profiles
    pos_salespersons = get_pos_salespersons()

    # Get warehouses for POS profiles
    pos_warehouses = get_pos_warehouses()

    # Get item quantities for all invoices
    item_quantities = get_item_quantities([inv.name for inv in invoices])

    # Get payment details for all invoices
    payment_details = get_payment_details([inv.name for inv in invoices])

    # Get payment entries (collections)
    collections = get_payment_collections(from_date, to_date, invoices)

    # gruop data by date and POS profile
    grouped_data = {}

    for inv in invoices:
        key = (inv.posting_date, inv.pos_profile)

        if key not in grouped_data:
            grouped_data[key] = {
                "date": inv.posting_date,
                "pos_profile": inv.pos_profile,
                "salesperson": pos_salespersons.get(inv.pos_profile, ""),
                "warehouse": pos_warehouses.get(inv.pos_profile, ""),
                "vlona_200": 0,
                "vlona_330": 0,
                "vlona_600": 0,
                "sale_qty": 0,
                "cash_sale": 0,
                "card_sale": 0,
                "credit_sale": 0,
                "overpaid": 0,
                "online_transfer": 0,
                "cash_collection": 0,
                "total_sale_amount": 0,
            }

        row = grouped_data[key]

        # add item quantities
        if inv.name in item_quantities:
            qty = item_quantities[inv.name]
            row["vlona_200"] += qty.get("vlona_200", 0)
            row["vlona_330"] += qty.get("vlona_330", 0)
            row["vlona_600"] += qty.get("vlona_600", 0)
            row["sale_qty"] += qty.get("total_qty", 0)

        # add payment details
        if inv.name in payment_details:
            payments = payment_details[inv.name]
            row["cash_sale"] += payments.get("cash", 0)
            row["card_sale"] += payments.get("card", 0)

        # Add credit sale
        if inv.status in ("Unpaid", "Overdue") and inv.outstanding_amount > 0:
            row["credit_sale"] += inv.grand_total

        # Add overpaid
        if inv.outstanding_amount < 0:
            row["overpaid"] += inv.outstanding_amount

        # add total sale amount (grand total)
        row["total_sale_amount"] += inv.grand_total

    # add collections to grouped data
    for coll in collections:
        key = (coll["date"], coll["pos_profile"])
        if key in grouped_data:
            if coll["mode"] == "online":
                grouped_data[key]["online_transfer"] += coll["amount"]
            else:
                grouped_data[key]["cash_collection"] += coll["amount"]

    # Convert to list and sort
    data = list(grouped_data.values())

    # calculate total_cash for each row
    for row in data:
        row["total_cash"] = row["online_transfer"] + row["cash_collection"]

    data.sort(key=lambda x: (x["date"], x["pos_profile"]))

    return data


def get_pos_salespersons():
    """Get salespersons mapped to POS profiles"""
    result = frappe.db.sql(
        """
        SELECT 
            parent as pos_profile,
            GROUP_CONCAT(DISTINCT custom_user_name) as salesperson
        FROM `tabPOS Profile User`
        WHERE custom_user_type = 'Salesman'
        GROUP BY parent
    """,
        as_dict=1,
    )

    return {r.pos_profile: r.salesperson for r in result}


def get_pos_warehouses():
    """Get warehouses mapped to POS profiles"""
    result = frappe.db.sql(
        """
        SELECT 
            name as pos_profile,
            warehouse
        FROM `tabPOS Profile`
    """,
        as_dict=1,
    )

    return {r.pos_profile: r.warehouse for r in result}


def get_item_quantities(invoice_names):
    """Get item quantities for invoices"""
    if not invoice_names:
        return {}

    result = frappe.db.sql(
        """
        SELECT
            parent,
            SUM(CASE WHEN item_code = 'VLONA Water 200ml Carton 48 pcs' THEN qty ELSE 0 END) as vlona_200,
            SUM(CASE WHEN item_code = 'VLONA Water 330 ML Carton 40pcs' THEN qty ELSE 0 END) as vlona_330,
            SUM(CASE WHEN item_code = 'VLONA Water 600ML Carton 30pcs' THEN qty ELSE 0 END) as vlona_600,
            (
                SUM(CASE WHEN item_code = 'VLONA Water 200ml Carton 48 pcs' THEN qty ELSE 0 END) +
                SUM(CASE WHEN item_code = 'VLONA Water 330 ML Carton 40pcs' THEN qty ELSE 0 END) +
                SUM(CASE WHEN item_code = 'VLONA Water 600ML Carton 30pcs' THEN qty ELSE 0 END)
            ) as total_qty
        FROM `tabSales Invoice Item`
        WHERE parent IN ({})
        GROUP BY parent
    """.format(
            ", ".join(["%s"] * len(invoice_names))
        ),
        invoice_names,
        as_dict=1,
    )

    return {r.parent: r for r in result}


def get_payment_details(invoice_names):
    """Get payment mode details for invoices"""
    if not invoice_names:
        return {}

    result = frappe.db.sql(
        """
        SELECT
            parent,
            SUM(CASE WHEN LOWER(mode_of_payment) LIKE '%%cash%%' THEN amount ELSE 0 END) as cash,
            SUM(CASE WHEN LOWER(mode_of_payment) NOT LIKE '%%cash%%' THEN amount ELSE 0 END) as card
        FROM `tabSales Invoice Payment`
        WHERE parent IN ({})
        GROUP BY parent
    """.format(
            ", ".join(["%s"] * len(invoice_names))
        ),
        invoice_names,
        as_dict=1,
    )

    return {r.parent: r for r in result}


def get_payment_collections(from_date, to_date, invoices):
    """Get payment entry collections"""
    #  sales team mapping for invoices
    sales_team_map = {}
    for inv in invoices:
        sales_persons = frappe.db.sql(
            """
            SELECT sales_person 
            FROM `tabSales Team` 
            WHERE parent = %s
        """,
            inv.name,
            as_dict=1,
        )
        sales_team_map[inv.name] = [sp.sales_person for sp in sales_persons]

    # get POS profile for each invoice
    invoice_pos_map = {inv.name: inv.pos_profile for inv in invoices}

    collections = frappe.db.sql(
        """
        SELECT
            DATE(pe.posting_date) as date,
            pe.custom_salesman,
            ped.reference_name,
            ped.allocated_amount,
            pe.mode_of_payment
        FROM `tabPayment Entry` pe
        JOIN `tabPayment Entry Reference` ped ON ped.parent = pe.name
        WHERE pe.docstatus = 1
            AND DATE(pe.posting_date) BETWEEN %s AND %s
    """,
        (from_date, to_date),
        as_dict=1,
    )

    result = []
    for coll in collections:
        # check if this payment belongs to our invoice set
        if coll.reference_name in invoice_pos_map:
            pos_profile = invoice_pos_map[coll.reference_name]
            mode = (
                "cash"
                if coll.mode_of_payment and "cash" in coll.mode_of_payment.lower()
                else "online"
            )

            result.append(
                {
                    "date": coll.date,
                    "pos_profile": pos_profile,
                    "amount": coll.allocated_amount or 0,
                    "mode": mode,
                }
            )

    return result
