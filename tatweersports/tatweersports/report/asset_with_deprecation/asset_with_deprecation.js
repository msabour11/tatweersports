// Copyright (c) 2026, Mohamed AbdElsabour and contributors
// For license information, please see license.txt

frappe.query_reports["Asset with Deprecation"] = {
  filters: [
    {
      fieldname: "asset_name",
      label: "Asset Name",
      fieldtype: "Link",
      options: "Asset",
      width: 200,
    },
    {
      fieldname: "company",
      label: "Company",
      fieldtype: "Link",
      options: "Company",
      reqd: 0,
    },
    {
      fieldname: "depreciation_upto_date",
      label: "Depreciation Up To Date",
      fieldtype: "Date",
    },
    {
      fieldname: "item_code",
      label: "Item Code",
      fieldtype: "Link",
      options: "Item",
    },
    {
      fieldname: "asset_category",
      label: "Asset Category",
      fieldtype: "Link",
      options: "Asset Category",
    },
    {
      fieldname: "location",
      label: "Location",
      fieldtype: "Link",
      options: "Location",
    },
    {
      fieldname: "is_existing_asset",
      label: "Is Existing Asset?",
      fieldtype: "Select",
      options: " \n1\n0",
      description: "1 = Yes, 0 = No",
    },
  ],
};
