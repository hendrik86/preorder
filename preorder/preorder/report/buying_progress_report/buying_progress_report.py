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
	sl_entries = frappe.db.sql("""select `name`, transaction_date, `status` from `tabPurchase Order` po where po.docstatus != '2' %s""" % conditions, as_dict=1)
	for cl in sl_entries:
		count_so = frappe.db.sql("""select count(distinct(poi.sales_order)) from `tabPurchase Order Item` poi inner join `tabPurchase Order` po on poi.parent = po.`name` where po.`name` = %s""",cl.name)[0][0]
		count_pr = frappe.db.sql("""select count(distinct(pr.`name`)) from `tabPurchase Receipt Item` pri inner join `tabPurchase Receipt` pr on pri.parent = pr.`name` where pri.purchase_order = %s and pr.docstatus != '2'""",cl.name)[0][0]
		count_pi = frappe.db.sql("""select count(distinct(pi.`name`)) from `tabPurchase Invoice Item` pii inner join `tabPurchase Invoice` pi on pii.parent = pi.`name` where pii.purchase_order = %s and pi.docstatus != '2'""",cl.name)[0][0]
		if count_so == 0 and count_pr == 0 and count_pi == 0:
			count = 1
		elif count_so >= count_pr and count_so >= count_pi:
			count = count_so
		elif count_pr >= count_so and count_pr >= count_pi:
			count = count_pr
		elif count_pi >= count_so and count_pi >= count_pr:
			count = count_pi
		for q in range(0,count):
			i = flt(q)+1
			if flt(q) < flt(count_so):
				so = frappe.db.sql("""select distinct(poi.sales_order) from `tabPurchase Order Item` poi inner join `tabPurchase Order` po on poi.parent = po.`name` where po.`name` = %s order by poi.sales_order asc limit %s,%s""",(cl.name, q, i))[0][0]
				so_date = frappe.db.get_value("Sales Order", {"name": so}, "transaction_date")
				so_status = frappe.db.get_value("Sales Order", {"name": so}, "status")
			else:
				so = ""
				so_date = ""
				so_status = ""
			if flt(q) < flt(count_pr):
				pr = frappe.db.sql("""select distinct(pr.`name`) from `tabPurchase Receipt Item` pri inner join `tabPurchase Receipt` pr on pri.parent = pr.`name` where pri.purchase_order = %s and pr.docstatus != '2' order by pr.`name` asc limit %s,%s""",(cl.name, q, i))[0][0]
				pr_date = frappe.db.get_value("Purchase Receipt", {"name": pr}, "posting_date")
				pr_status = frappe.db.get_value("Purchase Receipt", {"name": pr}, "status")
			else:
				pr = ""
				pr_date = ""
				pr_status = ""
			if flt(q) < flt(count_pi):
				pi = frappe.db.sql("""select distinct(pi.`name`) from `tabPurchase Invoice Item` pii inner join `tabPurchase Invoice` pi on pii.parent = pi.`name` where pii.purchase_order = %s and pi.docstatus != '2' order by pi.`name` asc limit %s,%s""",(cl.name, q, i))[0][0]
				pi_date = frappe.db.get_value("Purchase Invoice", {"name": pi}, "posting_date")
				pi_status = frappe.db.get_value("Purchase Invoice", {"name": pi}, "status")
			else:
				pi = ""
				pi_date = ""
				pi_status = ""
			if flt(q) == 0:
				data.append([cl.name, cl.transaction_date, cl.status, so, so_date, so_status, pr, pr_date, pr_status, pi, pi_date, pi_status])
			else:
				data.append(['', '', '', so, so_date, so_status, pr, pr_date, pr_status, pi, pi_date, pi_status])

	return columns, data

def get_columns():
	"""return columns"""

	columns = [
		_("Purchase Order")+":Link/Inquiry:110",
		_("Purchase Order Date")+":Date:110",
		_("Purchase Order Status")+":Data:120",
		_("Sales Order")+":Link/Sales Order:110",
		_("Sales Order Date")+":Date:110",
		_("Sales Order Status")+":Data:120",
		_("Purchase Receipt")+":Link/Purchase Receipt:110",
		_("Purchase Receipt Date")+":Date:110",
		_("Purchase Receipt Status")+":Data:120",
		_("Purchase Invoice")+":Link/Purchase Invoice:110",
		_("Purchase Invoice Date")+":Date:110",
		_("Purchase Invoice Status")+":Data:120",
	]

	return columns

def get_conditions(filters):
	conditions = ""
	if filters.get("company"):
		conditions += " and po.company >= '%s'" % frappe.db.escape(filters["company"])
	if filters.get("from_date"):
		conditions += " and po.transaction_date >= '%s'" % frappe.db.escape(filters["from_date"])
	if filters.get("to_date"):
		conditions += " and po.transaction_date <= '%s'" % frappe.db.escape(filters["to_date"])

	return conditions
