// Copyright (c) 2016, ridhosribumi and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Laporan Pembalik HPP"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"width": "80",
			"default": frappe.datetime.get_today(),
			"reqd": 1
		},
		/*
		{
			"fieldname": "month",
			"label": __("Month"),
			"width": "80",
			"fieldtype": "Select",
			"options": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
			"reqd": 1
		},
		{
			"fieldname": "fiscal_year",
			"label": __("Fiscal Year"),
			"fieldtype": "Link",
			"options": "Fiscal Year",
			"default": frappe.defaults.get_user_default("fiscal_year"),
			"reqd": 1,
		},
		*/
	]
}
