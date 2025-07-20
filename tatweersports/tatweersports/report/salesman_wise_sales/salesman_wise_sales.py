# # Copyright (c) 2025, Mohamed AbdElsabour and contributors
# # For license information, please see license.txt


# import frappe
# from frappe import _


# def execute(filters=None):
#     columns = get_columns()
#     data = get_data(filters)
#     return columns, data


# def get_columns():
#     return [
#         {"label": _("Date"), "fieldname": "date", "fieldtype": "Date", "width": 100},
#         {
#             "label": _("Salesperson"),
#             "fieldname": "salesperson",
#             "fieldtype": "Data",
#             "width": 150,
#         },
#         {
#             "label": _("Warehouse/Car"),
#             "fieldname": "set_warehouse",
#             "fieldtype": "Link",
#             "options": "Warehouse",
#             "width": 150,
#         },
#         {
#             "label": _("POS Profile"),
#             "fieldname": "pos_profile",
#             "fieldtype": "Link",
#             "options": "POS Profile",
#             "width": 150,
#         },
#         {
#             "label": _("Tara 200"),
#             "fieldname": "tara_200",
#             "fieldtype": "Int",
#             "width": 80,
#         },
#         {
#             "label": _("Tara 330"),
#             "fieldname": "tara_330",
#             "fieldtype": "Int",
#             "width": 80,
#         },
#         {
#             "label": _("Tara 600"),
#             "fieldname": "tara_600",
#             "fieldtype": "Int",
#             "width": 80,
#         },
#         {
#             "label": _("Sale Qty"),
#             "fieldname": "sale_qty",
#             "fieldtype": "Int",
#             "width": 80,
#         },
#         {
#             "label": _("Total Sale Amount"),
#             "fieldname": "total_sale_amount",
#             "fieldtype": "Currency",
#             "width": 120,
#         },
#         {
#             "label": _("Tara 200 Warehouse Qty"),
#             "fieldname": "tara_200_warehouse",
#             "fieldtype": "Float",
#             "width": 120,
#         },
#         {
#             "label": _("Tara 330 Warehouse Qty"),
#             "fieldname": "tara_330_warehouse",
#             "fieldtype": "Float",
#             "width": 120,
#         },
#         {
#             "label": _("Tara 600 Warehouse Qty"),
#             "fieldname": "tara_600_warehouse",
#             "fieldtype": "Float",
#             "width": 120,
#         },
#         {
#             "label": _("Total Warehouse Qty"),
#             "fieldname": "total_warehouse_qty",
#             "fieldtype": "Float",
#             "width": 120,
#         },
#         {
#             "label": _("Cash (Sales + Allocated)"),
#             "fieldname": "cash_total",
#             "fieldtype": "Currency",
#             "width": 140,
#         },
#         {
#             "label": _("Credit Card (Sales + Allocated)"),
#             "fieldname": "credit_card_total",
#             "fieldtype": "Currency",
#             "width": 160,
#         },
#         {
#             "label": _("Wire Transfer (Sales + Allocated)"),
#             "fieldname": "wire_transfer_total",
#             "fieldtype": "Currency",
#             "width": 160,
#         },
#         {
#             "label": _("Outstanding Amount"),
#             "fieldname": "outstanding_amount",
#             "fieldtype": "Currency",
#             "width": 140,
#         },
#     ]


