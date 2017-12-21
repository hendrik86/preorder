// Copyright (c) 2016, ridhosribumi and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Sales Order Report"] = {
	"filters": [
		{
			"fieldname":"warehouse",
			"label": __("Warehouse"),
			"fieldtype": "Link",
			"options": "Warehouse",
			"reqd": 1,
			"default": "VPI WAREHOUSE - VPI"
		},
	]
}
