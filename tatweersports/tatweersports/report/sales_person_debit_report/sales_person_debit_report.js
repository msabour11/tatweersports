// Copyright (c) 2026, Mohamed AbdElsabour and contributors
// For license information, please see license.txt

frappe.query_reports["Sales Person Debit Report"] = {
  filters: [
    {
      fieldname: "company",
      label: __("Company"),
      fieldtype: "Link",
      options: "Company",
      default: frappe.defaults.get_user_default("company"),
      reqd: 1,
    },
    {
      fieldname: "from_date",
      label: __("From Date"),
      fieldtype: "Date",
      default: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
    },
    {
      fieldname: "to_date",
      label: __("To Date"),
      fieldtype: "Date",
      default: frappe.datetime.get_today(),
    },
    {
      fieldname: "sales_person",
      label: __("Sales Person"),
      fieldtype: "Link",
      options: "Sales Person",
    },
    {
      fieldname: "customer",
      label: __("Customer"),
      fieldtype: "Link",
      options: "Customer",
    },
  ],
  formatter: function (value, row, column, data, default_formatter) {
    value = default_formatter(value, row, column, data);

    // تلوين إجمالي الذمة باللون الأحمر العريض
    if (
      column.fieldname === "total_combined_liability" &&
      data.total_combined_liability > 0
    ) {
      value = `<span style="color: red; font-weight: bold;">${value}</span>`;
    }

    // تمييز أسطر المندوبين
    if (data.sales_person && !data.voucher_no) {
      value = `<b>${value}</b>`;
    }

    return value;
  },
};
