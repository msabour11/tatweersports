# # Copyright (c) 2026, Mohamed AbdElsabour
# # For license information, please see license.txt

# import frappe
# from frappe.utils import flt


# def execute(filters=None):
#     if not filters:
#         filters = {}

#     columns = get_columns()
#     data = get_data(filters)

#     return columns, data


# def get_columns():
#     return [
#         {"label": "Date", "fieldname": "date", "fieldtype": "Date", "width": 120},
#         {"label": "Salesperson", "fieldname": "salesperson", "fieldtype": "Data", "width": 150},
#         {"label": "POS Profile", "fieldname": "pos_profile", "fieldtype": "Data", "width": 150},

#         {"label": "Tara 200", "fieldname": "tara_200", "fieldtype": "Int", "width": 100},
#         {"label": "Tara 330", "fieldname": "tara_330", "fieldtype": "Int", "width": 100},
#         {"label": "Tara 600", "fieldname": "tara_600", "fieldtype": "Int", "width": 100},

#         {"label": "Vlona 200", "fieldname": "vlona_200", "fieldtype": "Int", "width": 100},
#         {"label": "Vlona 330", "fieldname": "vlona_330", "fieldtype": "Int", "width": 100},
#         {"label": "Vlona 600", "fieldname": "vlona_600", "fieldtype": "Int", "width": 100},
#         {"label": "Vlona 1500", "fieldname": "vlona_1500", "fieldtype": "Int", "width": 100},

#         {"label": "Shtine 200", "fieldname": "shtine_200", "fieldtype": "Int", "width": 100},
#         {"label": "Shtine 330", "fieldname": "shtine_330", "fieldtype": "Int", "width": 100},
#         {"label": "Shtine 600", "fieldname": "shtine_600", "fieldtype": "Int", "width": 100},
#         {"label": "Shtine 1500", "fieldname": "shtine_1500", "fieldtype": "Int", "width": 100},

#         {"label": "Sale Qty", "fieldname": "sale_qty", "fieldtype": "Int", "width": 100},

#         {"label": "Cash Sale", "fieldname": "cash_sale", "fieldtype": "Currency", "width": 150},
#         {"label": "Card Sale", "fieldname": "card_sale", "fieldtype": "Currency", "width": 150},
#         {"label": "Credit Sale", "fieldname": "credit_sale", "fieldtype": "Currency", "width": 150},
#         {"label": "Online Transfer", "fieldname": "online_transfer", "fieldtype": "Currency", "width": 150},
#         {"label": "Cash Collection", "fieldname": "cash_collection", "fieldtype": "Currency", "width": 150},
#     ]


# def get_data(filters):
#     conditions = ""
#     values = {}

#     if filters.get("from_date") and filters.get("to_date"):
#         conditions = " AND date BETWEEN %(from_date)s AND %(to_date)s"
#         values.update({
#             "from_date": filters["from_date"],
#             "to_date": filters["to_date"],
#         })

#     query = f"""
#         SELECT
#             final.date,
#             final.salesperson,
#             final.pos_profile,
#             COALESCE(final.tara_200, 0) AS tara_200,
#             COALESCE(final.tara_330, 0) AS tara_330,
#             COALESCE(final.tara_600, 0) AS tara_600,
#             COALESCE(final.vlona_200, 0) AS vlona_200,
#             COALESCE(final.vlona_330, 0) AS vlona_330,
#             COALESCE(final.vlona_600, 0) AS vlona_600,
#             COALESCE(final.vlona_1500, 0) AS vlona_1500,
#             COALESCE(final.shtine_200, 0) AS shtine_200,
#             COALESCE(final.shtine_330, 0) AS shtine_330,
#             COALESCE(final.shtine_600, 0) AS shtine_600,
#             COALESCE(final.shtine_1500, 0) AS shtine_1500,
#             COALESCE(final.sale_qty, 0) AS sale_qty,
#             COALESCE(final.cash_sale, 0) AS cash_sale,
#             COALESCE(final.card_sale, 0) AS card_sale,
#             COALESCE(final.credit_sale, 0) AS credit_sale,
#             COALESCE(final.online_transfer, 0) AS online_transfer,
#             COALESCE(final.cash_collection, 0) AS cash_collection
#         FROM (
#             -- Sales Invoice
#             SELECT
#                 DATE(si.posting_date) AS date,
#                 (
#                     SELECT GROUP_CONCAT(DISTINCT ppu.custom_user_name)
#                     FROM `tabPOS Profile User` ppu
#                     WHERE ppu.parent = si.pos_profile
#                       AND ppu.custom_user_type = 'Salesman'
#                 ) AS salesperson,
#                 si.pos_profile,

