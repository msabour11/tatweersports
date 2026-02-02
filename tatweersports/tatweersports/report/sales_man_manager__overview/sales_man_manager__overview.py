# Copyright (c) 2026, Mohamed AbdElsabour and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


# ------------------------------------------------------------------
# 1.  DYNAMIC COLUMNS  (read Report Brand → items child-table)
# ------------------------------------------------------------------
def get_columns():
    """
    Build columns exactly like before, but the item-quantity columns
    are taken from Report Brand → items (only rows with enable=1).
    """
    cols = [
        {"fieldname": "date", "label": _("Date"), "fieldtype": "Date", "width": 100},
        {
            "fieldname": "salesperson",
            "label": _("Salesperson"),
            "fieldtype": "Data",
            "width": 150,
        },
        {
            "fieldname": "warehouse",
            "label": _("Car Number"),
            "fieldtype": "Link",
            "options": "Warehouse",
            "width": 150,
        },
    ]

    # --- dynamic part ------------------------------------------------
    for d in _get_report_brand_items():
        cols.append(
            {
                "fieldname": d.fieldname,
                "label": _(d.item_name or d.item_code),
                "fieldtype": "Int",
                "width": 100,
            }
        )
    # -----------------------------------------------------------------

    cols += [
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
    return cols


# ------------------------------------------------------------------
# 2.  DYNAMIC DATA  (same logic, but keys come from Report Brand)
# ------------------------------------------------------------------
def get_data(filters):
    from_date = filters.get("from_date")
    to_date = filters.get("to_date")
    if not (from_date and to_date):
        frappe.throw(_("Please select From Date and To Date"))

    invoices = _get_invoices(from_date, to_date)
    if not invoices:
        return []

    inv_names = [inv.name for inv in invoices]
    pos_sales = get_pos_salespersons()
    pos_wh = get_pos_warehouses()
    item_qty_map = get_item_quantities(inv_names)  # dynamic
    pay_map = get_payment_details(inv_names)
    collections = get_payment_collections(from_date, to_date, invoices)

    # pre-build dynamic item keys
    rb_items = _get_report_brand_items()  # list of simple namespace objects
    item_codes = [d.item_code for d in rb_items]

    grouped = {}
    for inv in invoices:
        key = (inv.posting_date, inv.pos_profile)
        if key not in grouped:
            grouped[key] = {
                "date": inv.posting_date,
                "pos_profile": inv.pos_profile,
                "salesperson": pos_sales.get(inv.pos_profile, ""),
                "warehouse": pos_wh.get(inv.pos_profile, ""),
                "sale_qty": 0,
                "cash_sale": 0,
                "card_sale": 0,
                "credit_sale": 0,
                "overpaid": 0,
                "online_transfer": 0,
                "cash_collection": 0,
                "total_sale_amount": 0,
            }
            # initialise every dynamic item column to 0
            for d in rb_items:
                grouped[key][d.fieldname] = 0

        row = grouped[key]

        # quantities --------------------------------------------------
        if inv.name in item_qty_map:
            qty_dict = item_qty_map[inv.name]
            row["sale_qty"] += qty_dict.get("total_qty", 0)
            for d in rb_items:
                row[d.fieldname] += qty_dict.get(d.item_code, 0)

        # payments ----------------------------------------------------
        if inv.name in pay_map:
            pm = pay_map[inv.name]
            row["cash_sale"] += pm.get("cash", 0)
            row["card_sale"] += pm.get("card", 0)

        # credit / overpaid ------------------------------------------
        if inv.status in ("Unpaid", "Overdue") and inv.outstanding_amount > 0:
            row["credit_sale"] += inv.grand_total
        if inv.outstanding_amount < 0:
            row["overpaid"] += inv.outstanding_amount

        row["total_sale_amount"] += inv.grand_total

    # attach collections ---------------------------------------------
    for coll in collections:
        key = (coll["date"], coll["pos_profile"])
        if key in grouped:
            if coll["mode"] == "online":
                grouped[key]["online_transfer"] += coll["amount"]
            else:
                grouped[key]["cash_collection"] += coll["amount"]

    # total collection column
    data = list(grouped.values())
    for r in data:
        r["total_cash"] = r["online_transfer"] + r["cash_collection"]

    data.sort(key=lambda x: (x["date"], x["pos_profile"]))
    return data


# ------------------------------------------------------------------
# 3.  DYNAMIC SQL FOR ITEM QUANTITIES
# ------------------------------------------------------------------
def get_item_quantities(invoice_names):
    """
    Returns dict  {  invoice_name :  { item_code:qty, …, total_qty:x }  }
    built from Report Brand items (enabled=1).
    """
    if not invoice_names:
        return {}

    rb_items = _get_report_brand_items()
    if not rb_items:
        return {}

    # build SELECT list
    selects = [
        "SUM(CASE WHEN item_code = %s THEN qty ELSE 0 END) AS `%s`"
        % (frappe.db.escape(d.item_code), d.item_code)
        for d in rb_items
    ]
    selects.append(
        "SUM(CASE WHEN item_code IN ({}) THEN qty ELSE 0 END) AS total_qty".format(
            ",".join(["%s"] * len(rb_items))
        )
    )

    sql = """
        SELECT
            parent,
            {selects}
        FROM `tabSales Invoice Item`
        WHERE parent IN ({placeholders})
        GROUP BY parent
    """.format(
        selects=",\n".join(selects), placeholders=",".join(["%s"] * len(invoice_names))
    )

    # flatten parameters
    params_sum = [d.item_code for d in rb_items] + invoice_names
    result = frappe.db.sql(sql, params_sum, as_dict=1)

    # convert to map
    return {r.parent: r for r in result}


# ------------------------------------------------------------------
# 4.  HELPERS  (unchanged except tiny helper below)
# ------------------------------------------------------------------
def _get_report_brand_items():
    """
    Read the single doctype 'Report Brand' → child table 'items'
    returns list of simple objects with:
        item_code, item_name, fieldname, enable
    (memoised per request)
    """
    if hasattr(frappe.local, "_rb_items_cache"):
        return frappe.local._rb_items_cache

    doc = frappe.get_single("Report Brand")
    items = []
    for child in doc.items:
        if not child.enable:
            continue
        # sanitised fieldname
        fld = "item_" + frappe.scrub(child.item_code)
        items.append(
            frappe._dict(
                item_code=child.item_code,
                item_name=child.item_name or child.item_code,
                fieldname=fld,
                enable=child.enable,
            )
        )
    frappe.local._rb_items_cache = items
    return items


# -------------  unchanged original helpers  -------------------------
def get_pos_salespersons():
    result = frappe.db.sql(
        """
        SELECT parent as pos_profile,
               GROUP_CONCAT(DISTINCT custom_user_name) as salesperson
        FROM `tabPOS Profile User`
        WHERE custom_user_type = 'Salesman'
        GROUP BY parent
    """,
        as_dict=1,
    )
    return {r.pos_profile: r.salesperson for r in result}


def get_pos_warehouses():
    result = frappe.db.sql(
        """
        SELECT name as pos_profile, warehouse
        FROM `tabPOS Profile`
    """,
        as_dict=1,
    )
    return {r.pos_profile: r.warehouse for r in result}


def get_payment_details(invoice_names):
    if not invoice_names:
        return {}
    result = frappe.db.sql(
        """
        SELECT parent,
               SUM(CASE WHEN LOWER(mode_of_payment) LIKE '%%cash%%' THEN amount ELSE 0 END) as cash,
               SUM(CASE WHEN LOWER(mode_of_payment) NOT LIKE '%%cash%%' THEN amount ELSE 0 END) as card
        FROM `tabSales Invoice Payment`
        WHERE parent IN ({})
        GROUP BY parent
    """.format(
            ",".join(["%s"] * len(invoice_names))
        ),
        invoice_names,
        as_dict=1,
    )
    return {r.parent: r for r in result}


def get_payment_collections(from_date, to_date, invoices):
    # … exactly the same code you already have …
    sales_team_map, invoice_pos_map = {}, {}
    for inv in invoices:
        sales_team_map[inv.name] = [
            sp.sales_person
            for sp in frappe.db.sql(
                """
                SELECT sales_person FROM `tabSales Team` WHERE parent=%s
            """,
                inv.name,
                as_dict=1,
            )
        ]
        invoice_pos_map[inv.name] = inv.pos_profile

    collections = frappe.db.sql(
        """
        SELECT DATE(pe.posting_date) as date,
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
        if coll.reference_name in invoice_pos_map:
            mode = (
                "cash"
                if coll.mode_of_payment and "cash" in coll.mode_of_payment.lower()
                else "online"
            )
            result.append(
                {
                    "date": coll.date,
                    "pos_profile": invoice_pos_map[coll.reference_name],
                    "amount": coll.allocated_amount or 0,
                    "mode": mode,
                }
            )
    return result


def _get_invoices(from_date, to_date):
    return frappe.db.sql(
        """
        SELECT name, posting_date, pos_profile, status, outstanding_amount, grand_total
        FROM `tabSales Invoice`
        WHERE docstatus = 1
          AND IFNULL(is_return, 0) = 0
          AND posting_date BETWEEN %s AND %s
        ORDER BY posting_date, pos_profile
    """,
        (from_date, to_date),
        as_dict=1,
    )
