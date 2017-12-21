# Copyright (c) 2013, ridhosribumi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, getdate

def execute(filters=None):
	columns = get_columns()
#	sl_entries = get_entries(filters)
	data = []

	conditions = get_conditions(filters)
	sl_entries = frappe.db.sql("""select `name`, `status`, transaction_date from `tabInquiry` iq where iq.docstatus = '1' %s""" % conditions, as_dict=1)
	for cl in sl_entries:
		count_quote = frappe.db.sql("""select count(distinct(qo.`name`)) from `tabQuotation Item` qi inner join `tabQuotation` qo on qi.parent = qo.`name` where qi.inquiry = %s and qo.docstatus != '2'""",cl.name)[0][0]
		count_so = frappe.db.sql("""select count(distinct(so.`name`)) from `tabSales Order Item` soi inner join `tabSales Order` so on soi.parent = so.`name` where soi.inquiry = %s and so.docstatus != '2'""",cl.name)[0][0]
		count_dn = frappe.db.sql("""select count(distinct(dn.`name`)) from `tabDelivery Note Item` dni inner join `tabDelivery Note` dn on dni.parent = dn.`name` where dni.inquiry = %s and dn.docstatus != '2'""",cl.name)[0][0]
		count_si = frappe.db.sql("""select count(distinct(si.`name`)) from `tabSales Invoice Item` sii inner join `tabSales Invoice` si on sii.parent = si.`name` where sii.inquiry = %s and si.docstatus != '2'""",cl.name)[0][0]
		if count_quote == 0:
			count = 1
		elif count_quote >= count_so and count_quote >= count_dn and count_quote >= count_si:
			count = count_quote
		elif count_so >= count_quote and count_so >= count_dn and count_so >= count_si:
			count = count_so
		elif count_dn >= count_quote and count_dn >= count_so and count_dn >= count_si:
			count = count_dn
		for q in range(0,count):
			i = flt(q)+1
			if flt(q) < flt(count_quote):
				quote = frappe.db.sql("""select distinct(qo.`name`) from `tabQuotation Item` qi inner join `tabQuotation` qo on qi.parent = qo.`name` where qi.inquiry = %s and qo.docstatus != '2' order by qo.`name` asc limit %s,%s""",(cl.name, q, i))[0][0]
				quote_date = frappe.db.get_value("Quotation", {"name": quote}, "transaction_date")
				quote_status = frappe.db.get_value("Quotation", {"name": quote}, "so_status")
			else:
				quote = ""
				quote_date = ""
				quote_status = ""
			if flt(q) < flt(count_so):
				so = frappe.db.sql("""select distinct(so.`name`) from `tabSales Order Item` soi inner join `tabSales Order` so on soi.parent = so.`name` where soi.inquiry = %s and so.docstatus != '2' order by so.`name` asc limit %s,%s""",(cl.name, q, i))[0][0]
				so_date = frappe.db.get_value("Sales Order", {"name": so}, "transaction_date")
				so_status = frappe.db.get_value("Sales Order", {"name": so}, "status")
			else:
				so = ""
				so_date = ""
				so_status = ""
			if flt(q) < flt(count_dn):
				dn = frappe.db.sql("""select distinct(dn.`name`) from `tabDelivery Note Item` dni inner join `tabDelivery Note` dn on dni.parent = dn.`name` where dni.inquiry = %s and dn.docstatus != '2' order by dn.`name` asc limit %s,%s""",(cl.name, q, i))[0][0]
				dn_date = frappe.db.get_value("Delivery Note", {"name": dn}, "posting_date")
				dn_status = frappe.db.get_value("Delivery Note", {"name": dn}, "status")
			else:
				dn = ""
				dn_date = ""
				dn_status = ""
			if flt(q) < flt(count_si):
				si = frappe.db.sql("""select distinct(si.`name`) from `tabSales Invoice Item` sii inner join `tabSales Invoice` si on sii.parent = si.`name` where sii.inquiry = %s and si.docstatus != '2' order by si.`name` asc limit %s,%s""",(cl.name, q, i))[0][0]
				si_date = frappe.db.get_value("Sales Invoice", {"name": si}, "posting_date")
				si_status = frappe.db.get_value("Sales Invoice", {"name": si}, "status")
			else:
				si = ""
				si_date = ""
				si_status = ""
			if flt(q) == 0:
				data.append([cl.name, cl.transaction_date, cl.status, quote, quote_date, quote_status, so, so_date, so_status, dn, dn_date, dn_status, si, si_date, si_status])
			else:
				data.append(['', '', '', quote, quote_date, quote_status, so, so_date, so_status, dn, dn_date, dn_status, si,  si_date, si_status])

	return columns, data

def get_columns():
	"""return columns"""

	columns = [
		_("Inquiry")+":Link/Inquiry:110",
		_("Inquiry Date")+":Date:100",
		_("Status Inquiry")+":Data:100",
		_("Quotation")+":Link/Quotation:110",
		_("Quotation Date")+":Date:100",
		_("Status Quotation")+":Data:110",
		_("Sales Order")+":Link/Sales Order:110",
		_("Sales Order Date")+":Date:110",
		_("Status Sales Order")+":Data:120",
		_("Delivery Note")+":Link/Delivery Note:110",
		_("Delivery Note Date")+":Date:110",
		_("Status Delivery Note")+":Data:110",
		_("Sales Invoice")+":Link/Sales Invoice:110",
		_("Sales Invoice Date")+":Date:120",
		_("Status Sales Invoice")+":Data:120",
	]

	return columns

def get_conditions(filters):
	conditions = ""
	if filters.get("company"):
		conditions += " and iq.company >= '%s'" % frappe.db.escape(filters["company"])
	if filters.get("from_date"):
		conditions += " and iq.transaction_date >= '%s'" % frappe.db.escape(filters["from_date"])
	if filters.get("to_date"):
		conditions += " and iq.transaction_date <= '%s'" % frappe.db.escape(filters["to_date"])

	return conditions

#def get_entries(filters):
#	conditions = get_conditions(filters)
#	aaa = ""
#	return aaa