#                 SUM(q.tara_200) AS tara_200,
#                 SUM(q.tara_330) AS tara_330,
#                 SUM(q.tara_600) AS tara_600,
#                 SUM(q.vlona_200) AS vlona_200,
#                 SUM(q.vlona_330) AS vlona_330,
#                 SUM(q.vlona_600) AS vlona_600,
#                 SUM(q.vlona_1500) AS vlona_1500,
#                 SUM(q.shtine_200) AS shtine_200,
#                 SUM(q.shtine_330) AS shtine_330,
#                 SUM(q.shtine_600) AS shtine_600,
#                 SUM(q.shtine_1500) AS shtine_1500,
#                 SUM(q.total_qty) AS sale_qty,

#                 SUM(IFNULL(cash.total_cash, 0)) AS cash_sale,
#                 SUM(IFNULL(card.total_card, 0)) AS card_sale,
#                 SUM(CASE WHEN si.status IN ('Unpaid', 'Overdue') THEN si.grand_total ELSE 0 END) AS credit_sale,
#                 0 AS online_transfer,
#                 0 AS cash_collection

#             FROM `tabSales Invoice` si

#             LEFT JOIN (
#                 SELECT
#                     parent,
#                     SUM(CASE WHEN item_code = 'TARA Water 200ml Carton 48 pcs' THEN qty ELSE 0 END) AS tara_200,
#                     SUM(CASE WHEN item_code = 'TARA Water 330 ML Carton 40pcs' THEN qty ELSE 0 END) AS tara_330,
#                     SUM(CASE WHEN item_code = 'TARA Water 600ML Carton 30pcs' THEN qty ELSE 0 END) AS tara_600,

#                     SUM(CASE WHEN item_code = 'VLONA Water 200ml Carton 48 pcs' THEN qty ELSE 0 END) AS vlona_200,
#                     SUM(CASE WHEN item_code = 'VLONA Water 330 ML Carton 40pcs' THEN qty ELSE 0 END) AS vlona_330,
#                     SUM(CASE WHEN item_code = 'VLONA Water 600ML Carton 30pcs' THEN qty ELSE 0 END) AS vlona_600,
#                     SUM(CASE WHEN item_code = 'VLONA Water 1500 ML Carton 12pcs' THEN qty ELSE 0 END) AS vlona_1500,

#                     SUM(CASE WHEN item_code = 'shtine water 200ml carton 48 pcs' THEN qty ELSE 0 END) AS shtine_200,
#                     SUM(CASE WHEN item_code = 'Shtine Water 330ml Carton 40 Pcs' THEN qty ELSE 0 END) AS shtine_330,
#                     SUM(CASE WHEN item_code = 'Shtine Water 600ml Carton 30 Pcs' THEN qty ELSE 0 END) AS shtine_600,
#                     SUM(CASE WHEN item_code = 'Shtine Water 1500ml Carton 12 Pcs' THEN qty ELSE 0 END) AS shtine_1500,

#                     (
#                         SUM(qty)
#                     ) AS total_qty
#                 FROM `tabSales Invoice Item`
#                 GROUP BY parent
#             ) q ON q.parent = si.name

#             LEFT JOIN (
#                 SELECT parent, SUM(amount) AS total_cash
#                 FROM `tabSales Invoice Payment`
#                 WHERE LOWER(mode_of_payment) LIKE '%%cash%%'
#                 GROUP BY parent
#             ) cash ON cash.parent = si.name

#             LEFT JOIN (
#                 SELECT parent, SUM(amount) AS total_card
#                 FROM `tabSales Invoice Payment`
#                 WHERE LOWER(mode_of_payment) NOT LIKE '%%cash%%'
#                 GROUP BY parent
#             ) card ON card.parent = si.name

#             WHERE si.docstatus = 1
#             GROUP BY DATE(si.posting_date), si.pos_profile, salesperson

