// Copyright (c) 2025, Mohamed AbdElsabour and contributors
// For license information, please see license.txt

frappe.query_reports["Account Customer Receive"] = {
  onload: function (report) {
    // Add print-specific CSS
    const style = document.createElement("style");
    style.innerHTML = `
            @media print {
                .dt-cell--col-6 { /* Column index 6 is Outstanding Amount (0-indexed) */
                    display: none !important;
                }
            }
        `;
    document.head.appendChild(style);
  },
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
