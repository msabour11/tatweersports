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
#             "label": _("Cash Sale (Cash Mode)"),
#             "fieldname": "cash_sale",
#             "fieldtype": "Currency",
#             "width": 120,
#         },
#         {
#             "label": _("Card Sale"),
#             "fieldname": "card_sale",
#             "fieldtype": "Currency",
#             "width": 100,
#         },
#         {
#             "label": _("Credit Sale"),
#             "fieldname": "credit_sale",
#             "fieldtype": "Currency",
#             "width": 100,
#         },
#         {
#             "label": _("Online Transfer"),
#             "fieldname": "online_transfer",
#             "fieldtype": "Currency",
#             "width": 120,
#         },
#         {
#             "label": _("Cash Collection"),
#             "fieldname": "cash_collection",
#             "fieldtype": "Currency",
#             "width": 120,
#         },
#     ]


# def get_data(filters):
#     conditions = get_conditions(filters)

#     query = """
#         SELECT
#             DATE(si.posting_date) AS date,
#             (
#                 SELECT GROUP_CONCAT(DISTINCT ppu.custom_user_name)
#                 FROM `tabPOS Profile User` ppu
#                 WHERE ppu.parent = si.pos_profile AND ppu.custom_user_type = 'Salesman'
#             ) AS salesperson,

#             (select warehouse from `tabPOS Profile` where name = si.pos_profile) AS set_warehouse,
#             si.pos_profile AS pos_profile,
#             -- Total Sale Amount
#             SUM(si.grand_total) AS total_sale_amount,

#             -- Item Quantities
#             SUM(IFNULL(qty.tara_200, 0)) AS tara_200,
#             SUM(IFNULL(qty.tara_330, 0)) AS tara_330,
#             SUM(IFNULL(qty.tara_600, 0)) AS tara_600,
#             -- Warehouse Quantities
#             IFNULL(wh_qty.tara_200_warehouse, 0) AS tara_200_warehouse,
#             IFNULL(wh_qty.tara_330_warehouse, 0) AS tara_330_warehouse,
#             IFNULL(wh_qty.tara_600_warehouse, 0) AS tara_600_warehouse,
#             SUM(IFNULL(qty.total_qty, 0)) AS sale_qty,
#             (IFNULL(wh_qty.tara_200_warehouse, 0) + IFNULL(wh_qty.tara_330_warehouse, 0) + IFNULL(wh_qty.tara_600_warehouse, 0)) AS total_warehouse_qty,
#             -- Payments
#             SUM(IFNULL(cash.total_cash, 0)) AS cash_sale,
#             SUM(IFNULL(card.total_card, 0)) AS card_sale,
#             -- Credit Sale
#             SUM(CASE
#                 WHEN si.status IN ('Unpaid', 'Overdue') THEN si.grand_total
#                 ELSE 0
#             END) AS credit_sale,
#             -- Online Transfer Collection
#             (
#                 SELECT SUM(ped.allocated_amount)
#                 FROM `tabPayment Entry` pe
#                 JOIN `tabPayment Entry Reference` ped ON ped.parent = pe.name
#                 WHERE pe.docstatus = 1
#                   AND pe.mode_of_payment NOT LIKE '%%cash%%'
#                   AND DATE(pe.posting_date) = DATE(si.posting_date)
#                   AND pe.custom_salesman IN (
#                       SELECT st.sales_person FROM `tabSales Team` st WHERE st.parent = si.name
#                   )
#             ) AS online_transfer,
#             -- Cash Collection
#             (
#                 SELECT SUM(ped.allocated_amount)
#                 FROM `tabPayment Entry` pe
#                 JOIN `tabPayment Entry Reference` ped ON ped.parent = pe.name
#                 WHERE pe.docstatus = 1
#                   AND pe.mode_of_payment LIKE '%%cash%%'
#                   AND DATE(pe.posting_date) = DATE(si.posting_date)
#                   AND pe.custom_salesman IN (
#                       SELECT st.sales_person FROM `tabSales Team` st WHERE st.parent = si.name
#                   )
#             ) AS cash_collection
#         FROM
#             `tabSales Invoice` si
#         -- Join summarized item quantities
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
#         -- Join warehouse quantities
#         LEFT JOIN (
#             SELECT
#                 pp.name as pos_profile,
#                 SUM(CASE WHEN bin.item_code = 'TARA Water 200ml Carton 48 pcs' THEN bin.actual_qty ELSE 0 END) AS tara_200_warehouse,
#                 SUM(CASE WHEN bin.item_code = 'TARA Water 330 ML Carton 40pcs' THEN bin.actual_qty ELSE 0 END) AS tara_330_warehouse,
#                 SUM(CASE WHEN bin.item_code = 'TARA Water 600ML Carton 30pcs' THEN bin.actual_qty ELSE 0 END) AS tara_600_warehouse
#             FROM `tabPOS Profile` pp
#             LEFT JOIN `tabBin` bin ON bin.warehouse = pp.warehouse
#             WHERE bin.item_code IN ('TARA Water 200ml Carton 48 pcs', 'TARA Water 330 ML Carton 40pcs', 'TARA Water 600ML Carton 30pcs')
#             GROUP BY pp.name, pp.warehouse
#         ) wh_qty ON wh_qty.pos_profile = si.pos_profile
#         -- Join pre-summarized cash
#         LEFT JOIN (
#             SELECT parent, SUM(amount) AS total_cash
#             FROM `tabSales Invoice Payment`
#             WHERE LOWER(mode_of_payment) LIKE '%%cash%%'
#             GROUP BY parent
#         ) cash ON cash.parent = si.name
#         -- Join pre-summarized card
#         LEFT JOIN (
#             SELECT parent, SUM(amount) AS total_card
#             FROM `tabSales Invoice Payment`
#             WHERE LOWER(mode_of_payment) NOT LIKE '%%cash%%'
#             GROUP BY parent
#         ) card ON card.parent = si.name
#         WHERE
#             si.docstatus = 1
#             {conditions}
#         GROUP BY
#             DATE(si.posting_date),
#             si.pos_profile,
#             (
#                 SELECT GROUP_CONCAT(DISTINCT ppu.custom_user_name)
#                 FROM `tabPOS Profile User` ppu
#                 WHERE ppu.parent = si.pos_profile AND ppu.custom_user_type = 'Salesman'
#             ),
#             wh_qty.tara_200_warehouse,
#             wh_qty.tara_330_warehouse,
#             wh_qty.tara_600_warehouse
#         ORDER BY
#             DATE(si.posting_date), si.pos_profile
#     """.format(
#         conditions=conditions
#     )

