# Copyright (c) 2026, Mohamed AbdElsabour and contributors
# For license information, please see license.txt


import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns()
    raw_data = get_raw_data(filters)

    data = []
    from itertools import groupby

    for sales_person, items in groupby(raw_data, key=lambda x: x["sales_person"]):
        items_list = list(items)
        first_item = items_list[0]

        total_customer_debt = sum(
            row.get("outstanding_amount") or 0
            for row in items_list
            if row.get("voucher_no")
        )
        personal_debt = first_item.get("employee_gl_balance") or 0

        # سطر المندوب
        data.append(
            {
                "sales_person": f"<b>{sales_person}</b>",
                "employee": first_item.get("employee"),
                "personal_debt": personal_debt,
                "customer_outstanding": total_customer_debt,
                "total_combined_liability": personal_debt + total_customer_debt,
                "customer": (
                    _("--- Details ---")
                    if first_item.get("voucher_no")
                    else _("No Data for this Period")
                ),
            }
        )

        # أسطر الفواتير
        for row in items_list:
            if row.get("voucher_no"):
                data.append(
                    {
                        "sales_person": "",
                        "customer": row.get("customer"),
                        "voucher_no": row.get("voucher_no"),
                        "posting_date": row.get("posting_date"),
                        "grand_total": row.get("grand_total"),
                        "outstanding_amount": row.get("outstanding_amount"),
                        "indent": 1,
                    }
                )
        data.append({})

    return columns, data


def get_columns():
    return [
        {
            "label": _("Sales Person / Details"),
            "fieldname": "sales_person",
            "fieldtype": "Data",
            "width": 180,
        },
        {
            "label": _("Employee"),
            "fieldname": "employee",
            "fieldtype": "Link",
            "options": "Employee",
            "width": 120,
        },
        {
            "label": _("Personal Debt (A)"),
            "fieldname": "personal_debt",
            "fieldtype": "Currency",
            "width": 130,
        },
        {
            "label": _("Customers Debt (B)"),
            "fieldname": "customer_outstanding",
            "fieldtype": "Currency",
            "width": 130,
        },
        {
            "label": _("Total Liability (A+B)"),
            "fieldname": "total_combined_liability",
            "fieldtype": "Currency",
            "width": 150,
        },
        {
            "label": _("Customer Name"),
            "fieldname": "customer",
            "fieldtype": "Link",
            "options": "Customer",
            "width": 160,
        },
        {
            "label": _("Invoice Number"),
            "fieldname": "voucher_no",
            "fieldtype": "Link",
            "options": "Sales Invoice",
            "width": 130,
        },
        {
            "label": _("Posting Date"),
            "fieldname": "posting_date",
            "fieldtype": "Date",
            "width": 110,
        },
        {
            "label": _("Grand Total"),
            "fieldname": "grand_total",
            "fieldtype": "Currency",
            "width": 120,
        },
        {
            "label": _("Outstanding Amount"),
            "fieldname": "outstanding_amount",
            "fieldtype": "Currency",
            "width": 120,
        },
    ]


def get_raw_data(filters):
    conditions = ""
    if filters.get("sales_person"):
        conditions += " AND sp.name = %(sales_person)s"
    if filters.get("company"):
        conditions += " AND si.company = %(company)s"
    if filters.get("customer"):
        conditions += " AND si.customer = %(customer)s"
    if filters.get("from_date"):
        conditions += " AND si.posting_date >= %(from_date)s"
    if filters.get("to_date"):
        conditions += " AND si.posting_date <= %(to_date)s"

    query = f"""
        SELECT 
            sp.name as sales_person, 
            sp.employee,
            si.customer, 
            si.name as voucher_no, 
            si.posting_date,
            si.grand_total,
            si.outstanding_amount,
            (
                SELECT SUM(gle.debit - gle.credit)
                FROM `tabGL Entry` gle
                WHERE gle.party_type = 'Employee' 
                AND gle.party = sp.employee
                AND gle.is_cancelled = 0
                AND gle.company = si.company
                AND gle.account = '110103002 - عجز مناديب المبيعات - shtn'
            ) as employee_gl_balance
        FROM 
            `tabSales Person` sp
        LEFT JOIN 
            `tabSales Invoice` si ON sp.name = si.sales_person 
            AND si.docstatus = 1 
            AND si.outstanding_amount > 0
        WHERE 1=1 {conditions}
        ORDER BY sp.name, si.posting_date DESC
    """
    return frappe.db.sql(query, filters, as_dict=True)