#             UNION ALL

#             -- Online Transfer
#             SELECT
#                 DATE(pe.posting_date),
#                 ppu.custom_user_name,
#                 ppu.pos_profile,
#                 0,0,0,0,0,0,0,0,0,0,0,
#                 0,0,0,
#                 SUM(pe.paid_amount),
#                 0
#             FROM `tabPayment Entry` pe
#             LEFT JOIN `tabPOS Profile User` ppu
#                 ON ppu.custom_sales_person = pe.custom_salesman
#             WHERE pe.docstatus = 1
#               AND pe.mode_of_payment NOT LIKE '%%cash%%'
#             GROUP BY DATE(pe.posting_date), pe.custom_salesman

#             UNION ALL

#             -- Cash Collection
#             SELECT
#                 DATE(pe.posting_date),
#                 ppu.custom_user_name,
#                 ppu.pos_profile,
#                 0,0,0,0,0,0,0,0,0,0,0,
#                 0,0,0,
#                 0,
#                 SUM(pe.paid_amount)
#             FROM `tabPayment Entry` pe
#             LEFT JOIN `tabPOS Profile User` ppu
#                 ON ppu.custom_sales_person = pe.custom_salesman
#             WHERE pe.docstatus = 1
#               AND pe.mode_of_payment LIKE '%%cash%%'
#             GROUP BY DATE(pe.posting_date), pe.custom_salesman
#         ) final
#         WHERE 1=1 {conditions}
#         ORDER BY final.date, final.pos_profile, final.salesperson
#     """

#     raw_data = frappe.db.sql(query, values, as_dict=True)

#     grouped = {}
#     for row in raw_data:
#         key = (row["date"], row["salesperson"], row["pos_profile"])
#         if key not in grouped:
#             grouped[key] = row
#         else:
#             for k in row:
#                 if k not in ("date", "salesperson", "pos_profile"):
#                     grouped[key][k] += flt(row[k])

#     return list(grouped.values())


#################group three brands sales report#######################


# Copyright (c) 2026, Mohamed AbdElsabour and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt


def execute(filters=None):
    if not filters:
        filters = {}

    columns = get_columns()
    data = get_data(filters)

    return columns, data


def get_columns():
    return [
        {"label": "Date", "fieldname": "date", "fieldtype": "Date", "width": 120},
        {
            "label": "Salesperson",
            "fieldname": "salesperson",
            "fieldtype": "Data",
            "width": 150,
        },
        {
            "label": "POS Profile",
            "fieldname": "pos_profile",
            "fieldtype": "Data",
            "width": 150,
        },
        {
            "label": "Tara 200",
            "fieldname": "tara_200",
            "fieldtype": "Int",
            "width": 100,
        },
        {
            "label": "Tara 330",
            "fieldname": "tara_330",
            "fieldtype": "Int",
            "width": 100,
        },
        {
            "label": "Tara 600",
            "fieldname": "tara_600",
            "fieldtype": "Int",
            "width": 100,
        },
        {
            "label": "Vlona 200",
            "fieldname": "vlona_200",
            "fieldtype": "Int",
            "width": 100,
        },
        {
            "label": "Vlona 330",
            "fieldname": "vlona_330",
            "fieldtype": "Int",
            "width": 100,
        },
        {
            "label": "Vlona 600",
            "fieldname": "vlona_600",
            "fieldtype": "Int",
            "width": 100,
        },
        {
            "label": "Vlona 1500",
            "fieldname": "vlona_1500",
            "fieldtype": "Int",
            "width": 100,
        },
        {
            "label": "Shtine 200",
            "fieldname": "shtine_200",
            "fieldtype": "Int",
            "width": 100,
        },
        {
            "label": "Shtine 330",
            "fieldname": "shtine_330",
            "fieldtype": "Int",
            "width": 100,
        },
        {
            "label": "Shtine 600",
            "fieldname": "shtine_600",
            "fieldtype": "Int",
            "width": 100,
        },
        {
            "label": "Shtine 1500",
            "fieldname": "shtine_1500",
            "fieldtype": "Int",
            "width": 100,
        },
        {
            "label": "Sale Qty",
            "fieldname": "sale_qty",
            "fieldtype": "Int",
            "width": 100,
        },
        {
            "label": "Cash Sale (Cash Mode)",
            "fieldname": "cash_sale",
            "fieldtype": "Currency",
            "width": 150,
        },
        {
            "label": "Card Sale",
            "fieldname": "card_sale",
            "fieldtype": "Currency",
            "width": 150,
        },
        {
            "label": "Credit Sale",
            "fieldname": "credit_sale",
            "fieldtype": "Currency",
            "width": 150,
        },
        {
            "label": "Online Transfer",
            "fieldname": "online_transfer",
            "fieldtype": "Currency",
            "width": 150,
        },
        {
            "label": "Cash Collection",
            "fieldname": "cash_collection",
            "fieldtype": "Currency",
            "width": 150,
        },
    ]