# def get_data(filters):
#     conditions = get_conditions(filters)
#     query = """
#         SELECT
#             DATE(si.posting_date) AS date,
#             si.pos_profile,
#             (SELECT warehouse FROM `tabPOS Profile` WHERE name = si.pos_profile) AS set_warehouse,
#             SUM(IFNULL(qty.tara_200, 0)) AS tara_200,
#             SUM(IFNULL(qty.tara_330, 0)) AS tara_330,
#             SUM(IFNULL(qty.tara_600, 0)) AS tara_600,
#             SUM(IFNULL(qty.total_qty, 0)) AS sale_qty,
#             SUM(si.grand_total) AS total_sale_amount,
#             SUM(IFNULL(pay_cash.si_amount, 0) + IFNULL(alloc_cash.allocated, 0)) AS cash_total,
#             SUM(IFNULL(pay_card.si_amount, 0) + IFNULL(alloc_card.allocated, 0)) AS credit_card_total,
#             SUM(IFNULL(pay_wire.si_amount, 0) + IFNULL(alloc_wire.allocated, 0)) AS wire_transfer_total,
#             SUM(si.outstanding_amount) AS outstanding_amount
#         FROM `tabSales Invoice` si
#         LEFT JOIN (
#             SELECT
#                 parent,
#                 SUM(CASE WHEN item_code = 'TARA Water 200ml Carton 48 pcs' THEN qty ELSE 0 END) AS tara_200,
#                 SUM(CASE WHEN item_code = 'TARA Water 330 ML Carton 40pcs' THEN qty ELSE 0 END) AS tara_330,
#                 SUM(CASE WHEN item_code = 'TARA Water 600ML Carton 30pcs' THEN qty ELSE 0 END) AS tara_600,
#                 SUM(qty) AS total_qty
#             FROM `tabSales Invoice Item`
#             GROUP BY parent
#         ) qty ON qty.parent = si.name
#         LEFT JOIN (
#             SELECT parent, SUM(amount) AS si_amount
#             FROM `tabSales Invoice Payment`
#             WHERE LOWER(mode_of_payment) LIKE '%%cash%%'
#             GROUP BY parent
#         ) pay_cash ON pay_cash.parent = si.name
#         LEFT JOIN (
#             SELECT parent, SUM(amount) AS si_amount
#             FROM `tabSales Invoice Payment`
#             WHERE LOWER(mode_of_payment) LIKE '%%credit%%'
#             GROUP BY parent
#         ) pay_card ON pay_card.parent = si.name
#         LEFT JOIN (
#             SELECT parent, SUM(amount) AS si_amount
#             FROM `tabSales Invoice Payment`
#             WHERE LOWER(mode_of_payment) LIKE '%%wire%%'
#             GROUP BY parent
#         ) pay_wire ON pay_wire.parent = si.name
#         LEFT JOIN (
#             SELECT ped.reference_name AS si_name, SUM(ped.allocated_amount) AS allocated
#             FROM `tabPayment Entry Reference` ped
#             JOIN `tabPayment Entry` pe ON ped.parent = pe.name
#             WHERE pe.docstatus = 1 AND LOWER(pe.mode_of_payment) LIKE '%%cash%%'
#             GROUP BY ped.reference_name
#         ) alloc_cash ON alloc_cash.si_name = si.name
#         LEFT JOIN (
#             SELECT ped.reference_name AS si_name, SUM(ped.allocated_amount) AS allocated
#             FROM `tabPayment Entry Reference` ped
#             JOIN `tabPayment Entry` pe ON ped.parent = pe.name
#             WHERE pe.docstatus = 1 AND LOWER(pe.mode_of_payment) LIKE '%%credit%%'
#             GROUP BY ped.reference_name
#         ) alloc_card ON alloc_card.si_name = si.name
#         LEFT JOIN (
#             SELECT ped.reference_name AS si_name, SUM(ped.allocated_amount) AS allocated
#             FROM `tabPayment Entry Reference` ped
#             JOIN `tabPayment Entry` pe ON ped.parent = pe.name
#             WHERE pe.docstatus = 1 AND LOWER(pe.mode_of_payment) LIKE '%%wire%%'
#             GROUP BY ped.reference_name
#         ) alloc_wire ON alloc_wire.si_name = si.name
#         WHERE si.docstatus = 1 {conditions}
#         GROUP BY DATE(si.posting_date), si.pos_profile
#         ORDER BY DATE(si.posting_date),
#                  (SELECT MIN(IFNULL(custom_order, 999999))
#                   FROM `tabPOS Profile User`
#                   WHERE parent = si.pos_profile
#                   AND custom_user_type = 'Salesman'),
#                  si.pos_profile
#     """.format(
#         conditions=conditions
#     )

