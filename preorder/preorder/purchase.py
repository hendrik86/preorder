from __future__ import unicode_literals
import frappe
from frappe.utils import nowdate, cstr, flt, now, getdate, add_months
from frappe import msgprint, _
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc

@frappe.whitelist()
def make_purchase_order(source_name, target_doc=None):
	def set_missing_values(source, target):
		target.ignore_pricing_rule = 1
		target.run_method("set_missing_values")
		target.run_method("get_schedule_dates")
		target.run_method("calculate_taxes_and_totals")

	def update_item(source, target, source_parent):
		target.stock_qty = flt(source.qty) * flt(source.conversion_factor)
		target.price_list_rate = 0
		target.rate = 0

	def update_item_assembly(source, target, source_parent):
		target.description = frappe.db.sql("""select item_description from `tabProduct Assembly Item` where `name` = %s""", source.product_assembly_item)[0][0]
		target.item_code = frappe.db.sql("""select item_code from `tabProduct Assembly Item` where `name` = %s""", source.product_assembly_item)[0][0]

	doclist = get_mapped_doc("Sales Order", source_name, {
		"Sales Order": {
			"doctype": "Purchase Order",
			"validation": {
				"docstatus": ["=", 1],
			},
			"field_no_map":["currency", "conversion_rate", "shipping_address", "contact_person", "address_display"]
		},
		"Sales Order Item": {
			"doctype": "Purchase Order Item",
			"field_map": [
				["name", "sales_order_item"],
				["parent", "sales_order"],
			],
			"field_no_map":["price_list_rate", "rate", "amount", "net_rate", "net_amount"],
			"condition":lambda doc: doc.is_product_assembly == 0,
			"postprocess": update_item
		},
		"Quotation Assembly Item": {
			"doctype": "Purchase Order Item",
			"postprocess": update_item_assembly
		},
	}, target_doc, set_missing_values)

	return doclist

@frappe.whitelist()
def get_po_items(tipe, related_doc, percen):
    pi_list = []
    item_dp = frappe.db.sql("""select `value` from `tabSingles` where doctype = 'Item Settings' and field = 'default_item_for_dp'""")[0][0]
    item = frappe.db.get_value("Item", item_dp, ["item_name", "description", "stock_uom", "income_account", "expense_account"], as_dict=1)
    if tipe == "Down Payment":
        so = frappe.db.get_value("Purchase Order", related_doc, ["total"], as_dict=1)
    else:
        so = frappe.db.get_value("Purchase Receipt", related_doc, ["total"], as_dict=1)
    rate = (flt(percen)/100) * flt(so.total)
    pi_list.append(frappe._dict({
        'item_code': item_dp,
        'item_name': item.item_name,
        'description': item.description,
        'qty':1,
        'uom': item.stock_uom,
        'rate': rate,
        'amount': rate,
        'expense_account': item.expense_account
    }))
    return pi_list

@frappe.whitelist()
def get_purchase_receipt(supplier, po):
    if supplier and po:
        pr_list = []
        invoice_list = frappe.db.sql("""select `name`, posting_date, base_total, base_net_total, total, net_total from `tabPurchase Receipt` where docstatus = '1' and status = 'To Bill' and supplier = %s and invoice_payment is null and purchase_order = %s""", (supplier, po), as_dict=True)
        for d in invoice_list:
            pr_list.append(frappe._dict({
                'purchase_receipt': d.name,
                'posting_date': d.posting_date,
				'total': d.total,
                'net_total': d.net_total,
				'base_total': d.base_total,
                'base_net_total': d.base_net_total
            }))

        return pr_list

@frappe.whitelist()
def get_items_payment(supplier):
    if supplier:
        pr_list = []
        item = frappe.db.sql("""select `value` from `tabSingles` where doctype = 'Item Settings' and field = 'default_item_for_dp'""")[0][0]
        item_detail = frappe.db.get_value("Item", item, ["item_name", "description", "stock_uom", "income_account", "expense_account"], as_dict=1)
        pr_list.append(frappe._dict({
            'item_code': item,
            'item_name': item_detail.item_name,
            'description': item_detail.item_description,
            'uom': item_detail.stock_uom,
            'stock_uom': item_detail.stock_uom,
            'qty': '1',
            'expense_account': item_detail.expense_account
        }))

        return pr_list

@frappe.whitelist()
def get_purchase_invoice(supplier, po, invoice_type, net_total, base_net_total):
    pi_list = []
    if invoice_type == 'Non Project Payment':
        invoice_list = frappe.db.sql("""select `name`, posting_date, base_total, base_net_total, total, net_total from `tabPurchase Invoice` where docstatus = '1' and type_of_invoice = 'Down Payment' and purchase_order = %s""", po, as_dict=True)
    else:
        invoice_list = frappe.db.sql("""select `name`, posting_date, base_total, base_net_total, total, net_total from `tabPurchase Invoice` where docstatus = '1' and purchase_order = %s""", po, as_dict=True)
    for d in invoice_list:
        total_po = frappe.db.sql("""select net_total from `tabPurchase Order` where docstatus = '1' and `name` = %s""", po)[0][0]
        base_total_po = frappe.db.sql("""select base_net_total from `tabPurchase Order` where docstatus = '1' and `name` = %s""", po)[0][0]
        alokasi = (flt(net_total) / flt(total_po)) * flt(d.net_total)
        alokasi_total = (flt(net_total) / flt(total_po)) * flt(d.total)
        base_alokasi = (flt(base_net_total) / flt(base_total_po)) * flt(d.base_net_total)
        base_alokasi_total = (flt(base_net_total) / flt(base_total_po)) * flt(d.base_total)
        if alokasi != 0:
            pi_list.append(frappe._dict({
                'purchase_invoice': d.name,
                'posting_date': d.posting_date,
                'base_total': base_alokasi_total,
                'base_net_total': base_alokasi,
                'total': alokasi_total,
                'net_total': alokasi
            }))
    return pi_list