#     return frappe.db.sql(query, filters, as_dict=True)


# def get_conditions(filters):
#     conditions = []

#     if filters.get("from_date"):
#         conditions.append("si.posting_date >= %(from_date)s")

#     if filters.get("to_date"):
#         conditions.append("si.posting_date <= %(to_date)s")

#     if filters.get("pos_profile"):
#         conditions.append("si.pos_profile = %(pos_profile)s")
#     if filters.get("set_warehouse"):
#         conditions.append("si.set_warehouse = %(set_warehouse)s")

#     if filters.get("salesperson"):
#         conditions.append(
#             """
#             EXISTS (
#                 SELECT 1 FROM `tabPOS Profile User` ppu
#                 WHERE ppu.parent = si.pos_profile
#                 AND ppu.custom_user_type = 'Salesman'
#                 AND ppu.custom_user_name = %(salesperson)s
#             )
#         """
#         )

#     return " AND " + " AND ".join(conditions) if conditions else ""


#####################################################3
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
        {
            "label": _("POS Profile"),
            "fieldname": "pos_profile",
            "fieldtype": "Link",
            "options": "POS Profile",
            "width": 150,
        },
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
            "fieldtype": "Float",
            "width": 120,
        },
        {
            "label": _("Tara 330 Warehouse Qty"),
            "fieldname": "tara_330_warehouse",
            "fieldtype": "Float",
            "width": 120,
        },
        {
            "label": _("Tara 600 Warehouse Qty"),
            "fieldname": "tara_600_warehouse",
            "fieldtype": "Float",
            "width": 120,
        },
        {
            "label": _("Total Warehouse Qty"),
            "fieldname": "total_warehouse_qty",
            "fieldtype": "Float",
            "width": 120,
        },
        {
            "label": _("Cash Sale (Cash Mode)"),
            "fieldname": "cash_sale",
            "fieldtype": "Currency",
            "width": 120,
        },
        {
            "label": _("Card Sale"),
            "fieldname": "card_sale",
            "fieldtype": "Currency",
            "width": 100,
        },
        {
            "label": _("Credit Sale"),
            "fieldname": "credit_sale",
            "fieldtype": "Currency",
            "width": 100,
        },
        {
            "label": _("Online Transfer"),
            "fieldname": "online_transfer",
            "fieldtype": "Currency",
            "width": 120,
        },
        {
            "label": _("Cash Collection"),
            "fieldname": "cash_collection",
            "fieldtype": "Currency",
            "width": 120,
        },
    ]


