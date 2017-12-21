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

	sl_entries = frappe.db.sql("""select si.`name`, si.posting_date, si.net_total from `tabSales Invoice` si where si.docstatus = '1' and si.type_of_invoice in ('Retention', 'Non Project Payment', 'Standard') and si.`status` = 'Paid' %s""" % conditions, as_dict=1)
	for cl in sl_entries:
		count_1 = frappe.db.sql("""select count(*) from `tabPayment Entry Reference` where reference_name = %s and docstatus = '1'""", cl.name)[0][0]
		if count_1 == 0:
			count = 1
		else:
			count = count_1
		for q in range(0,count):
			i = flt(q)+1
			if q == 0:
				si_name = cl.name
				si_date = cl.posting_date
				si_amount = cl.net_total
				cogs = frappe.db.sql("""select sum(cogs) from `tabSales Invoice Item` where docstatus = '1' and parent =  %s""", cl.name)[0][0]
				count_2 = frappe.db.sql("""select count(distinct(inquiry)) from `tabSales Invoice Item` where parent = %s""", cl.name)[0][0]
				if count_2 != 0:
					inquiry = frappe.db.sql("""select distinct(inquiry) from `tabSales Invoice Item` where parent = %s""", cl.name, as_dict=1)
					expenses = 0
					for inq in inquiry:
					 	expense = frappe.db.sql("""select sum(total_debit) from `tabJournal Entry` where docstatus = '1' and inquiry = %s""", inq.inquiry)[0][0]
						expenses = flt(expenses) + flt(expense)
				else:
					expenses = ""
				net_profit = flt(si_amount) - (flt(cogs) + flt(expenses))
			else:
				si_name = ""
				si_date = ""
				si_amount = ""
				cogs = ""
				expenses = ""
				net_profit = ""
			if flt(q) < flt(count_1):
				payment = frappe.db.sql("""select parent from `tabPayment Entry Reference` where reference_name = %s and docstatus = '1' order by parent asc limit %s,%s""", (cl.name, q, i))[0][0]
				payment_date = frappe.db.sql("""select posting_date from `tabPayment Entry` where `name` = %s""", payment)[0][0]
			else:
				payment = ""
				payment_date = ""
			data.append([si_name, si_date, si_amount, payment, payment_date, cogs, expenses, net_profit])

	return columns, data

def get_columns():
	"""return columns"""

	columns = [
		_("Sales Invoice")+":Link/Sales Invoice:120",
		_("Posting Date")+":Date:100",
		_("Selling Amount")+":Currency:120",
		_("Payment")+":Link/Payment Entry:120",
		_("Payment Date")+":Date:120",
		_("HPP")+":Currency:120",
		_("Expenses")+":Currency:120",
		_("Net Profit")+":Currency:120",
	]

	return columns

def get_conditions(filters):
	conditions = ""
	if filters.get("company"):
		conditions += " and si.company = '%s'" % frappe.db.escape(filters["company"])
	if filters.get("from_date"):
		conditions += " and si.paid_date >= '%s'" % frappe.db.escape(filters["from_date"])
	if filters.get("to_date"):
		conditions += " and si.paid_date <= '%s'" % frappe.db.escape(filters["to_date"])

	return conditions

def get_entries(filters):
	conditions = get_conditions(filters)
	return frappe.db.sql("""
		select
			si.`name`,
			si.posting_date,
			si.net_total,
			(select group_concat(parent separator ', ') from `tabPayment Entry Reference` where reference_name = si.`name` and docstatus = '1') as payment,
			(select group_concat(pe.posting_date separator ', ') from `tabPayment Entry Reference` per inner join `tabPayment Entry` pe on pe.`name` = per.parent where pe.docstatus = '1' and per.reference_name = si.`name`) as payment_date,
			(select sum(cogs) from `tabSales Invoice Item` where docstatus = '1' and parent = si.`name`) as hpp, (select sum(expense_amount) from `tabSales Invoice Item` where docstatus = '1' and parent = si.`name`) as expenses,
			(si.net_total - ((select sum(cogs) from `tabSales Invoice Item` where docstatus = '1' and parent = si.`name`) + (select sum(expense_amount) from `tabSales Invoice Item` where docstatus = '1' and parent = si.`name`))) as net_profit
		from `tabSales Invoice` si
		where si.docstatus = '1' and si.type_of_invoice in ('Retention', 'Non Project Payment', 'Standard') and si.`status` = 'Paid' %s
	""" % conditions, as_dict=1)
#	return frappe.db.sql("""select distinct(iq.`name`) as inquiry, iq.transaction_date as inquiry_date, iq.sales_invoice_link,
#	(select sum(aa.net_amount) from `tabSales Invoice Item` aa inner join `tabSales Invoice` bb on aa.parent = bb.`name` where aa.inquiry = iq.`name` and bb.docstatus = '1' and bb.status = 'Paid') as selling_amount,
#	pe.`name` as payment, pe.posting_date as payment_date,
#	(select sum((sle.actual_qty * -1) * sle.valuation_rate) from `tabDelivery Note Item` dni
#	inner join `tabStock Ledger Entry` sle on dni.`name` = sle.voucher_detail_no where inquiry = iq.`name`) as cogs,
#	(select total_debit from `tabJournal Entry` where inquiry = iq.`name`) as expenses,
#	((select sum(aa.net_amount) from `tabSales Invoice Item` aa inner join `tabSales Invoice` bb on aa.parent = bb.`name` where aa.inquiry = iq.`name` and bb.docstatus = '1' and bb.status = 'Paid') -
#	(select sum((sle.actual_qty * -1) * sle.valuation_rate) from `tabDelivery Note Item` dni
#	inner join `tabStock Ledger Entry` sle on dni.`name` = sle.voucher_detail_no where inquiry = iq.`name`) -
#	(select coalesce(sum(total_debit),0) from `tabJournal Entry` where inquiry = iq.`name`)) as net_profit
#	from `tabInquiry` iq
#	inner join `tabSales Invoice Item` sii on sii.inquiry = iq.`name`
#	inner join `tabSales Invoice` si on si.`name` = sii.parent and si.type_of_invoice in ('Retention', 'Non Project Payment', 'Standard') and si.`status` = 'Paid'
#	inner join `tabPayment Entry Reference` per on sii.parent = per.reference_name
#	inner join `tabPayment Entry` pe on per.parent = pe.`name`
#	where iq.docstatus = '1' and si.docstatus = '1' and pe.docstatus = '1' %s order by iq.`name` asc""" % conditions, as_dict=1)
