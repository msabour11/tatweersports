# Copyright (c) 2025, Mohamed AbdElsabour and contributors
# For license information, please see license.txt


import frappe
from frappe.utils import flt


def execute(filters=None):
    if not filters:
        filters = {}

    warehouse_condition = ""
    if filters.get("warehouse"):
        warehouse_condition = "AND ppu.warehouse = %(warehouse)s"

    data = frappe.db.sql(
        f"""
        SELECT
            DATE(si.posting_date) AS date,
            ppu.salespersons AS salesperson,
            si.pos_profile,
            ppu.warehouse,

            -- Item Quantities
            SUM(IFNULL(qty.tara_200, 0))    AS tara_200,
            SUM(IFNULL(qty.tara_330, 0))    AS tara_330,
            SUM(IFNULL(qty.tara_600, 0))    AS tara_600,
            SUM(IFNULL(qty.total_qty, 0))   AS sale_qty,

            -- Item Amounts
            SUM(IFNULL(qty.tara_200_amount, 0)) AS tara_200_amount,
            SUM(IFNULL(qty.tara_330_amount, 0)) AS tara_330_amount,
            SUM(IFNULL(qty.tara_600_amount, 0)) AS tara_600_amount,
            SUM(IFNULL(qty.total_amount, 0)) AS total_sale_amount,

            -- Payments
            SUM(IFNULL(cash.total_cash, 0)) AS cash_sale,
            SUM(IFNULL(card.total_card, 0)) AS card_sale,

            -- Credit Sale (Unpaid/Overdue)
            SUM(CASE
                WHEN si.status IN ('Unpaid', 'Overdue') AND si.outstanding_amount > 0
                THEN si.grand_total ELSE 0
            END) AS credit_sale,

            -- Overpaid
            SUM(CASE
                WHEN si.outstanding_amount < 0
                THEN si.outstanding_amount ELSE 0
            END) AS overpaid,

            -- Online Transfer Collection
            (
                SELECT SUM(ped.allocated_amount)
                FROM `tabPayment Entry` pe
                JOIN `tabPayment Entry Reference` ped ON ped.parent = pe.name
                WHERE pe.docstatus = 1
                  AND pe.mode_of_payment NOT LIKE '%%cash%%'
                  AND DATE(pe.posting_date) = DATE(si.posting_date)
                  AND pe.custom_salesman IN (
                      SELECT st.sales_person
                      FROM `tabSales Team` st
                      WHERE st.parent = si.name
                  )
            ) AS online_transfer,

            -- Cash Collection
            (
                SELECT SUM(ped.allocated_amount)
                FROM `tabPayment Entry` pe
                JOIN `tabPayment Entry Reference` ped ON ped.parent = pe.name
                WHERE pe.docstatus = 1
                  AND pe.mode_of_payment LIKE '%%cash%%'
                  AND DATE(pe.posting_date) = DATE(si.posting_date)
                  AND pe.custom_salesman IN (
                      SELECT st.sales_person
                      FROM `tabSales Team` st
                      WHERE st.parent = si.name
                  )
            ) AS cash_collection,

            ppu.min_order AS _order

        FROM `tabSales Invoice` si

        LEFT JOIN (
            SELECT
                parent AS pos_profile,
                GROUP_CONCAT(DISTINCT custom_user_name ORDER BY custom_order ASC SEPARATOR ', ') AS salespersons,
                MIN(custom_order) AS min_order,
                warehouse
            FROM `tabPOS Profile User`
            LEFT JOIN `tabPOS Profile` pp ON pp.name = `tabPOS Profile User`.parent
            WHERE custom_user_type = 'Salesman'
            GROUP BY parent
        ) ppu ON ppu.pos_profile = si.pos_profile

        LEFT JOIN (
            SELECT
                parent,
                SUM(CASE WHEN item_code = 'TARA Water 200ml Carton 48 pcs' THEN qty ELSE 0 END) AS tara_200,
                SUM(CASE WHEN item_code = 'TARA Water 330 ML Carton 40pcs' THEN qty ELSE 0 END) AS tara_330,
                SUM(CASE WHEN item_code = 'TARA Water 600ML Carton 30pcs' THEN qty ELSE 0 END) AS tara_600,
                SUM(qty) AS total_qty,

                SUM(CASE WHEN item_code = 'TARA Water 200ml Carton 48 pcs' THEN amount ELSE 0 END) AS tara_200_amount,
                SUM(CASE WHEN item_code = 'TARA Water 330 ML Carton 40pcs' THEN amount ELSE 0 END) AS tara_330_amount,
                SUM(CASE WHEN item_code = 'TARA Water 600ML Carton 30pcs' THEN amount ELSE 0 END) AS tara_600_amount,
                SUM(amount) AS total_amount
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
          AND IFNULL(si.is_return, 0) = 0
          AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
          {warehouse_condition}

        GROUP BY
            DATE(si.posting_date),
            si.pos_profile,
            ppu.salespersons,
            ppu.warehouse,
            ppu.min_order

        ORDER BY
            ppu.min_order ASC,
            DATE(si.posting_date),
            si.pos_profile
        """,
        filters,
        as_dict=True,
    )

    columns = [
        {"label": "Date", "fieldname": "date", "fieldtype": "Date"},
        {"label": "Salesperson", "fieldname": "salesperson", "fieldtype": "Data"},
        {"label": "Warehouse", "fieldname": "warehouse", "fieldtype": "Data"},
        {"label": "Tara 200", "fieldname": "tara_200", "fieldtype": "Int"},
        {"label": "Tara 330", "fieldname": "tara_330", "fieldtype": "Int"},
        {"label": "Tara 600", "fieldname": "tara_600", "fieldtype": "Int"},
        {"label": "Sale Qty", "fieldname": "sale_qty", "fieldtype": "Int"},
        {
            "label": "Tara 200 Amount",
            "fieldname": "tara_200_amount",
            "fieldtype": "Currency",
        },
        {
            "label": "Tara 330 Amount",
            "fieldname": "tara_330_amount",
            "fieldtype": "Currency",
        },
        {
            "label": "Tara 600 Amount",
            "fieldname": "tara_600_amount",
            "fieldtype": "Currency",
        },
        {
            "label": "Total Sale Amount",
            "fieldname": "total_sale_amount",
            "fieldtype": "Currency",
        },
        {
            "label": "Cash Sale (Cash Mode)",
            "fieldname": "cash_sale",
            "fieldtype": "Currency",
        },
        {"label": "Card Sale", "fieldname": "card_sale", "fieldtype": "Currency"},
        {"label": "Credit Sale", "fieldname": "credit_sale", "fieldtype": "Currency"},
        {
            "label": "Online Transfer",
            "fieldname": "online_transfer",
            "fieldtype": "Currency",
        },
        {
            "label": "Cash Collection",
            "fieldname": "cash_collection",
            "fieldtype": "Currency",
        },
    ]

    return columns, data
