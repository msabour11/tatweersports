// Copyright (c) 2025, Mohamed AbdElsabour and contributors
// For license information, please see license.txt

frappe.query_reports["Salesman Wise Sales"] = {
  filters: [
    {
      fieldname: "from_date",
      label: "From Date",
      fieldtype: "Date",
      width: "200px",
      default: frappe.datetime.add_months(frappe.datetime.get_today()),
      reqd: 1,
    },
    {
      fieldname: "to_date",
      label: "To Date",
      fieldtype: "Date",
    },
    {
      fieldname: "set_warehouse",
      label: "Warehouse",
      fieldtype: "Link",
      options: "Warehouse",
      //   default: frappe.defaults.get_user_default("Warehouse"),
      width: "200px",
    },
    // {
    //   fieldname: "salesperson",
    //   label: "salesperson",
    //   fieldtype: "Link",
    //   options: "Sales Person",
    //   // default: frappe.defaults.get_user_default("sales_person"),
    //   width: "200px",
    // },
  ],
};
// frappe.query_reports["Salesman Wise Sales"].onload = function (report) {
//   report.page.set_title(__("Salesman Wise Sales"));
//   report.page.set_secondary_action(
//     __("Download CSV"),
//     function () {
//       report.download_csv();
//     },
//     "octicon octicon-file-directory"
//   );
// };
