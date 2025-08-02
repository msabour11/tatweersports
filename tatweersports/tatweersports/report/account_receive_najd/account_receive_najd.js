// Copyright (c) 2025, Mohamed AbdElsabour and contributors
// For license information, please see license.txt

frappe.query_reports["Account Receive Najd"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			// "default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			// "reqd": 1,
			"width": "80px"
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",	
			// "default": frappe.datetime.get_today(),
			// "reqd": 1,
			"width": "80px"
		},
		{
			"fieldname": "customer",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options": "Customer",
			"width": "80px"
		},
		{
			"fieldname": "sales_person",
			"label": __("Sales Person"),
			"fieldtype": "Link",
			"options": "Sales Person",
			// "default": frappe.defaults.get_user_default("sales_person"),
			"width": "80px"
		},
		


	]
};
