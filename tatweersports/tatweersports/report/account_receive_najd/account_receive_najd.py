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
    ]


def get_data(filters):
    conditions = get_conditions(filters)

    query = """
        SELECT posting_date as posting_date,
         customer as customer,
          sales_person as sales_person,
          name as invoice_no,
          grand_total as invoiced_amount,
          outstanding_amount as outstanding_amount,
          (grand_total - outstanding_amount) as paid_amount
        FROM `tabSales Invoice`
        WHERE docstatus = 1 and is_return = 0
		and outstanding_amount > 0
        {conditions}
        ORDER BY posting_date DESC
    """.format(
        conditions=conditions
    )

    return frappe.db.sql(query, filters, as_dict=True)


def get_conditions(filters):
    conditions = []

    if filters.get("from_date"):
        conditions.append("posting_date >= %(from_date)s")

    if filters.get("to_date"):
        conditions.append("posting_date <= %(to_date)s")

    if filters.get("customer"):
        conditions.append("customer = %(customer)s")

    if filters.get("sales_person"):
        conditions.append("sales_person = %(sales_person)s")

    return "AND " + " AND ".join(conditions) if conditions else ""
