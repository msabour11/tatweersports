# Copyright (c) 2025, Mohamed AbdElsabour and contributors
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
                    (
                        SUM(CASE WHEN item_code = 'TARA Water 200ml Carton 48 pcs' THEN qty ELSE 0 END) +
                        SUM(CASE WHEN item_code = 'TARA Water 330 ML Carton 40pcs' THEN qty ELSE 0 END) +
                        SUM(CASE WHEN item_code = 'TARA Water 600ML Carton 30pcs' THEN qty ELSE 0 END)
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

            -- Payment Entry Data (Online Transfer)
            SELECT
                DATE(pe.posting_date) AS date,
                ppu.custom_user_name AS salesperson,
                ppu_profile.pos_profile,
                0 AS tara_200,
                0 AS tara_330,
                0 AS tara_600,
                0 AS sale_qty,
                0 AS cash_sale,
                0 AS card_sale,
                0 AS credit_sale,
                SUM(pe.paid_amount) AS online_transfer,
                0 AS cash_collection
            FROM `tabPayment Entry` pe
            JOIN `tabPOS Profile User` ppu ON ppu.custom_sales_person = pe.custom_salesman
            LEFT JOIN (
                SELECT DISTINCT custom_sales_person, parent AS pos_profile
                FROM `tabPOS Profile User`
                WHERE custom_sales_person IS NOT NULL
            ) ppu_profile ON ppu_profile.custom_sales_person = pe.custom_salesman
            WHERE pe.docstatus = 1
              AND pe.mode_of_payment NOT LIKE '%%cash%%'
            GROUP BY DATE(pe.posting_date), pe.custom_salesman, ppu.custom_user_name, ppu_profile.pos_profile

            UNION ALL

            -- Payment Entry Data (Cash Collection)
            SELECT
                DATE(pe.posting_date) AS date,
                ppu.custom_user_name AS salesperson,
                ppu_profile.pos_profile,
                0 AS tara_200,
                0 AS tara_330,
                0 AS tara_600,
                0 AS sale_qty,
                0 AS cash_sale,
                0 AS card_sale,
                0 AS credit_sale,
                0 AS online_transfer,
                SUM(pe.paid_amount) AS cash_collection
            FROM `tabPayment Entry` pe
            JOIN `tabPOS Profile User` ppu ON ppu.custom_sales_person = pe.custom_salesman
            LEFT JOIN (
                SELECT DISTINCT custom_sales_person, parent AS pos_profile
                FROM `tabPOS Profile User`
                WHERE custom_sales_person IS NOT NULL
            ) ppu_profile ON ppu_profile.custom_sales_person = pe.custom_salesman
            WHERE pe.docstatus = 1
              AND pe.mode_of_payment LIKE '%%cash%%'
            GROUP BY DATE(pe.posting_date), pe.custom_salesman, ppu.custom_user_name, ppu_profile.pos_profile
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
            "sale_qty",
            "cash_sale",
            "card_sale",
            "credit_sale",
            "online_transfer",
            "cash_collection",
        ]:
            grouped_data[key][field] += flt(row[field])

    return list(grouped_data.values())