def get_data(filters):
    conditions = get_conditions(filters)

    # Get sales data and warehouse data separately, then combine them properly
    sales_data = get_sales_data(filters, conditions)
    warehouse_data = get_warehouse_data(filters)

    # Combine the data with proper warehouse quantity handling
    return combine_sales_and_warehouse_data(sales_data, warehouse_data)


def get_sales_data(filters, conditions):
    """Get sales data grouped by date and pos_profile"""
    query = """
        SELECT
            DATE(si.posting_date) AS date,
            si.pos_profile,
            (SELECT warehouse FROM `tabPOS Profile` WHERE name = si.pos_profile) AS set_warehouse,
            -- Group salespersons for this date and pos_profile
            GROUP_CONCAT(DISTINCT 
                CASE 
                    WHEN ppu.custom_user_name IS NOT NULL 
                    THEN ppu.custom_user_name 
                    ELSE 'No Salesperson' 
                END 
                ORDER BY ppu.custom_user_name 
                SEPARATOR ', '
            ) AS salesperson,
            
            -- Sales quantities (aggregated)
            SUM(IFNULL(qty.tara_200, 0)) AS tara_200,
            SUM(IFNULL(qty.tara_330, 0)) AS tara_330,
            SUM(IFNULL(qty.tara_600, 0)) AS tara_600,
            SUM(IFNULL(qty.total_qty, 0)) AS sale_qty,
            
            -- Sales amounts (aggregated)
            SUM(si.grand_total) AS total_sale_amount,
            
            -- Payments (aggregated)
            SUM(IFNULL(cash.total_cash, 0)) AS cash_sale,
            SUM(IFNULL(card.total_card, 0)) AS card_sale,
            
            -- Credit Sale
            SUM(CASE 
                WHEN si.status IN ('Unpaid', 'Overdue') THEN si.grand_total
                ELSE 0 
            END) AS credit_sale,
            
            -- Collections (aggregated by date and pos_profile)
            COALESCE(collections.online_transfer, 0) AS online_transfer,
            COALESCE(collections.cash_collection, 0) AS cash_collection
            
        FROM `tabSales Invoice` si
        
        -- Join salespersons
        LEFT JOIN `tabPOS Profile User` ppu ON ppu.parent = si.pos_profile 
            AND ppu.custom_user_type = 'Salesman'
        
        -- Join item quantities
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
        
        -- Join cash payments
        LEFT JOIN (
            SELECT parent, SUM(amount) AS total_cash
            FROM `tabSales Invoice Payment`
            WHERE LOWER(mode_of_payment) LIKE '%%cash%%'
            GROUP BY parent
        ) cash ON cash.parent = si.name
        
        -- Join card payments
        LEFT JOIN (
            SELECT parent, SUM(amount) AS total_card
            FROM `tabSales Invoice Payment`
            WHERE LOWER(mode_of_payment) NOT LIKE '%%cash%%'
            GROUP BY parent
        ) card ON card.parent = si.name
        
        -- Join collections (pre-aggregated by date and pos_profile)
        LEFT JOIN (
            SELECT 
                DATE(pe.posting_date) AS collection_date,
                pp.name AS pos_profile,
                SUM(CASE 
                    WHEN pe.mode_of_payment NOT LIKE '%%cash%%' 
                    THEN ped.allocated_amount 
                    ELSE 0 
                END) AS online_transfer,
                SUM(CASE 
                    WHEN pe.mode_of_payment LIKE '%%cash%%' 
                    THEN ped.allocated_amount 
                    ELSE 0 
                END) AS cash_collection
            FROM `tabPayment Entry` pe
            JOIN `tabPayment Entry Reference` ped ON ped.parent = pe.name
            JOIN `tabPOS Profile User` ppu ON ppu.custom_user_name = pe.custom_salesman
                AND ppu.custom_user_type = 'Salesman'
            JOIN `tabPOS Profile` pp ON pp.name = ppu.parent
            WHERE pe.docstatus = 1
            GROUP BY DATE(pe.posting_date), pp.name
        ) collections ON collections.collection_date = DATE(si.posting_date) 
            AND collections.pos_profile = si.pos_profile
        
        WHERE si.docstatus = 1 {conditions}
        GROUP BY DATE(si.posting_date), si.pos_profile
        ORDER BY DATE(si.posting_date), si.pos_profile
    """.format(
        conditions=conditions
    )

    return frappe.db.sql(query, filters, as_dict=True)


