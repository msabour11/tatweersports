# Copyright (c) 2026, Mohamed AbdElsabour and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
    if not filters:
        filters = {}

    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {
            "label": "Asset Name",
            "fieldname": "asset_name",
            "fieldtype": "Link",
            "options": "Asset",
            "width": 200,
        },
        {
            "label": "Company",
            "fieldname": "company",
            "fieldtype": "Link",
            "options": "Company",
            "width": 160,
        },
        {
            "label": "Item Code",
            "fieldname": "item_code",
            "fieldtype": "Link",
            "options": "Item",
            "width": 150,
        },
        {
            "label": "Asset Category",
            "fieldname": "asset_category",
            "fieldtype": "Link",
            "options": "Asset Category",
            "width": 150,
        },
        {
            "label": "Location",
            "fieldname": "location",
            "fieldtype": "Link",
            "options": "Location",
            "width": 150,
        },
        {
            "label": "Is Existing Asset?",
            "fieldname": "is_existing_asset",
            "fieldtype": "Data",
            "width": 130,
        },
        {
            "label": "Purchase Amount",
            "fieldname": "purchase_amount",
            "fieldtype": "Currency",
            "width": 140,
        },
        {
            "label": "Total Depreciation Booked",
            "fieldname": "total_depreciation",
            "fieldtype": "Currency",
            "width": 160,
        },
        {
            "label": "Purchase Date",
            "fieldname": "purchase_date",
            "fieldtype": "Date",
            "width": 120,
        },
        {
            "label": "Available for Use Date",
            "fieldname": "available_for_use_date",
            "fieldtype": "Date",
            "width": 160,
        },
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 130},
    ]


def get_data(filters):
    conditions = "1=1"
    params = {}

    if filters.get("company"):
        conditions += " AND a.company = %(company)s"
        params["company"] = filters["company"]

    if filters.get("asset_name"):
        conditions += " AND a.name = %(asset_name)s"
        params["asset_name"] = filters["asset_name"]

    if filters.get("asset_category"):
        conditions += " AND a.asset_category = %(asset_category)s"
        params["asset_category"] = filters["asset_category"]

    if filters.get("location"):
        conditions += " AND a.location = %(location)s"
        params["location"] = filters["location"]

    if filters.get("item_code"):
        conditions += " AND a.item_code = %(item_code)s"
        params["item_code"] = filters["item_code"]

    if filters.get("is_existing_asset") and filters["is_existing_asset"] in ("0", "1"):
        conditions += " AND a.is_existing_asset = %(is_existing_asset)s"
        params["is_existing_asset"] = int(filters["is_existing_asset"])

    # depreciation cutoff date
    dep_date_cond = ""
    if filters.get("depreciation_upto_date"):
        dep_date_cond = " AND gle.posting_date <= %(depreciation_upto_date)s"
        params["depreciation_upto_date"] = filters["depreciation_upto_date"]

    sql = f"""
        SELECT
            a.name AS asset_name,
            a.company,
            a.item_code,
            a.asset_category,
            a.location,
            IF(a.is_existing_asset = 1, 'Yes', 'No') AS is_existing_asset,
            a.gross_purchase_amount AS purchase_amount,
            (
                SELECT COALESCE(SUM(gle.credit - gle.debit), 0)
                FROM `tabGL Entry` gle
                LEFT JOIN `tabAccount` acc ON acc.name = gle.account
                WHERE gle.company = a.company
                  AND gle.voucher_type = 'Journal Entry'
                  AND gle.is_cancelled = 0
                  -- correctly linked to asset
                  AND (
                        (gle.against_voucher_type = 'Asset' AND gle.against_voucher = a.name)
                  )
                  -- only accumulated depreciation accounts
                  AND (
                        acc.account_type = 'Accumulated Depreciation'
                        OR acc.account_name LIKE '%%Accumulated Depreciation%%'
                        OR gle.account LIKE '%%Accumulated Depreciation%%'
                  )
                  {dep_date_cond}
            ) AS total_depreciation,
            a.purchase_date,
            a.available_for_use_date,
            a.status
        FROM `tabAsset` a
        WHERE {conditions}
        ORDER BY a.purchase_date DESC
    """

    return frappe.db.sql(sql, params, as_dict=True)
