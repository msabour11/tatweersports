# Copyright (c) 2025, Mohamed AbdElsabour and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
    if not filters:
        filters = {}

    # Base conditions: only submitted, non-return invoices
    conditions = "si.docstatus = 1 AND IFNULL(si.is_return, 0) = 0"
    if filters.get("from_date") and filters.get("to_date"):
        conditions += " AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s"
    if filters.get("warehouse"):
        conditions += " AND ppu.warehouse = %(warehouse)s"

    data = frappe.db.sql(
        f"""
        SELECT
            DATE(si.posting_date) AS date,
            ppu.salespersons AS salesperson,
            si.pos_profile,
            ppu.warehouse,

            -- Quantities by Shtine SKU
            SUM(IFNULL(qty.shtine_200, 0))    AS shtine_200,
            SUM(IFNULL(qty.shtine_330, 0))    AS shtine_330,
            SUM(IFNULL(qty.shtine_600, 0))    AS shtine_600,
            SUM(IFNULL(qty.shtine_1500, 0))   AS shtine_1500,
            SUM(IFNULL(qty.total_qty, 0))     AS sale_qty,

            -- Amounts by Shtine SKU
            SUM(IFNULL(qty.shtine_200_amount, 0))   AS shtine_200_amount,
            SUM(IFNULL(qty.shtine_330_amount, 0))   AS shtine_330_amount,
            SUM(IFNULL(qty.shtine_600_amount, 0))   AS shtine_600_amount,
            SUM(IFNULL(qty.shtine_1500_amount, 0))  AS shtine_1500_amount,
            SUM(IFNULL(qty.total_amount, 0))        AS total_sale_amount,

            -- Payments via SI Payment table
            SUM(IFNULL(cash.total_cash, 0)) AS cash_sale,
            SUM(IFNULL(card.total_card, 0)) AS card_sale,

            -- Credit Sale: Unpaid or Overdue with positive outstanding
            SUM(CASE
                WHEN si.status IN ('Unpaid', 'Overdue') AND si.outstanding_amount > 0
                THEN si.grand_total ELSE 0
            END) AS credit_sale,

            -- Overpaid (negative outstanding)
            SUM(CASE
                WHEN si.outstanding_amount < 0
                THEN ABS(si.outstanding_amount) ELSE 0
            END) AS overpaid,

            -- Online Transfer Collection (non-cash Payment Entries)
            (
                SELECT SUM(ped.allocated_amount)
                FROM `tabPayment Entry` pe
                INNER JOIN `tabPayment Entry Reference` ped ON ped.parent = pe.name
                WHERE pe.docstatus = 1
                  AND LOWER(pe.mode_of_payment) NOT LIKE '%%cash%%'
                  AND DATE(pe.posting_date) = DATE(si.posting_date)
                  AND pe.custom_salesman IN (
                      SELECT st.sales_person FROM `tabSales Team` st WHERE st.parent = si.name
                  )
            ) AS online_transfer,

            -- Cash Collection (cash-mode Payment Entries)
            (
                SELECT SUM(ped.allocated_amount)
                FROM `tabPayment Entry` pe
                INNER JOIN `tabPayment Entry Reference` ped ON ped.parent = pe.name
                WHERE pe.docstatus = 1
                  AND LOWER(pe.mode_of_payment) LIKE '%%cash%%'
                  AND DATE(pe.posting_date) = DATE(si.posting_date)
                  AND pe.custom_salesman IN (
                      SELECT st.sales_person FROM `tabSales Team` st WHERE st.parent = si.name
                  )
            ) AS cash_collection,

            ppu.min_order AS _order  -- Hidden sort key

        FROM `tabSales Invoice` si

        -- Fetch salesperson(s) and warehouse per POS Profile
        LEFT JOIN (
            SELECT
                parent AS pos_profile,
                GROUP_CONCAT(DISTINCT custom_user_name ORDER BY custom_order ASC SEPARATOR ', ') AS salespersons,
                MIN(custom_order) AS min_order,
                warehouse
            FROM `tabPOS Profile User` ppu1
            LEFT JOIN `tabPOS Profile` pp ON pp.name = ppu1.parent
            WHERE custom_user_type = 'Salesman'
            GROUP BY parent, warehouse
        ) ppu ON ppu.pos_profile = si.pos_profile

        -- Aggregate item-wise quantities & amounts (Shtine SKUs only)
        LEFT JOIN (
            SELECT
                parent,
                SUM(CASE WHEN item_code = 'Shtine Water 200ml Carton 48 Pcs' THEN qty ELSE 0 END) AS shtine_200,
                SUM(CASE WHEN item_code = 'Shtine Water 330ml Carton 40 Pcs' THEN qty ELSE 0 END) AS shtine_330,
                SUM(CASE WHEN item_code = 'Shtine Water 600ml Carton 30 Pcs' THEN qty ELSE 0 END) AS shtine_600,
                SUM(CASE WHEN item_code = 'Shtine Water 1500ml Carton 12 Pcs' THEN qty ELSE 0 END) AS shtine_1500,
                SUM(qty) AS total_qty,

                SUM(CASE WHEN item_code = 'Shtine Water 200ml Carton 48 Pcs' THEN amount ELSE 0 END) AS shtine_200_amount,
                SUM(CASE WHEN item_code = 'Shtine Water 330ml Carton 40 Pcs' THEN amount ELSE 0 END) AS shtine_330_amount,
                SUM(CASE WHEN item_code = 'Shtine Water 600ml Carton 30 Pcs' THEN amount ELSE 0 END) AS shtine_600_amount,
                SUM(CASE WHEN item_code = 'Shtine Water 1500ml Carton 12 Pcs' THEN amount ELSE 0 END) AS shtine_1500_amount,
                SUM(amount) AS total_amount
            FROM `tabSales Invoice Item`
            GROUP BY parent
        ) qty ON qty.parent = si.name

        -- Cash payments (from SI Payment child table)
        LEFT JOIN (
            SELECT parent, SUM(amount) AS total_cash
            FROM `tabSales Invoice Payment`
            WHERE LOWER(mode_of_payment) LIKE '%%cash%%'
            GROUP BY parent
        ) cash ON cash.parent = si.name

        -- Card/other payments (non-cash)
        LEFT JOIN (
            SELECT parent, SUM(amount) AS total_card
            FROM `tabSales Invoice Payment`
            WHERE LOWER(mode_of_payment) NOT LIKE '%%cash%%'
            GROUP BY parent
        ) card ON card.parent = si.name

        WHERE {conditions}

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

    # Compute derived fields in Python (clean & safe)
    for row in data:
        row["total_collection"] = (row.get("online_transfer") or 0) + (
            row.get("cash_collection") or 0
        )

    # Column definitions — clean, intuitive labels
    columns = [
        {"label": "Date", "fieldname": "date", "fieldtype": "Date", "width": 90},
        {
            "label": "Salesperson",
            "fieldname": "salesperson",
            "fieldtype": "Data",
            "width": 150,
        },
        {
            "label": "Warehouse",
            "fieldname": "warehouse",
            "fieldtype": "Link",
            "options": "Warehouse",
            "width": 120,
        },
        {
            "label": "Shtine 200ml (Cartons)",
            "fieldname": "shtine_200",
            "fieldtype": "Int",
            "width": 80,
        },
        {
            "label": "Amt (200ml)",
            "fieldname": "shtine_200_amount",
            "fieldtype": "Currency",
            "width": 100,
        },
        {
            "label": "Shtine 330ml (Cartons)",
            "fieldname": "shtine_330",
            "fieldtype": "Int",
            "width": 80,
        },
        {
            "label": "Amt (330ml)",
            "fieldname": "shtine_330_amount",
            "fieldtype": "Currency",
            "width": 100,
        },
        {
            "label": "Shtine 600ml (Cartons)",
            "fieldname": "shtine_600",
            "fieldtype": "Int",
            "width": 80,
        },
        {
            "label": "Amt (600ml)",
            "fieldname": "shtine_600_amount",
            "fieldtype": "Currency",
            "width": 100,
        },
        {
            "label": "Shtine 1500ml (Cartons)",
            "fieldname": "shtine_1500",
            "fieldtype": "Int",
            "width": 90,
        },
        {
            "label": "Amt (1500ml)",
            "fieldname": "shtine_1500_amount",
            "fieldtype": "Currency",
            "width": 100,
        },
        {
            "label": "Total Qty (Cartons)",
            "fieldname": "sale_qty",
            "fieldtype": "Int",
            "width": 80,
        },
        {
            "label": "Total Sale Amount",
            "fieldname": "total_sale_amount",
            "fieldtype": "Currency",
            "width": 120,
        },
        {
            "label": "Cash Sale (POS)",
            "fieldname": "cash_sale",
            "fieldtype": "Currency",
            "width": 100,
        },
        {
            "label": "Card Sale (POS)",
            "fieldname": "card_sale",
            "fieldtype": "Currency",
            "width": 100,
        },
        {
            "label": "Credit Sale",
            "fieldname": "credit_sale",
            "fieldtype": "Currency",
            "width": 100,
        },
        {
            "label": "Overpaid",
            "fieldname": "overpaid",
            "fieldtype": "Currency",
            "width": 90,
        },
        {
            "label": "Online Transfer",
            "fieldname": "online_transfer",
            "fieldtype": "Currency",
            "width": 110,
        },
        {
            "label": "Cash Collection",
            "fieldname": "cash_collection",
            "fieldtype": "Currency",
            "width": 110,
        },
        {
            "label": "Total Collection",
            "fieldname": "total_collection",
            "fieldtype": "Currency",
            "width": 120,
        },
    ]

    return columns, data
