# Copyright (c) 2025, Mohamed AbdElsabour and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters or {})
    return columns, data


def get_columns():
    return [
        {
            "label": _("Posting Date"),
            "fieldname": "posting_date",
            "fieldtype": "Date",
            "width": 120,
        },
        {
            "label": _("Customer"),
            "fieldname": "customer",
            "fieldtype": "Link",
            "options": "Customer",
            "width": 200,
        },
        {
            "label": _("Sales Person"),
            "fieldname": "sales_person",
            "fieldtype": "Link",
            "options": "Sales Person",
            "width": 160,
        },
        {
            "label": _("Invoice No"),
            "fieldname": "invoice_no",
            "fieldtype": "Link",
            "options": "Sales Invoice",
            "width": 180,
        },
        {
            "label": _("Invoiced Amount"),
            "fieldname": "invoiced_amount",
            "fieldtype": "Currency",
            "width": 120,
        },
        {
            "label": _("Paid Amount"),
            "fieldname": "paid_amount",
            "fieldtype": "Currency",
            "width": 120,
        },
        {
            "label": _("Outstanding Amount"),
            "fieldname": "outstanding_amount",
            "fieldtype": "Currency",
            "width": 130,
        },
        {
            "label": _("Credit Amount"),
            "fieldname": "credit_amount",
            "fieldtype": "Currency",
            "width": 120,
        },
        {
            "label": _("Net Outstanding"),
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
            s.invoice_no,
            s.invoiced_amount,
            s.paid_amount,
            s.outstanding_amount,

            CASE
                WHEN s.rn = 1 THEN COALESCE(s.credit_amount, 0)
                ELSE 0
            END AS credit_amount,

            s.outstanding_amount -
            CASE
                WHEN s.rn = 1 THEN COALESCE(s.credit_amount, 0)
                ELSE 0
            END AS net_outstanding

        FROM (
            SELECT
                si.posting_date,
                si.customer,
                si.sales_person,
                si.name AS invoice_no,
                si.grand_total AS invoiced_amount,
                (si.grand_total - si.outstanding_amount) AS paid_amount,
                si.outstanding_amount,
                gle.credit_amount,

                ROW_NUMBER() OVER (
                    PARTITION BY si.customer
                    ORDER BY si.posting_date DESC
                ) AS rn

            FROM `tabSales Invoice` si

            LEFT JOIN (
                SELECT
                    party AS customer,
                    SUM(credit_in_account_currency) AS credit_amount
                FROM `tabGL Entry`
                WHERE
                    party_type = 'Customer'
                    AND voucher_type = 'Journal Entry'
                    AND is_cancelled = 0
                    AND credit_in_account_currency > 0
                GROUP BY party
            ) gle ON gle.customer = si.customer

            WHERE
                si.docstatus = 1
                AND si.is_return = 0
                AND si.outstanding_amount > 0
                {conditions}
        ) s

        ORDER BY
            s.customer,
            s.posting_date DESC
    """

    return frappe.db.sql(query, filters, as_dict=True)


def get_conditions(filters):
    conditions = []

    if filters.get("from_date"):
        conditions.append("si.posting_date >= %(from_date)s")

    if filters.get("to_date"):
        conditions.append("si.posting_date <= %(to_date)s")

    if filters.get("customer"):
        conditions.append("si.customer = %(customer)s")

    if filters.get("sales_person"):
        conditions.append("si.sales_person = %(sales_person)s")

    return " AND " + " AND ".join(conditions) if conditions else ""
