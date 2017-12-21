# -*- coding: utf-8 -*-
# Copyright (c) 2017, ridhosribumi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import msgprint, _
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc

class Inquiry(Document):
	def check_item_table(self):
		if not self.get('items'):
			frappe.msgprint(_("Please enter item details"))

	def validate(self):
		yes = 0
		for row in self.items:
			if not row.is_product_assembly:
				yes = 1
		if yes == 1:
			frappe.db.set(self, 'complete_assembly', 'Yes')
		else:
			frappe.db.set(self, 'complete_assembly', 'No')

	def on_submit(self):
		self.check_item_table()
		self.check_assembly_item()
		self.insert_to_all_item()

	def before_cancel(self):
		self.delete_all_item()

	def on_cancel(self):
		frappe.db.set(self, 'status', 'Cancelled')

	def declare_order_lost(self, arg):
		frappe.db.set(self, 'status', 'Lost')
		frappe.db.set(self, 'order_lost_reason', arg)

	def check_assembly_item(self):
		exist = 0
		for row in self.items:
			if row.is_product_assembly:
				exist = 1
				product_assembly = frappe.get_doc({
					"doctype": "Product Assembly",
					"parent_item": row.item_description,
					"inquiry": self.name,
					"inquiry_item": row.name,
					"quantity": row.qty
				})
				product_assembly.insert()

		if exist == 1:
			self.update_inquiry_item()
			frappe.db.set(self, 'status', 'Engineered')
		else:
			frappe.db.set(self, 'status', 'Submitted')

	def update_inquiry_item(self):
		for row in self.items:
			product_assembly = frappe.db.get_value("Product Assembly", {"inquiry_item": row.name}, "name")
			if product_assembly:
				frappe.db.sql("""update `tabInquiry Item` set product_assembly = %s where `name` = %s""", (product_assembly, row.name))

	def insert_to_all_item(self):
		no = 0
		frappe.db.sql("""delete from `tabInquiry All Item` where `parent` = %s""", self.name)
		for row in self.items:
			if not row.is_product_assembly:
				no = no+1
				items = frappe.get_doc({
					"doctype": "Inquiry All Item",
					"parent": self.name,
					"parentfield": "item_all",
					"parenttype": "Inquiry",
					"idx": no,
					"item_description": row.item_description,
					"qty": row.qty,
					"uom": row.uom
				})
				items.insert()

	def delete_all_item(self):
		frappe.db.sql("""delete from `tabInquiry All Item` where `parent` = %s""", self.name)

@frappe.whitelist()
def make_rfsq(source_name, target_doc=None):
	def set_missing_values(source, target):
		target.run_method("set_missing_values")

	si = get_mapped_doc("Inquiry", source_name, {
		"Inquiry": {
			"doctype": "Request for Supplier Quotation",
			"field_no_map": [
				"naming_series", "title"
			],
			"field_map": {
				"transaction_date":"date"
			},
		},
		"Inquiry Item":{
			"doctype": "Request for Supplier Quotation Inquiry",
			"condition":lambda doc: doc.idx == 1,
		},
		"Inquiry All Item":{
			"doctype": "Request for Supplier Quotation Item",
			"field_map": {
				"name":"inquiry_detail"
			},
		}
	}, target_doc, set_missing_values)
	return si