def get_warehouse_data(filters):
    """Get current warehouse quantities - this is NOT date-dependent"""
    query = """
        SELECT
            pp.name as pos_profile,
            pp.warehouse,
            SUM(CASE WHEN bin.item_code = 'TARA Water 200ml Carton 48 pcs' THEN bin.actual_qty ELSE 0 END) AS tara_200_warehouse,
            SUM(CASE WHEN bin.item_code = 'TARA Water 330 ML Carton 40pcs' THEN bin.actual_qty ELSE 0 END) AS tara_330_warehouse,
            SUM(CASE WHEN bin.item_code = 'TARA Water 600ML Carton 30pcs' THEN bin.actual_qty ELSE 0 END) AS tara_600_warehouse
        FROM `tabPOS Profile` pp
        LEFT JOIN `tabBin` bin ON bin.warehouse = pp.warehouse
        WHERE bin.item_code IN ('TARA Water 200ml Carton 48 pcs', 'TARA Water 330 ML Carton 40pcs', 'TARA Water 600ML Carton 30pcs')
    """

    # Add warehouse filter if specified
    if filters.get("set_warehouse"):
        query += " AND pp.warehouse = %(set_warehouse)s"

    # Add pos_profile filter if specified
    if filters.get("pos_profile"):
        query += " AND pp.name = %(pos_profile)s"

    query += " GROUP BY pp.name, pp.warehouse"

    return frappe.db.sql(query, filters, as_dict=True)


def combine_sales_and_warehouse_data(sales_data, warehouse_data):
    """Combine sales data with warehouse data, showing warehouse qty only once per POS Profile"""

    # Create a dictionary for quick warehouse lookup
    warehouse_dict = {}
    for wh in warehouse_data:
        warehouse_dict[wh["pos_profile"]] = wh

    # Track which POS Profiles we've already shown warehouse quantities for
    warehouse_shown = set()

    result = []

    for sale in sales_data:
        pos_profile = sale["pos_profile"]

        # Add warehouse quantities only for the first occurrence of each POS Profile
        if pos_profile not in warehouse_shown and pos_profile in warehouse_dict:
            wh_data = warehouse_dict[pos_profile]
            sale["tara_200_warehouse"] = wh_data["tara_200_warehouse"]
            sale["tara_330_warehouse"] = wh_data["tara_330_warehouse"]
            sale["tara_600_warehouse"] = wh_data["tara_600_warehouse"]
            sale["total_warehouse_qty"] = (
                wh_data["tara_200_warehouse"]
                + wh_data["tara_330_warehouse"]
                + wh_data["tara_600_warehouse"]
            )
            warehouse_shown.add(pos_profile)
        else:
            # For subsequent dates with same POS Profile, show warehouse as 0 or None
            sale["tara_200_warehouse"] = None
            sale["tara_330_warehouse"] = None
            sale["tara_600_warehouse"] = None
            sale["total_warehouse_qty"] = None

        result.append(sale)

    return result


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

    # if filters.get("salesperson"):
    #     conditions.append(
    #         """
    #         EXISTS (
    #             SELECT 1 FROM `tabPOS Profile User` ppu
    #             WHERE ppu.parent = si.pos_profile
    #             AND ppu.custom_user_type = 'Salesman'
    #             AND ppu.custom_user_name = %(salesperson)s
    #         )
    #     """
    #     )

    return " AND " + " AND ".join(conditions) if conditions else ""
