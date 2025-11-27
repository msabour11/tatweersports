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
        {
            "label": "Posting Date",
            "fieldname": "posting_date",
            "fieldtype": "Date",
            "width": 120,
        },
        {
            "label": "Customer",
            "fieldname": "customer",
            "fieldtype": "Link",
            "options": "Customer",
            "width": 200,
        },
        {
            "label": "Sales Person",
            "fieldname": "sales_person",
            "fieldtype": "Link",
            "options": "Sales Person",
            "width": 160,
        },
        {
            "label": "Invoice No",
            "fieldname": "invoice_no",
            "fieldtype": "Link",
            "options": "Sales Invoice",
            "width": 180,
        },
        {
            "label": "Invoiced Amount",
            "fieldname": "invoiced_amount",
            "fieldtype": "Currency",
            "width": 120,
        },
        {
            "label": "Paid Amount",
            "fieldname": "paid_amount",
            "fieldtype": "Currency",
            "width": 120,
        },
        {
            "label": "Outstanding Amount",
            "fieldname": "outstanding_amount",
            "fieldtype": "Currency",
            "width": 120,
        },
        {
            "label": "Credit Amount",
            "fieldname": "credit_amount",
            "fieldtype": "Currency",
            "width": 120,
        },
        {
            "label": "Net Outstanding",
            "fieldname": "net_outstanding",
            "fieldtype": "Currency",
            "width": 140,
        },
    ]


def get_data(filters):
    conditions = get_conditions(filters)

    query = f"""
        SELECT
            s.posting_date,
            s.customer,
            s.sales_person,
            s.name AS invoice_no,
            s.grand_total AS invoiced_amount,
            s.outstanding_amount,
            (s.grand_total - s.outstanding_amount) AS paid_amount,
            CASE WHEN s.seq = 1 THEN COALESCE(s.credit_amount, 0) ELSE 0 END AS credit_amount,
            (s.outstanding_amount - CASE WHEN s.seq = 1 THEN COALESCE(s.credit_amount, 0) ELSE 0 END) AS net_outstanding
        FROM (
            SELECT
                si.*,
                gle.credit_amount,
                ROW_NUMBER() OVER (PARTITION BY si.customer ORDER BY si.posting_date DESC) AS seq
            FROM `tabSales Invoice` si
            LEFT JOIN (
                SELECT
                    party,
                    SUM(credit) AS credit_amount
                FROM `tabGL Entry`
                WHERE
                    voucher_type = 'Journal Entry'
                    AND voucher_subtype = 'Journal Entry'
                    AND is_cancelled = 0
                    AND credit > 0
                GROUP BY party
            ) gle ON gle.party = si.customer
        ) s
        WHERE s.docstatus = 1
        AND s.is_return = 0
        AND s.outstanding_amount > 0
        {conditions}
        ORDER BY s.posting_date DESC
    """

    return frappe.db.sql(query, filters, as_dict=True)


def get_conditions(filters):
    conditions = []

    if filters.get("from_date"):
        conditions.append("s.posting_date >= %(from_date)s")

    if filters.get("to_date"):
        conditions.append("s.posting_date <= %(to_date)s")

    if filters.get("customer"):
        conditions.append("s.customer = %(customer)s")

    if filters.get("sales_person"):
        conditions.append("s.sales_person = %(sales_person)s")

    return "AND " + " AND ".join(conditions) if conditions else ""
