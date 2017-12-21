# Copyright (c) 2013, ridhosribumi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, getdate

def execute(filters=None):
	columns = get_columns()
	sl_entries = get_entries(filters)
	data = []

	for ri in sl_entries:
		if ri.dn_date:
			a_dn_date = ri.dn_date.strftime("%B %Y")
		else:
			a_dn_date = ""
		if ri.si_date:
			a_si_date = ri.si_date.strftime("%B %Y")
		else:
			a_si_date = ""
		if ri.delivery and ri.no_si:
			if a_dn_date == a_si_date:
				check = "&#10004;"
			else:
				if ri.jv_name and ri.re_name:
					check = "&#10004;"
				else:
					check = "-"
		else:
			check = "-"
		if ri.jv_name:
			a_jv_date = ri.jv_date
		else:
			if a_dn_date != a_si_date and ri.no_si:
				a_jv_date = "<a href='/desk#Form/Journal%20Entry/New%20Journal%20Entry%201?delivery_note="+ri.delivery+"'>Make JV</a>"
			else:
				a_jv_date = ""
		data.append([a_dn_date, ri.delivery, ri.dn_total, ri.hpp, a_si_date, ri.no_si, ri.si_total, a_jv_date, ri.jv_name, ri.re_date, ri.re_name, check])

	return columns, data

def get_columns():
	"""return columns"""

	columns = [
		_("Tgl DN")+"::100",
		_("No DN")+":Link/Delivery Note:100",
		_("Nilai DN")+":Currency:100",
		_("HPP")+":Currency:100",
		_("Tgl SI")+"::100",
		_("No SI")+":Link/Sales Invoice:100",
		_("Nilai SI")+":Currency:100",
		_("Tgl JV")+"::100",
		_("No JV")+":Link/Journal Entry:100",
		_("Tgl RJV")+"::100",
		_("No RJV")+":Link/Journal Entry:100",
		_("Check")+"::50",
	]

	return columns

def get_conditions(filters):
	conditions = ""
	if filters.get("from_date"):
		conditions += " and dn.posting_date <= '%s'" % frappe.db.escape(filters["from_date"])
	return conditions

def get_entries(filters):
	conditions = get_conditions(filters)
	return frappe.db.sql("""select distinct(so2.delivery_note) as delivery, dn.posting_date as dn_date, dn.net_total as dn_total, (select sum((actual_qty * -1) * valuation_rate) from `tabStock Ledger Entry` where voucher_no = dn.`name`) as hpp, so2.sales_invoice as no_si, si.posting_date as si_date, si.net_total as si_total, je.posting_date as jv_date, je.`name` as jv_name, re.posting_date as re_date, re.`name` as re_name from `tabSales Order to Invoice` so2 inner join `tabDelivery Note` dn on so2.delivery_note = dn.`name` left join `tabSales Invoice` si on so2.sales_invoice = si.`name` left join `tabJournal Entry` je on so2.delivery_note = je.delivery_note and je.docstatus = '1' and je.reversing_entry = '0' left join `tabJournal Entry` re on so2.delivery_note = re.delivery_note and re.docstatus = '1' and re.reversing_entry = '1' where so2.delivery_note is not null %s order by dn.`name` asc""" % conditions, as_dict=1)
#	return frappe.db.sql("""select dn.posting_date as dn_date, dn.`name` as delivery, dn.net_total as dn_total, (select sum((actual_qty * -1) * valuation_rate) from `tabStock Ledger Entry` where voucher_no = dn.`name`) as hpp, si.posting_date as si_date, si.`name` as no_si, si.net_total as si_total, je.posting_date as jv_date, je.`name` as jv_name, re.posting_date as re_date, re.`name` as re_name from `tabDelivery Note` dn left join `tabSales Invoice` si on dn.inquiry = si.inquiry and si.docstatus = '1' and si.type_of_invoice in ('Retention', 'Non Project Payment', 'Standard') left join `tabJournal Entry` je on dn.`name` = je.delivery_note and je.docstatus = '1' and je.reversing_entry = '0' left join `tabJournal Entry` re on dn.`name` = re.delivery_note and re.docstatus = '1' and re.reversing_entry = '1' where dn.docstatus = '1' and dn.inquiry is not null %s order by dn.`name` asc""" % conditions, as_dict=1)
#
