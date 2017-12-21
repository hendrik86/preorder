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
	sl_entries = frappe.db.sql("""select `name`, transaction_date from `tabSales Order` so where so.docstatus = '1' and so.status in ('To Deliver and Bill', 'To Deliver')""", as_dict=1)
	for cl in sl_entries:
		count_so = frappe.db.sql("""select count(*) from `tabSales Order Item` where parent = %s and is_product_assembly = '0'""", cl.name)[0][0]
		count_packed = frappe.db.sql("""select count(*) from `tabQuotation Assembly Item` where parent = %s""", cl.name)[0][0]
		count = count_so + count_packed
		x = 0
		y = 0
		for q in range(0,count):
			i = flt(q)+1
			if count_so > q:
				items = frappe.db.sql("""select `name` from `tabSales Order Item` where parent = %s and is_product_assembly = '0' order by idx asc limit %s,%s """, (cl.name, q, i))[0][0]
				det = frappe.db.get_value("Sales Order Item", items, ["item_code", "description", "qty"], as_dict=1)
				item_code = det.item_code
				item_desc = det.description
				item_qty = det.qty
			else:
				y = flt(y)+1
				assembly_item = frappe.db.sql("""select product_assembly_item from `tabQuotation Assembly Item` where parent = %s order by idx asc limit %s,%s """, (cl.name, x, y))[0][0]
				items = frappe.db.sql("""select item_code from `tabProduct Assembly Item` where `name` = %s""", assembly_item)[0][0]
				item_code = items
				item_desc = frappe.db.get_value("Item", {"name": items}, "description")
				item_qty = frappe.db.sql("""select qty from `tabQuotation Assembly Item` where parent = %s order by idx asc limit %s,%s """, (cl.name, x, y))[0][0]
				x = flt(x)+1
			po = frappe.db.get_value("Purchase Order Item", {"item_code": item_code, "sales_order": cl.name, "docstatus": ["!=", 2]}, "parent")
			po_date = frappe.db.get_value("Purchase Order", po, "transaction_date")
			po_status = frappe.db.get_value("Purchase Order", po, "status")
			check_actual = frappe.db.sql("""select count(*) from `tabStock Ledger Entry` where item_code = %s and warehouse = %s""", (item_code, filters.get("warehouse")))[0][0]
			if flt(check_actual) == 0:
				actual_qty = 0
			else:
				actual_qty = frappe.db.sql("""select qty_after_transaction from `tabStock Ledger Entry` where item_code = %s and warehouse = %s order by `name` desc limit 1""", (item_code, filters.get("warehouse")))[0][0]
			# invoices
#			check_invoice = frappe.db.sql("""select count(*) from `tabSales Invoice` where sales_order = %s and docstatus != '2' and type_of_invoice = 'Down Payment' limit %s,%s""", (cl.name, q, i))[0][0]
#			if check_invoice != 0:
#				invoice = frappe.db.sql("""select `name` from `tabSales Invoice` where sales_order = %s and docstatus != '2' and type_of_invoice = 'Down Payment' limit %s,%s""", (cl.name, q, i))[0][0]
#			else:
#				invoice = ""
			if flt(q) == 0:
				data.append([cl.transaction_date, cl.name, item_code, item_desc, item_qty, po, po_date, po_status, actual_qty])
			else:
				data.append(['', '', item_code, item_desc, item_qty, po, po_date, po_status, actual_qty])

	return columns, data

def get_columns():
	"""return columns"""

	columns = [
		_("SO Date")+":Date:100",
		_("Sales Order")+":Link/Sales Order:110",
		_("Item Code")+":Link/Item:150",
		_("Description")+":Data:150",
		_("Qty")+":Float:70",
		_("Purchase Order")+":Link/Purchase Order:110",
		_("PO Date")+":Date:100",
		_("PO Status")+":Data:100",
		_("Actual Qty")+":Float:70",
	]

	return columns

def get_conditions(filters):
	conditions = ""
	if filters.get("company"):
		conditions += " and warehouse >= '%s'" % frappe.db.escape(filters["company"])

	return conditions