#     data = frappe.db.sql(query, filters, as_dict=True)
#     add_salesperson_data(data)
#     add_warehouse_quantities(data)
#     return data


# def add_salesperson_data(data):
#     """Add salesperson data with proper ordering based on custom_order field"""
#     pos_profiles = list({d["pos_profile"] for d in data})
#     if not pos_profiles:
#         return

#     # Get salesperson data with explicit ordering
#     salesperson_data = frappe.db.sql(
#         """
#         SELECT
#             parent as pos_profile,
#             custom_user_name,
#             custom_order
#         FROM `tabPOS Profile User`
#         WHERE parent IN %(profiles)s
#         AND custom_user_type = 'Salesman'
#         ORDER BY parent ASC,
#                  custom_order ASC,
#                  custom_user_name ASC
#     """,
#         {"profiles": pos_profiles},
#         as_dict=True,
#     )

#     # Group by pos_profile maintaining the SQL order
#     profile_salespeople = {}

#     for sp in salesperson_data:
#         profile = sp["pos_profile"]
#         if profile not in profile_salespeople:
#             profile_salespeople[profile] = []

#         name = sp["custom_user_name"] if sp["custom_user_name"] else "No Salesperson"
#         profile_salespeople[profile].append(name)

#     # Add salesperson data to main data
#     for row in data:
#         profile = row["pos_profile"]
#         if profile in profile_salespeople:
#             row["salesperson"] = ", ".join(profile_salespeople[profile])
#         else:
#             row["salesperson"] = "No Salesperson"


# def add_warehouse_quantities(data):
#     pos_profiles = list({d["pos_profile"] for d in data})
#     if not pos_profiles:
#         return

#     wh_data = frappe.db.sql(
#         """
#         SELECT
#             pp.name AS pos_profile,
#             SUM(CASE WHEN bin.item_code = 'TARA Water 200ml Carton 48 pcs' THEN bin.actual_qty ELSE 0 END) AS tara_200_warehouse,
#             SUM(CASE WHEN bin.item_code = 'TARA Water 330 ML Carton 40pcs' THEN bin.actual_qty ELSE 0 END) AS tara_330_warehouse,
#             SUM(CASE WHEN bin.item_code = 'TARA Water 600ML Carton 30pcs' THEN bin.actual_qty ELSE 0 END) AS tara_600_warehouse
#         FROM `tabPOS Profile` pp
#         LEFT JOIN `tabBin` bin ON bin.warehouse = pp.warehouse
#         WHERE pp.name IN %(profiles)s
#         GROUP BY pp.name
#     """,
#         {"profiles": pos_profiles},
#         as_dict=True,
#     )

#     wh_map = {row.pos_profile: row for row in wh_data}

#     shown_profiles = set()
#     for row in data:
#         profile = row.pos_profile
#         if profile in wh_map and profile not in shown_profiles:
#             wh = wh_map[profile]
#             row["tara_200_warehouse"] = wh["tara_200_warehouse"]
#             row["tara_330_warehouse"] = wh["tara_330_warehouse"]
#             row["tara_600_warehouse"] = wh["tara_600_warehouse"]
#             row["total_warehouse_qty"] = (
#                 wh["tara_200_warehouse"]
#                 + wh["tara_330_warehouse"]
#                 + wh["tara_600_warehouse"]
#             )
#             shown_profiles.add(profile)
#         else:
#             row["tara_200_warehouse"] = None
#             row["tara_330_warehouse"] = None
#             row["tara_600_warehouse"] = None
#             row["total_warehouse_qty"] = None