def get_data(filters):
    conditions = ""
    values = {}

    if filters.get("from_date") and filters.get("to_date"):
        conditions = " AND date BETWEEN %(from_date)s AND %(to_date)s"
        values.update(
            {"from_date": filters["from_date"], "to_date": filters["to_date"]}
        )

    query = f"""
        SELECT
            final.date,
            final.salesperson,
            final.pos_profile,
            COALESCE(final.tara_200, 0) AS tara_200,
            COALESCE(final.tara_330, 0) AS tara_330,
            COALESCE(final.tara_600, 0) AS tara_600,
            COALESCE(final.vlona_200, 0) AS vlona_200,
            COALESCE(final.vlona_330, 0) AS vlona_330,
            COALESCE(final.vlona_600, 0) AS vlona_600,
            COALESCE(final.vlona_1500, 0) AS vlona_1500,
            COALESCE(final.shtine_200, 0) AS shtine_200,
            COALESCE(final.shtine_330, 0) AS shtine_330,
            COALESCE(final.shtine_600, 0) AS shtine_600,
            COALESCE(final.shtine_1500, 0) AS shtine_1500,
            COALESCE(final.sale_qty, 0) AS sale_qty,
            COALESCE(final.cash_sale, 0) AS cash_sale,
            COALESCE(final.card_sale, 0) AS card_sale,
            COALESCE(final.credit_sale, 0) AS credit_sale,
            COALESCE(final.online_transfer, 0) AS online_transfer,
            COALESCE(final.cash_collection, 0) AS cash_collection
        FROM (
            -- Sales Invoice Data
            SELECT
                DATE(si.posting_date) AS date,
                (
                    SELECT GROUP_CONCAT(DISTINCT ppu.custom_user_name)
                    FROM `tabPOS Profile User` ppu
                    WHERE ppu.parent = si.pos_profile
                      AND ppu.custom_user_type = 'Salesman'
                ) AS salesperson,
                si.pos_profile,
                SUM(IFNULL(qty.tara_200, 0)) AS tara_200,
                SUM(IFNULL(qty.tara_330, 0)) AS tara_330,
                SUM(IFNULL(qty.tara_600, 0)) AS tara_600,
                SUM(IFNULL(qty.vlona_200, 0)) AS vlona_200,
                SUM(IFNULL(qty.vlona_330, 0)) AS vlona_330,
                SUM(IFNULL(qty.vlona_600, 0)) AS vlona_600,
                SUM(IFNULL(qty.vlona_1500, 0)) AS vlona_1500,
                SUM(IFNULL(qty.shtine_200, 0)) AS shtine_200,
                SUM(IFNULL(qty.shtine_330, 0)) AS shtine_330,
                SUM(IFNULL(qty.shtine_600, 0)) AS shtine_600,
                SUM(IFNULL(qty.shtine_1500, 0)) AS shtine_1500,
                SUM(IFNULL(qty.total_qty, 0)) AS sale_qty,
                SUM(IFNULL(cash.total_cash, 0)) AS cash_sale,
                SUM(IFNULL(card.total_card, 0)) AS card_sale,
                SUM(CASE WHEN si.status IN ('Unpaid', 'Overdue') THEN si.grand_total ELSE 0 END) AS credit_sale,
                0 AS online_transfer,
                0 AS cash_collection
            FROM `tabSales Invoice` si
            LEFT JOIN (
                SELECT
                    parent,
                    SUM(CASE WHEN item_code = 'TARA Water 200ml Carton 48 pcs' THEN qty ELSE 0 END) AS tara_200,
                    SUM(CASE WHEN item_code = 'TARA Water 330 ML Carton 40pcs' THEN qty ELSE 0 END) AS tara_330,
                    SUM(CASE WHEN item_code = 'TARA Water 600ML Carton 30pcs' THEN qty ELSE 0 END) AS tara_600,
                    SUM(CASE WHEN item_code = 'VLONA Water 200ml Carton 48 pcs' THEN qty ELSE 0 END) AS vlona_200,
                    SUM(CASE WHEN item_code = 'VLONA Water 330 ML Carton 40pcs' THEN qty ELSE 0 END) AS vlona_330,
                    SUM(CASE WHEN item_code = 'VLONA Water 600ML Carton 30pcs' THEN qty ELSE 0 END) AS vlona_600,
                    SUM(CASE WHEN item_code = 'VLONA Water 1500 ML Carton 12pcs' THEN qty ELSE 0 END) AS vlona_1500,
                    SUM(CASE WHEN item_code = 'Shtine Water 200ml Carton 48 pcs' THEN qty ELSE 0 END) AS shtine_200,
                    SUM(CASE WHEN item_code = 'Shtine Water 330ml Carton 40 Pcs' THEN qty ELSE 0 END) AS shtine_330,
                    SUM(CASE WHEN item_code = 'Shtine Water 600ml Carton 30 Pcs' THEN qty ELSE 0 END) AS shtine_600,
                    SUM(CASE WHEN item_code = 'Shtine Water 1500ml Carton 12 Pcs' THEN qty ELSE 0 END) AS shtine_1500,
                    (
                        SUM(CASE WHEN item_code = 'TARA Water 200ml Carton 48 pcs' THEN qty ELSE 0 END) +
                        SUM(CASE WHEN item_code = 'TARA Water 330 ML Carton 40pcs' THEN qty ELSE 0 END) +
                        SUM(CASE WHEN item_code = 'TARA Water 600ML Carton 30pcs' THEN qty ELSE 0 END) +
                        SUM(CASE WHEN item_code = 'VLONA Water 200ml Carton 48 pcs' THEN qty ELSE 0 END) +
                        SUM(CASE WHEN item_code = 'VLONA Water 330 ML Carton 40pcs' THEN qty ELSE 0 END) +
                        SUM(CASE WHEN item_code = 'VLONA Water 600ML Carton 30pcs' THEN qty ELSE 0 END) +
                        SUM(CASE WHEN item_code = 'VLONA Water 1500 ML Carton 12pcs' THEN qty ELSE 0 END) +
                        SUM(CASE WHEN item_code = 'Shtine Water 200ml Carton 48 pcs' THEN qty ELSE 0 END) +
                        SUM(CASE WHEN item_code = 'Shtine Water 330ml Carton 40 Pcs' THEN qty ELSE 0 END) +
                        SUM(CASE WHEN item_code = 'Shtine Water 600ml Carton 30 Pcs' THEN qty ELSE 0 END) +
                        SUM(CASE WHEN item_code = 'Shtine Water 1500ml Carton 12 Pcs' THEN qty ELSE 0 END)
                    ) AS total_qty
                FROM `tabSales Invoice Item`
                GROUP BY parent
            ) qty ON qty.parent = si.name
            LEFT JOIN (
                SELECT parent, SUM(amount) AS total_cash
                FROM `tabSales Invoice Payment`
                WHERE LOWER(mode_of_payment) LIKE '%%cash%%'
                GROUP BY parent
            ) cash ON cash.parent = si.name
            LEFT JOIN (
                SELECT parent, SUM(amount) AS total_card
                FROM `tabSales Invoice Payment`
                WHERE LOWER(mode_of_payment) NOT LIKE '%%cash%%'
                GROUP BY parent
            ) card ON card.parent = si.name
            WHERE si.docstatus = 1
            GROUP BY DATE(si.posting_date), si.pos_profile, salesperson

            UNION ALL

            -- Payment Entry Data (Online Transfer) - FIXED
            SELECT
                DATE(pe.posting_date) AS date,
                ppu.custom_user_name AS salesperson,
                ppu.pos_profile,
                0 AS tara_200,
                0 AS tara_330,
                0 AS tara_600,
                0 AS vlona_200,
                0 AS vlona_330,
                0 AS vlona_600,
                0 AS vlona_1500,
                0 AS shtine_200,
                0 AS shtine_330,
                0 AS shtine_600,
                0 AS shtine_1500,
                0 AS sale_qty,
                0 AS cash_sale,
                0 AS card_sale,
                0 AS credit_sale,
                SUM(pe.paid_amount) AS online_transfer,
                0 AS cash_collection
            FROM `tabPayment Entry` pe
            LEFT JOIN (
                SELECT 
                    custom_sales_person,
                    MAX(custom_user_name) as custom_user_name,
                    MAX(parent) AS pos_profile
                FROM `tabPOS Profile User`
                WHERE custom_sales_person IS NOT NULL
                GROUP BY custom_sales_person
            ) ppu ON ppu.custom_sales_person = pe.custom_salesman
            WHERE pe.docstatus = 1
              AND pe.mode_of_payment NOT LIKE '%%cash%%'
              AND pe.custom_salesman IS NOT NULL
            GROUP BY DATE(pe.posting_date), pe.custom_salesman

            UNION ALL

            -- Payment Entry Data (Cash Collection) - FIXED
            SELECT
                DATE(pe.posting_date) AS date,
                ppu.custom_user_name AS salesperson,
                ppu.pos_profile,
                0 AS tara_200,
                0 AS tara_330,
                0 AS tara_600,
                0 AS vlona_200,
                0 AS vlona_330,
                0 AS vlona_600,
                0 AS vlona_1500,
                0 AS shtine_200,
                0 AS shtine_330,
                0 AS shtine_600,
                0 AS shtine_1500,
                0 AS sale_qty,
                0 AS cash_sale,
                0 AS card_sale,
                0 AS credit_sale,
                0 AS online_transfer,
                SUM(pe.paid_amount) AS cash_collection
            FROM `tabPayment Entry` pe
            LEFT JOIN (
                SELECT 
                    custom_sales_person,
                    MAX(custom_user_name) as custom_user_name,
                    MAX(parent) AS pos_profile
                FROM `tabPOS Profile User`
                WHERE custom_sales_person IS NOT NULL
                GROUP BY custom_sales_person
            ) ppu ON ppu.custom_sales_person = pe.custom_salesman
            WHERE pe.docstatus = 1
              AND pe.mode_of_payment LIKE '%%cash%%'
              AND pe.custom_salesman IS NOT NULL
            GROUP BY DATE(pe.posting_date), pe.custom_salesman
        ) AS final
        WHERE 1=1 {conditions}
            AND (
                final.pos_profile IS NULL
                OR final.pos_profile IN (
                    SELECT name FROM `tabPOS Profile` WHERE disabled = 0
                )
            )
        ORDER BY final.date, final.pos_profile, final.salesperson
    """

    # Get the unioned data
    raw_data = frappe.db.sql(query, values, as_dict=True)

    # Group and aggregate the data
    grouped_data = {}
    for row in raw_data:
        key = (row["date"], row["salesperson"], row["pos_profile"])
        if key not in grouped_data:
            grouped_data[key] = {
                "date": row["date"],
                "salesperson": row["salesperson"],
                "pos_profile": row["pos_profile"],
                "tara_200": 0,
                "tara_330": 0,
                "tara_600": 0,
                "vlona_200": 0,
                "vlona_330": 0,
                "vlona_600": 0,
                "vlona_1500": 0,
                "shtine_200": 0,
                "shtine_330": 0,
                "shtine_600": 0,
                "shtine_1500": 0,
                "sale_qty": 0,
                "cash_sale": 0,
                "card_sale": 0,
                "credit_sale": 0,
                "online_transfer": 0,
                "cash_collection": 0,
            }

        # Sum all values
        for field in [
            "tara_200",
            "tara_330",
            "tara_600",
            "vlona_200",
            "vlona_330",
            "vlona_600",
            "vlona_1500",
            "shtine_200",
            "shtine_330",
            "shtine_600",
            "shtine_1500",
            "sale_qty",
            "cash_sale",
            "card_sale",
            "credit_sale",
            "online_transfer",
            "cash_collection",
        ]:
            grouped_data[key][field] += flt(row[field])

    return list(grouped_data.values())
