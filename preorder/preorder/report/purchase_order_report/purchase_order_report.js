// Copyright (c) 2016, ridhosribumi and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Purchase Order Report"] = {
	"filters": [
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"reqd": 1,
			"default": frappe.defaults.get_user_default("Company")
		},
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"width": "80",
			"default": frappe.datetime.month_start(frappe.datetime.get_today()),
			"reqd": 1
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"width": "80",
			"default": frappe.datetime.get_today(),
			"reqd": 1
		},
	],
	"formatter":function (row, cell, value, columnDef, dataContext, default_formatter) {
		value = default_formatter(row, cell, value, columnDef, dataContext);
		if (columnDef.id != "Purchase Order" && columnDef.id != "Supplier Name" && dataContext["Item Status"] == "Completed") {
			value = "<span style='color:#DF01D7 !important'>" + value + "</span>";
		}
		return value;
	}
}
