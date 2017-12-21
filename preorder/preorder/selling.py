from __future__ import unicode_literals
import frappe
from frappe.utils import nowdate, cstr, flt, now, getdate, add_months
from frappe import msgprint, _
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc

@frappe.whitelist()
def make_sales_order(source_name, target_doc=None):
	quotation = frappe.db.get_value("Quotation", source_name, ["transaction_date", "valid_till"], as_dict = 1)
	if quotation.valid_till and (quotation.valid_till < quotation.transaction_date or quotation.valid_till < getdate(nowdate())):
		frappe.throw(_("Validity period of this quotation has ended."))
	return _make_sales_order(source_name, target_doc)

def _make_sales_order(source_name, target_doc=None, ignore_permissions=False):
	def set_missing_values(source, target):
		target.ignore_pricing_rule = 1
		target.flags.ignore_permissions = ignore_permissions
		target.run_method("set_missing_values")
		target.run_method("calculate_taxes_and_totals")

	def update_item(source, target, source_parent):
		target.stock_qty = flt(source.qty) * flt(source.conversion_factor)
		target.quotation_rate = flt(source.rate)
		target.qty = flt(source.qty) - flt(source.so_qty)

	doclist = get_mapped_doc("Quotation", source_name, {
			"Quotation": {
				"doctype": "Sales Order",
				"validation": {
					"docstatus": ["=", 1]
				}
			},
			"Quotation Item": {
				"doctype": "Sales Order Item",
				"field_map": {
					"parent": "prevdoc_docname",
                    "name": "quotation_item"
				},
				"field_no_map":["mark_as_complete"],
				"postprocess": update_item,
				"condition":lambda doc: doc.so_qty < doc.qty
			},
			"Sales Taxes and Charges": {
				"doctype": "Sales Taxes and Charges",
				"add_if_empty": True
			},
			"Sales Team": {
				"doctype": "Sales Team",
				"add_if_empty": True
			}
		}, target_doc, set_missing_values, ignore_permissions=ignore_permissions)

	# postprocess: fetch shipping address, set missing values

	return doclist

@frappe.whitelist()
def get_sales_order(doctype, txt, searchfield, start, page_len, filters):
	from erpnext.controllers.queries import get_match_cond

	if not filters: filters = {}

	condition = ""
	if filters.get("inquiry"):
		condition += "and soi.inquiry = %(inquiry)s"

	return frappe.db.sql("""select distinct(soi.parent) from `tabSales Order Item` soi
		where soi.docstatus='1'
			and soi.parent LIKE %(txt)s
			{condition} {match_condition}"""
		.format(condition=condition,
			match_condition=get_match_cond(doctype)), {
			'inquiry': filters.get("inquiry", ""),
			'txt': "%%%s%%" % frappe.db.escape(txt)
		})
