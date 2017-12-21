from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Documents"),
			"items": [
				{
					"type": "doctype",
					"name": "Inquiry",
					"description": _("Inquiry")
				},
				{
					"type": "doctype",
					"name": "Request for Supplier Quotation",
					"description": _("Request for Supplier Quotation")
				},
			]
		},
		{
			"label": _("Settings"),
			"items": [
				{
					"type": "doctype",
					"name": "Item Settings",
					"description": _("Item Settings")
				},
			]
		},
		{
			"label": _("Engineering"),
			"items": [
				{
					"type": "doctype",
					"name": "Product Assembly",
					"description": _("Product Assembly")
				},
			]
		},
		{
			"label": _("Report"),
			"items": [
				{
					"type": "report",
					"name": "Account Receivable",
					"doctype": "Sales Invoice",
					"is_query_report": True
				},
				{
					"type": "report",
					"name": "Buying Progress Report",
					"doctype": "Inquiry",
					"is_query_report": True
				},
				{
					"type": "report",
					"name": "Gross Margin",
					"doctype": "Inquiry",
					"is_query_report": True
				},
#				{
#					"type": "report",
#					"name": "Inquiry Collection",
#					"doctype": "Inquiry",
#					"is_query_report": True
#				},
				{
					"type": "report",
					"name": "Laporan Pembalik HPP",
					"doctype": "Delivery Note",
					"is_query_report": True
				},
				{
					"type": "report",
					"name": "Invoice Check",
					"doctype": "Sales Order",
					"is_query_report": True
				},
				{
					"type": "report",
					"name": "Net Profit",
					"doctype": "Inquiry",
					"is_query_report": True
				},
				{
					"type": "report",
					"name": "Purchase Order Report",
					"doctype": "Purchase Order",
					"is_query_report": True
				},
				{
					"type": "report",
					"name": "Sales Order Report",
					"doctype": "Sales Order",
					"is_query_report": True
				},
				{
					"type": "report",
					"name": "Selling Progress Report",
					"doctype": "Inquiry",
					"is_query_report": True
				},
				{
					"type": "report",
					"name": "Stock Available",
					"doctype": "Item",
					"is_query_report": True
				},
			]
		},
	]
