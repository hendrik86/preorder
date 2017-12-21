from __future__ import unicode_literals
import frappe, json
from frappe.utils import nowdate, cstr, flt, now, getdate, add_months
from frappe import msgprint, _
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc

@frappe.whitelist()
def reset_rate(doc):
    #msgprint(_(doc{"customer"}))
    pass

@frappe.whitelist()
def get_items_selling_quotation(source_name, target_doc=None):
    cek = frappe.db.get_value("Inquiry", source_name, "status")
    if cek != "Lost":
#        if target_doc:
#            if isinstance(target_doc, basestring):
#                import json
#                target_doc = frappe.get_doc(json.loads(target_doc))
#            target_doc.set("items", [])
#            target_doc.set("assembly_item", [])

        def update_item(source, target, source_parent):
            target.item_code = frappe.db.sql("""select `value` from `tabSingles` where doctype = 'Item Settings' and field = 'default_item_for_inquiry'""")[0][0]
            target.item_name = frappe.db.sql("""select `value` from `tabSingles` where doctype = 'Item Settings' and field = 'inquiry_item_name'""")[0][0]
            target.description = frappe.db.sql("""select `value` from `tabSingles` where doctype = 'Item Settings' and field = 'inquiry_item_descrition'""")[0][0]
            target.qty = flt(source.qty) - flt(source.qty_used)

        def update_assembly_item(source, target, source_parent):
            pa = frappe.db.get_value("Product Assembly", source.product_assembly, ["parent_item", "product_bundle"], as_dict=1)
            target.parent_item = pa.parent_item
            target.product_bundle = pa.product_bundle
            target.base_qty = frappe.db.get_value("Product Assembly Item", source.product_assembly_item, "qty")

        doc = get_mapped_doc("Inquiry", source_name, {
    		"Inquiry": {
    			"doctype": "Quotation",
    			"validation": {
    				"docstatus": ["=", 1],
    			},
                "field_no_map":["inquiry"]
    		},
    		"Inquiry Item": {
    			"doctype": "Quotation Item",
    			"field_map":{
    				"parent": "inquiry",
    				"name": "inquiry_item",
    			},
                "condition":lambda doc: doc.qty > doc.qty_used,
                "postprocess": update_item
    		},
    		"Inquiry All Item": {
    			"doctype": "Quotation Assembly Item",
                "condition":lambda doc: doc.is_product_assembly == 1,
                "postprocess": update_assembly_item
    		},
    	}, target_doc)
        return doc

@frappe.whitelist()
def get_items_from_sales_order(source_name, target_doc=None):
    doc = get_mapped_doc("Sales Order", source_name, {
    	"Sales Order": {
    		"doctype": "Purchase Order",
    		"validation": {
    			"docstatus": ["=", 1],
    		},
            "field_no_map": [
                "contact_person", "contact_display"
            ],
    	},
    	"Sales Order Item": {
    		"doctype": "Purchase Order Item",
    		"field_map":{
    			"name": "sales_order_item"
    		},
            "field_no_map": [
                "price_list_rate", "rate", "amount"
            ],
			"add_if_empty": True
    	},
    }, target_doc)

    return doc

@frappe.whitelist()
def make_purchase_order(source_name, target_doc=None):
	pi = get_mapped_doc("Sales Order", source_name, {
		"Sales Order": {
			"doctype": "Purchase Order",
			"validation": {
				"docstatus": ["=", 1]
			}
		},
		"Sales Order Item": {
			"doctype": "Purchase Order Item",
			"field_map": {
				"parent": "sales_order"
			},
            "field_no_map": [
                "price_list_rate", "rate"
            ],
			"add_if_empty": True
		}
	}, target_doc)

	return pi

@frappe.whitelist()
def get_items_tampungan(related_doc, tipe, percen):
    si_list = []
    item_dp = frappe.db.sql("""select `value` from `tabSingles` where doctype = 'Item Settings' and field = 'default_item_for_dp'""")[0][0]
    item = frappe.db.get_value("Item", item_dp, ["item_name", "description", "stock_uom", "income_account", "expense_account"], as_dict=1)
    if tipe == "Down Payment":
        so = frappe.db.get_value("Sales Order", related_doc, ["total"], as_dict=1)
    else:
        so = frappe.db.get_value("Delivery Note", related_doc, ["total"], as_dict=1)
    rate = (flt(percen)/100) * flt(so.total)
    si_list.append(frappe._dict({
        'item_code': item_dp,
        'item_name': item.item_name,
        'description': item.description,
        'qty':1,
        'uom': item.stock_uom,
        'rate': rate,
        'amount': rate,
        'income_account': item.income_account,
        'expense_account': item.expense_account
    }))
    return si_list

@frappe.whitelist()
def get_delivery_note(sales_order):
    if sales_order:
        dn_list = []
        invoice_list = frappe.db.sql("""select distinct(dn.`name`), dn.posting_date, dn.total, dn.net_total from `tabDelivery Note` dn inner join `tabDelivery Note Item` dni on dn.`name` = dni.parent where dn.docstatus = '1' and dni.against_sales_order = %s and dn.sales_invoice is null""", sales_order, as_dict=True)
        for d in invoice_list:
            dn_list.append(frappe._dict({
                'delivery_note': d.name,
                'posting_date': d.posting_date,
                'total': d.total,
                'net_total': d.net_total
            }))

        return dn_list

