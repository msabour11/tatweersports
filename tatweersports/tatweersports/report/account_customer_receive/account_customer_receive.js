// Copyright (c) 2025, Mohamed AbdElsabour and contributors
// For license information, please see license.txt

frappe.query_reports["Account Customer Receive"] = {
  filters: [
    {
      fieldname: "from_date",
      label: __("From Date"),
      fieldtype: "Date",

      width: "80px",
    },
    {
      fieldname: "to_date",
      label: __("To Date"),
      fieldtype: "Date",
      // "reqd": 1,
      width: "80px",
    },
    {
      fieldname: "customer",
      label: __("Customer"),
      fieldtype: "Link",
      options: "Customer",
      width: "80px",
    },
    {
      fieldname: "sales_person",
      label: __("Sales Person"),
      fieldtype: "Link",
      options: "Sales Person",
      width: "80px",
    },
  ],
};