# def get_conditions(filters):
#     conditions = []
#     if filters.get("from_date"):
#         conditions.append("si.posting_date >= %(from_date)s")
#     if filters.get("to_date"):
#         conditions.append("si.posting_date <= %(to_date)s")
#     if filters.get("pos_profile"):
#         conditions.append("si.pos_profile = %(pos_profile)s")
#     if filters.get("set_warehouse"):
#         conditions.append(
#             "(SELECT warehouse FROM `tabPOS Profile` WHERE name = si.pos_profile) = %(set_warehouse)s"
#         )
#     return " AND " + " AND ".join(conditions) if conditions else ""


#####################refactored code#####################

# Copyright (c) 2025, Mohamed AbdElsabour and contributors
# For license information, please see license.txt


import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {"label": _("Date"), "fieldname": "date", "fieldtype": "Date", "width": 100},
        {
            "label": _("Salesperson"),
            "fieldname": "salesperson",
            "fieldtype": "Data",
            "width": 150,
        },
        {
            "label": _("Warehouse/Car"),
            "fieldname": "set_warehouse",
            "fieldtype": "Link",
            "options": "Warehouse",
            "width": 150,
        },
        # {
        #     "label": _("POS Profile"),
        #     "fieldname": "pos_profile",
        #     "fieldtype": "Link",
        #     "options": "POS Profile",
        #     "width": 150,
        # },
        {
            "label": _("Tara 200"),
            "fieldname": "tara_200",
            "fieldtype": "Int",
            "width": 80,
        },
        {
            "label": _("Tara 330"),
            "fieldname": "tara_330",
            "fieldtype": "Int",
            "width": 80,
        },
        {
            "label": _("Tara 600"),
            "fieldname": "tara_600",
            "fieldtype": "Int",
            "width": 80,
        },
        {
            "label": _("Sale Qty"),
            "fieldname": "sale_qty",
            "fieldtype": "Int",
            "width": 80,
        },
        {
            "label": _("Total Sale Amount"),
            "fieldname": "total_sale_amount",
            "fieldtype": "Currency",
            "width": 120,
        },
        {
            "label": _("Tara 200 Warehouse Qty"),
            "fieldname": "tara_200_warehouse",
            "fieldtype": "Int",
            "width": 80,
        },
        {
            "label": _("Tara 330 Warehouse Qty"),
            "fieldname": "tara_330_warehouse",
            "fieldtype": "Int",
            "width": 80,
        },
        {
            "label": _("Tara 600 Warehouse Qty"),
            "fieldname": "tara_600_warehouse",
            "fieldtype": "Int",
            "width": 80,
        },
        {
            "label": _("Total Warehouse Qty"),
            "fieldname": "total_warehouse_qty",
            "fieldtype": "Int",
            "width": 80,
        },
        {
            "label": _("Cash"),
            "fieldname": "cash_total",
            "fieldtype": "Currency",
            "width": 120,
        },
        {
            "label": _("Card"),
            "fieldname": "credit_card_total",
            "fieldtype": "Currency",
            "width": 120,
        },
        {
            "label": _("Wire Transfer"),
            "fieldname": "wire_transfer_total",
            "fieldtype": "Currency",
            "width": 120,
        },
        {
            "label": _("Credit Amount"),
            "fieldname": "outstanding_amount",
            "fieldtype": "Currency",
            "width": 120,
        },
    ]