@frappe.whitelist()
def get_items_from_pelunasan(sales_order, total_delivery, percen):
    si_list = []
    item_dp = frappe.db.sql("""select `value` from `tabSingles` where doctype = 'Item Settings' and field = 'default_item_for_dp'""")[0][0]
    item = frappe.db.get_value("Item", item_dp, ["item_name", "description", "stock_uom", "income_account", "expense_account"], as_dict=1)
    rate = (flt(percen)/100) * flt(total_delivery)
    si_list.append(frappe._dict({
        'item_code': item_dp,
        'item_name': item.item_name,
        'description': item.description,
        'qty':1,
        'uom': item.stock_uom,
        'rate': rate,
        'amount': rate,
        'income_account': item.income_account,
        'expense_account': item.expense_account
    }))
    return si_list

@frappe.whitelist()
def get_sales_invoice(sales_order, tipe):
    invoice_list = frappe.db.sql("""select sales_invoice, posting_date, total, net_total from `tabSales Order Invoice` where docstatus = '1' and parent = %s order by sales_invoice asc""", sales_order, as_dict=True)
    si_list = []
    for d in invoice_list:
        si_list.append(frappe._dict({
            'sales_invoice': d.sales_invoice,
            'posting_date': d.posting_date,
            'total': d.total,
            'net_total': d.net_total
        }))
    return si_list

@frappe.whitelist()
def get_sales_invoice2(sales_order, delivery, tipe, total):
    if sales_order != 'none':
        si_list = []
        invoice_list = frappe.db.sql("""select sales_invoice, posting_date, total, net_total from `tabSales Order Invoice` where docstatus = '1' and parent = %s order by sales_invoice asc""", sales_order, as_dict=True)
        for d in invoice_list:
            si_list.append(frappe._dict({
                'sales_invoice': d.sales_invoice,
                'posting_date': d.posting_date,
                'total': d.total,
                'net_total': d.net_total
            }))
        return si_list
    if delivery != 'none':
        so = frappe.db.sql("""select distinct(against_sales_order) as so from `tabDelivery Note Item` where docstatus = '1' and parent = %s """, delivery, as_dict=True)
        for ss in so:
            si_list = []
            invoice_list = frappe.db.sql("""select sales_invoice, posting_date, total, net_total from `tabSales Order Invoice` where docstatus = '1' and parent = %s order by sales_invoice asc""", ss.so, as_dict=True)
            for d in invoice_list:
                total_so = frappe.db.sql("""select net_total as so from `tabSales Order` where docstatus = '1' and `name` = %s """, ss.so)[0][0]
                total_si = (flt(total) / flt(total_so)) * flt(d.total)
                net_total = (flt(total) / flt(total_so)) * flt(d.net_total)
                si_list.append(frappe._dict({
                    'sales_invoice': d.sales_invoice,
                    'posting_date': d.posting_date,
                    'total': total_si,
                    'net_total': net_total
                }))
            return si_list

@frappe.whitelist()
def make_journal_entry(source_name, target_doc=None):
	def set_missing_values(source, target):
		target.run_method("set_missing_values")

	jv = get_mapped_doc("Delivery Note", source_name, {
		"Delivery Note": {
			"doctype": "Journal Entry",
    		"field_map":{
    			"posting_date": "posting_date"
    		},
		},
	}, target_doc, set_missing_values)
	return jv

@frappe.whitelist()
def make_reverse_journal(source_name, target_doc=None):
	def set_missing_values(source, target):
		target.reversing_entry = 1
		target.run_method("set_missing_values")

	jv = get_mapped_doc("Journal Entry", source_name, {
		"Journal Entry": {
			"doctype": "Journal Entry",
    		"field_map":{
    			"posting_date": "posting_date"
    		},
		},
		"Journal Entry Account": {
			"doctype": "Journal Entry Account",
    		"field_map":{
				"credit_in_account_currency": "debit_in_account_currency",
                "debit_in_account_currency": "credit_in_account_currency",
    		},
		},
	}, target_doc, set_missing_values)
	return jv

@frappe.whitelist()
def get_amount(dn):
    dn_list = []
    list1 = frappe.db.sql("""select sum((actual_qty * -1) * valuation_rate) as debit from `tabStock Ledger Entry` where voucher_no = %s""", dn, as_dict=True)
    for d in list1:
        dn_list.append(frappe._dict({
            'party_type': 'Customer',
            'debit': d.debit,
            'credit': ''
        }))
    list2 = frappe.db.sql("""select sum((actual_qty * -1) * valuation_rate) as credit from `tabStock Ledger Entry` where voucher_no = %s""", dn, as_dict=True)
    for d in list2:
        dn_list.append(frappe._dict({
            'party_type': 'Customer',
            'debit': '',
            'credit': d.credit
        }))
    return dn_list

@frappe.whitelist()
def get_inquiry_items(source_name, target_doc=None):
    cek = frappe.db.get_value("Inquiry", source_name, "status")
    if cek != "Lost":
        if target_doc:
            if isinstance(target_doc, basestring):
                import json
                target_doc = frappe.get_doc(json.loads(target_doc))
            target_doc.set("items", [])

        doc = get_mapped_doc("Sales Order", source_name, {
    		"Sales Order": {
    			"doctype": "Stock Entry",
    			"validation": {
    				"docstatus": ["=", 1],
    			},
    		},
    		"Packed Item": {
    			"doctype": "Stock Entry Detail",
    		},
    	}, target_doc)
        return doc

@frappe.whitelist()
def make_journal_entry(source_name, target_doc=None):
    doc = get_mapped_doc("Delivery Note", source_name, {
    	"Delivery Note": {
    		"doctype": "Journal Entry",
    		"validation": {
    			"docstatus": ["=", 1],
    		},
    	},
    }, target_doc)
    return doc

@frappe.whitelist()
def make_journal_entry2(source_name, target_doc=None):
    doc = get_mapped_doc("Inquiry", source_name, {
    	"Inquiry": {
    		"doctype": "Journal Entry",
    		"validation": {
    			"docstatus": ["=", 1],
    		},
    	},
    }, target_doc)
    return doc
