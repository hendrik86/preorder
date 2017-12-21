# Copyright (c) 2013, ridhosribumi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, getdate

def execute(filters=None):
	columns = get_columns()
	data = []

	conditions = get_conditions(filters)
	sl_entries = frappe.db.sql("""select so.`name`, so.transaction_date, so.`status` as status_so from `tabSales Order` so where so.docstatus = '1' %s""" % conditions, as_dict=1)
	for cl in sl_entries:
		count_1 = frappe.db.sql("""select count(distinct(si.`name`)) from `tabSales Invoice` si inner join `tabSales Invoice Item` sii on si.`name` = sii.parent where si.docstatus != '2' and sii.sales_order = %s and si.type_of_invoice = 'Full Payment'""", cl.name)[0][0]
		count_2 = frappe.db.sql("""select count(distinct(si.`name`)) from `tabSales Invoice Item` sii inner join `tabSales Invoice` si on si.`name` = sii.parent where si.docstatus != '2' and si.sales_order = %s and si.type_of_invoice = 'Down Payment'""", cl.name)[0][0]
		count_3 = frappe.db.sql("""select count(distinct(si.`name`)) from `tabSales Invoice` si inner join `tabSales Invoice Item` sii on si.`name` = sii.parent where si.docstatus != '2' and sii.sales_order = %s and si.type_of_invoice = 'Non Project Payment'""", cl.name)[0][0]
		count_4 = frappe.db.sql("""select count(distinct(si.`name`)) from `tabDelivery Note` dn inner join `tabDelivery Note Item` dni on dn.`name` = dni.parent inner join `tabSales Invoice` si on dn.`name` = si.delivery_note where si.docstatus != '2' and si.type_of_invoice = 'Progress Payment' and dni.against_sales_order = %s""", cl.name)[0][0]
		count_5 = frappe.db.sql("""select count(distinct(si.`name`)) from `tabSales Invoice Item` sii inner join `tabSales Invoice` si on si.`name` = sii.parent where si.docstatus != '2' and si.sales_order = %s and si.type_of_invoice = 'Termin Payment'""", cl.name)[0][0]
		count_6 = frappe.db.sql("""select count(distinct(si.`name`)) from `tabSales Invoice Item` sii inner join `tabSales Invoice` si on si.`name` = sii.parent where si.docstatus != '2' and sii.sales_order = %s and si.type_of_invoice = 'Retention'""", cl.name)[0][0]
		if count_1 == 0 and count_2 == 0 and count_3 == 0 and count_4 == 0 and count_5 == 0 and count_6 == 0:
			count = 1
		else:
			if count_1 >= count_2 and count_1 >= count_3 and count_1 >= count_4 and count_1 >= count_5 and count_1 >= count_6:
				count = count_1
			elif count_2 >= count_1 and count_2 >= count_3 and count_2 >= count_4 and count_2 >= count_5 and count_2 >= count_6:
				count = count_2
			elif count_3 >= count_1 and count_3 >= count_2 and count_3 >= count_4 and count_3 >= count_5 and count_3 >= count_6:
				count = count_3
			elif count_4 >= count_1 and count_4 >= count_2 and count_4 >= count_3 and count_4 >= count_5 and count_4 >= count_6:
				count = count_4
			elif count_5 >= count_1 and count_5 >= count_2 and count_5 >= count_3 and count_5 >= count_4 and count_5 >= count_6:
				count = count_5
			else:
				count = count_6
		for q in range(0,count):
			i = flt(q)+1
			if q == 0:
				so_date = cl.transaction_date
				so_name = cl.name
				so_status = cl.status_so
			else:
				so_date = ""
				so_name = ""
				so_status = ""
			if flt(q) < flt(count_1):
				si_1 = frappe.db.sql("""select distinct(si.`name`) from `tabSales Invoice` si inner join `tabSales Invoice Item` sii on si.`name` = sii.parent where si.docstatus != '2' and sii.sales_order = %s and si.type_of_invoice = 'Full Payment' order by si.`name` asc limit %s,%s""", (cl.name, q, i))[0][0]
				si_1_status = frappe.db.get_value("Sales Invoice", si_1, "status")
			else:
				si_1 = ""
				si_1_status = ""
			if flt(q) < flt(count_2):
				si_2 = frappe.db.sql("""select distinct(si.`name`) from `tabSales Invoice Item` sii inner join `tabSales Invoice` si on si.`name` = sii.parent where si.docstatus != '2' and si.sales_order = %s and si.type_of_invoice = 'Down Payment' order by si.idx asc limit %s,%s""", (cl.name, q, i))[0][0]
				si_2_status = frappe.db.get_value("Sales Invoice", si_2, "status")
			else:
				si_2 = ""
				si_2_status = ""
			if flt(q) < flt(count_3):
				si_3 = frappe.db.sql("""select distinct(si.`name`) from `tabSales Invoice` si inner join `tabSales Invoice Item` sii on si.`name` = sii.parent where si.docstatus != '2' and sii.sales_order = %s and si.type_of_invoice = 'Non Project Payment' order by si.`name` asc limit %s,%s""", (cl.name, q, i))[0][0]
				si_3_status = frappe.db.get_value("Sales Invoice", si_3, "status")
			else:
				si_3 = ""
				si_3_status = ""
			if flt(q) < flt(count_4):
				si_4 = frappe.db.sql("""select distinct(si.`name`) from `tabDelivery Note` dn inner join `tabDelivery Note Item` dni on dn.`name` = dni.parent inner join `tabSales Invoice` si on dn.`name` = si.delivery_note where si.docstatus != '2' and si.type_of_invoice = 'Progress Payment' and dni.against_sales_order = %s order by si.`name` asc limit %s,%s""", (cl.name, q, i))[0][0]
				si_4_status = frappe.db.get_value("Sales Invoice", si_4, "status")
			else:
				si_4 = ""
				si_4_status = ""
			if flt(q) < flt(count_5):
				si_5 = frappe.db.sql("""select distinct(si.`name`) from `tabSales Invoice Item` sii inner join `tabSales Invoice` si on si.`name` = sii.parent where si.docstatus != '2' and si.sales_order = %s and si.type_of_invoice = 'Termin Payment' order by si.idx asc limit %s,%s""", (cl.name, q, i))[0][0]
				si_5_status = frappe.db.get_value("Sales Invoice", si_5, "status")
			else:
				si_5 = ""
				si_5_status = ""
			if flt(q) < flt(count_6):
				si_6 = frappe.db.sql("""select distinct(si.`name`) from `tabSales Invoice Item` sii inner join `tabSales Invoice` si on si.`name` = sii.parent where si.docstatus != '2' and si.sales_order = %s and si.type_of_invoice = 'Retention' order by si.idx asc limit %s,%s""", (cl.name, q, i))[0][0]
				si_6_status = frappe.db.get_value("Sales Invoice", si_6, "status")
			else:
				si_6 = ""
				si_6_status = ""
			data.append([so_date, so_name, so_status, si_1, si_1_status, si_2, si_2_status, si_3, si_3_status, si_4, si_4_status, si_5, si_5_status, si_6, si_6_status])

	return columns, data

def get_columns():
	"""return columns"""

	columns = [
		_("SO Date")+":Date:90",
		_("Sales Order")+":Link/Sales Order:110",
		_("Status")+":Data:130",
		_("Full Payment")+":Link/Sales Invoice:110",
		_("Status 1")+":Data:90",
		_("Down Payment")+":Link/Sales Invoice:110",
		_("Status 2")+":Data:90",
		_("Non Project Payment")+":Link/Sales Invoice:130",
		_("Status 3")+":Data:90",
		_("Progress Payment")+":Link/Sales Invoice:110",
		_("Status 4")+":Data:90",
		_("Termin Payment")+":Link/Sales Invoice:110",
		_("Status 5")+":Data:90",
		_("Retention")+":Link/Sales Invoice:110",
		_("Status 6")+":Data:90",
	]

	return columns

def get_conditions(filters):
	conditions = ""
	if filters.get("from_date"):
		conditions += " and so.transaction_date >= '%s'" % frappe.db.escape(filters["from_date"])
	if filters.get("to_date"):
		conditions += " and so.transaction_date <= '%s'" % frappe.db.escape(filters["to_date"])
	if filters.get("need_down_payment") == 1:
		conditions += " and so.need_down_payment = '1'"

	return conditions