def get_data(filters):
    conditions = get_conditions(filters)
    query = """
        SELECT
            DATE(si.posting_date) AS date,
            si.pos_profile,
            (SELECT warehouse FROM `tabPOS Profile` WHERE name = si.pos_profile) AS set_warehouse,
            SUM(IFNULL(qty.tara_200, 0)) AS tara_200,
            SUM(IFNULL(qty.tara_330, 0)) AS tara_330,
            SUM(IFNULL(qty.tara_600, 0)) AS tara_600,
            SUM(IFNULL(qty.total_qty, 0)) AS sale_qty,
            SUM(si.grand_total) AS total_sale_amount,
            SUM(IFNULL(pay_cash.si_amount, 0) + IFNULL(alloc_cash.allocated, 0)) AS cash_total,
            SUM(IFNULL(pay_card.si_amount, 0) + IFNULL(alloc_card.allocated, 0)) AS credit_card_total,
            SUM(IFNULL(pay_wire.si_amount, 0) + IFNULL(alloc_wire.allocated, 0)) AS wire_transfer_total,
            SUM(si.outstanding_amount) AS outstanding_amount
        FROM `tabSales Invoice` si
        LEFT JOIN (
            SELECT
                parent,
                SUM(CASE WHEN item_code = 'TARA Water 200ml Carton 48 pcs' THEN qty ELSE 0 END) AS tara_200,
                SUM(CASE WHEN item_code = 'TARA Water 330 ML Carton 40pcs' THEN qty ELSE 0 END) AS tara_330,
                SUM(CASE WHEN item_code = 'TARA Water 600ML Carton 30pcs' THEN qty ELSE 0 END) AS tara_600,
                SUM(qty) AS total_qty
            FROM `tabSales Invoice Item`
            GROUP BY parent
        ) qty ON qty.parent = si.name
        LEFT JOIN (
            SELECT parent, SUM(amount) AS si_amount
            FROM `tabSales Invoice Payment`
            WHERE LOWER(mode_of_payment) LIKE '%%cash%%'
            GROUP BY parent
        ) pay_cash ON pay_cash.parent = si.name
        LEFT JOIN (
            SELECT parent, SUM(amount) AS si_amount
            FROM `tabSales Invoice Payment`
            WHERE LOWER(mode_of_payment) LIKE '%%credit%%'
            GROUP BY parent
        ) pay_card ON pay_card.parent = si.name
        LEFT JOIN (
            SELECT parent, SUM(amount) AS si_amount
            FROM `tabSales Invoice Payment`
            WHERE LOWER(mode_of_payment) LIKE '%%wire%%'
            GROUP BY parent
        ) pay_wire ON pay_wire.parent = si.name
        LEFT JOIN (
            SELECT ped.reference_name AS si_name, SUM(ped.allocated_amount) AS allocated
            FROM `tabPayment Entry Reference` ped
            JOIN `tabPayment Entry` pe ON ped.parent = pe.name
            WHERE pe.docstatus = 1 AND LOWER(pe.mode_of_payment) LIKE '%%cash%%'
            GROUP BY ped.reference_name
        ) alloc_cash ON alloc_cash.si_name = si.name
        LEFT JOIN (
            SELECT ped.reference_name AS si_name, SUM(ped.allocated_amount) AS allocated
            FROM `tabPayment Entry Reference` ped
            JOIN `tabPayment Entry` pe ON ped.parent = pe.name
            WHERE pe.docstatus = 1 AND LOWER(pe.mode_of_payment) LIKE '%%credit%%'
            GROUP BY ped.reference_name
        ) alloc_card ON alloc_card.si_name = si.name
        LEFT JOIN (
            SELECT ped.reference_name AS si_name, SUM(ped.allocated_amount) AS allocated
            FROM `tabPayment Entry Reference` ped
            JOIN `tabPayment Entry` pe ON ped.parent = pe.name
            WHERE pe.docstatus = 1 AND LOWER(pe.mode_of_payment) LIKE '%%wire%%'
            GROUP BY ped.reference_name
        ) alloc_wire ON alloc_wire.si_name = si.name
        WHERE si.docstatus = 1 {conditions}
        GROUP BY DATE(si.posting_date), si.pos_profile
        ORDER BY DATE(si.posting_date), 
                 (SELECT MIN(IFNULL(custom_order, 999999)) 
                  FROM `tabPOS Profile User` 
                  WHERE parent = si.pos_profile 
                  AND custom_user_type = 'Salesman'), 
                 si.pos_profile
    """.format(
        conditions=conditions
    )

    data = frappe.db.sql(query, filters, as_dict=True)
    add_salesperson_data(data)
    add_warehouse_quantities(data)
    return data


