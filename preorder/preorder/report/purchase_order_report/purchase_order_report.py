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
	sl_entries = frappe.db.sql("""select `name`, supplier_name, transaction_date, payment, delivery_term, delivery_time, freight from `tabPurchase Order` po where po.docstatus != '2' %s""" % conditions, as_dict=1)
	for cl in sl_entries:
		count = frappe.db.sql("""select count(*) from `tabPurchase Order Item` where parent = %s""", cl.name)[0][0]
		for q in range(0,count):
			i = flt(q)+1
			items = frappe.db.sql("""select `name` from `tabPurchase Order Item` where parent = %s order by idx asc limit %s,%s """, (cl.name, q, i))[0][0]
			det = frappe.db.get_value("Purchase Order Item", items, ["item_code", "description", "qty", "rate", "received_qty", "item_status"], as_dict=1)
			if det.received_qty == 0:
				status_oto = "Not yet Received"
			elif det.received_qty < det.qty:
				status_oto = "Partial Received"
			else:
				status_oto = "Full Received"
			if flt(q) == 0:
				data.append([cl.name, cl.supplier_name, det.item_code, det.description, det.qty, det.rate, cl.transaction_date, cl.payment, cl.delivery_time, cl.delivery_term, cl.freight, status_oto, det.item_status])
			else:
				data.append(['', '', det.item_code, det.description, det.qty, det.rate, '', '', '', '', '', status_oto, det.item_status])

	return columns, data

def get_columns():
	"""return columns"""

	columns = [
		_("Purchase Order")+":Link/Purchase Order:110",
		_("Supplier Name")+"::150",
		_("Item Code")+":Link/Item:150",
		_("Description")+"::150",
		_("Qty")+":Float:60",
		_("Price")+":Currency:110",
		_("PO Date")+":Date:90",
		_("Payment")+"::150",
		_("Delivery Time")+"::150",
		_("Delivery Term")+"::150",
		_("Freight")+"::100",
		_("Status")+"::100",
		_("Item Status")+"::100",
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