def add_salesperson_data(data):
    """Add salesperson data with proper ordering based on custom_order field"""
    pos_profiles = list({d["pos_profile"] for d in data})
    if not pos_profiles:
        return

    # Get salesperson data with explicit ordering
    salesperson_data = frappe.db.sql(
        """
        SELECT 
            parent as pos_profile,
            custom_user_name,
            custom_order
        FROM `tabPOS Profile User` 
        WHERE parent IN %(profiles)s 
        AND custom_user_type = 'Salesman'
        ORDER BY parent ASC, 
                 custom_order ASC, 
                 custom_user_name ASC
    """,
        {"profiles": pos_profiles},
        as_dict=True,
    )

    # Group by pos_profile maintaining the SQL order
    profile_salespeople = {}

    for sp in salesperson_data:
        profile = sp["pos_profile"]
        if profile not in profile_salespeople:
            profile_salespeople[profile] = []

        name = sp["custom_user_name"] if sp["custom_user_name"] else "No Salesperson"
        profile_salespeople[profile].append(name)

    # Add salesperson data to main data
    for row in data:
        profile = row["pos_profile"]
        if profile in profile_salespeople:
            row["salesperson"] = ", ".join(profile_salespeople[profile])
        else:
            row["salesperson"] = "No Salesperson"


def add_warehouse_quantities(data):
    pos_profiles = list({d["pos_profile"] for d in data})
    if not pos_profiles:
        return

    wh_data = frappe.db.sql(
        """
        SELECT
            pp.name AS pos_profile,
            SUM(CASE WHEN bin.item_code = 'TARA Water 200ml Carton 48 pcs' THEN bin.actual_qty ELSE 0 END) AS tara_200_warehouse,
            SUM(CASE WHEN bin.item_code = 'TARA Water 330 ML Carton 40pcs' THEN bin.actual_qty ELSE 0 END) AS tara_330_warehouse,
            SUM(CASE WHEN bin.item_code = 'TARA Water 600ML Carton 30pcs' THEN bin.actual_qty ELSE 0 END) AS tara_600_warehouse
        FROM `tabPOS Profile` pp
        LEFT JOIN `tabBin` bin ON bin.warehouse = pp.warehouse
        WHERE pp.name IN %(profiles)s
        GROUP BY pp.name
    """,
        {"profiles": pos_profiles},
        as_dict=True,
    )

    wh_map = {row.pos_profile: row for row in wh_data}

    shown_profiles = set()
    for row in data:
        profile = row.pos_profile
        if profile in wh_map and profile not in shown_profiles:
            wh = wh_map[profile]
            row["tara_200_warehouse"] = wh["tara_200_warehouse"]
            row["tara_330_warehouse"] = wh["tara_330_warehouse"]
            row["tara_600_warehouse"] = wh["tara_600_warehouse"]
            row["total_warehouse_qty"] = (
                wh["tara_200_warehouse"]
                + wh["tara_330_warehouse"]
                + wh["tara_600_warehouse"]
            )
            shown_profiles.add(profile)
        else:
            row["tara_200_warehouse"] = None
            row["tara_330_warehouse"] = None
            row["tara_600_warehouse"] = None
            row["total_warehouse_qty"] = None


def get_conditions(filters):
    conditions = []
    if filters.get("from_date"):
        conditions.append("si.posting_date >= %(from_date)s")
    if filters.get("to_date"):
        conditions.append("si.posting_date <= %(to_date)s")
    if filters.get("pos_profile"):
        conditions.append("si.pos_profile = %(pos_profile)s")
    if filters.get("set_warehouse"):
        conditions.append(
            "(SELECT warehouse FROM `tabPOS Profile` WHERE name = si.pos_profile) = %(set_warehouse)s"
        )
    return " AND " + " AND ".join(conditions) if conditions else ""
