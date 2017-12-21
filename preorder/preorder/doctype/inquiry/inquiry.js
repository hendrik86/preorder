// Copyright (c) 2017, ridhosribumi and contributors
// For license information, please see license.txt

frappe.ui.form.on('Inquiry', {
	refresh: function(frm) {
		frm.set_df_property("inquiry_type", "read_only", frm.doc.__islocal ? 0 : 1);
		if(frm.doc.docstatus == 1 && frm.doc.status == "Submitted" && frm.doc.complete_assembly == "Yes") {
			cur_frm.add_custom_button(__('Request for Supplier Quotation'), cur_frm.cscript['Request for Supplier Quotation'], __("Make"));
			cur_frm.add_custom_button(__('Quotation'), cur_frm.cscript['Quotation'], __("Make"));
			cur_frm.add_custom_button(__('Journal Entry'), cur_frm.cscript['Journal Entry'], __("Make"));
			cur_frm.page.set_inner_btn_group_as_primary(__("Make"));
		}
		if(frm.doc.docstatus == 1 && frm.doc.status == "Completed"){
			cur_frm.add_custom_button(__('Journal Entry'), cur_frm.cscript['Journal Entry'], __("Make"));
			cur_frm.page.set_inner_btn_group_as_primary(__("Make"));
		}
		if(frm.doc.status == "Submitted") {
			cur_frm.add_custom_button(__('Set as Lost'), cur_frm.cscript['Declare Order Lost']);
		}
	},
	on_submit: function(frm){
		frm.refresh_fields();
	},
	validate: function(frm){
		frm.events.validate_series(frm);
		frm.events.copy_to_child(frm);
	},
	validate_series: function(frm){
		if(frm.doc.inquiry_type == 'Request'){
			frm.doc.naming_series = 'R.YY.-.####'
		}else if (frm.doc.inquiry_type == 'Request Flender') {
			frm.doc.naming_series = 'RF.YY.-.####'
		}else if (frm.doc.inquiry_type == 'Request Project') {
			frm.doc.naming_series = 'RP.YY.-.####'
		}else if (frm.doc.inquiry_type == 'Request Service') {
			frm.doc.naming_series = 'RS.YY.-.####'
		}else if (frm.doc.inquiry_type == 'Request BST') {
			frm.doc.naming_series = 'RBST.YY.-.####'
		}else {
			frm.doc.naming_series = 'RPBST.YY.-.####'
		}
	},
	copy_to_child: function(frm){
		var tbl = frm.doc.items || [];
		var i = tbl.length;
		while (i--) {
			frm.doc.items[i].transaction_date = frm.doc.transaction_date;
			frm.doc.items[i].customer = frm.doc.customer;
			frm.doc.items[i].customer_name = frm.doc.customer_name;
			frm.refresh_field("items");
		}
	},
	engineer: function(frm){
		frappe.call({
			method: "frappe.client.get",
			args: {
					doctype: "Employee",
					name: frm.doc.engineer,
			},
			callback: function (data) {
					frm.set_value("engineer_name", data.message.employee_name);
			}
		})
	}
});
cur_frm.cscript['Request for Supplier Quotation'] = function() {
	frappe.model.open_mapped_doc({
		method: "preorder.preorder.doctype.inquiry.inquiry.make_rfsq",
		frm: cur_frm
	})
}
cur_frm.cscript['Quotation'] = function() {
	frappe.model.open_mapped_doc({
		method: "preorder.preorder.lemparan.get_items_selling_quotation",
		frm: cur_frm
	})
}
cur_frm.cscript['Journal Entry'] = function() {
	frappe.model.open_mapped_doc({
		method: "preorder.preorder.lemparan.make_journal_entry2",
		frm: cur_frm
	})
}
cur_frm.cscript['Declare Order Lost'] = function(){
	var dialog = new frappe.ui.Dialog({
		title: "Set as Lost",
		fields: [
			{
				"fieldtype": "Text",
				"label": __("Reason for losing"),
				"fieldname": "reason",
				"reqd": 1
			},
			{
				"fieldtype": "Button",
				"label": __("Update"),
				"fieldname": "update"
			},
		]
	});

	dialog.fields_dict.update.$input.click(function() {
		var args = dialog.get_values();
		if(!args) return;
		return cur_frm.call({
			method: "declare_order_lost",
			doc: cur_frm.doc,
			args: args.reason,
			callback: function(r) {
				if(r.exc) {
					frappe.msgprint(__("There were errors."));
					return;
				}
				dialog.hide();
				cur_frm.refresh();
			},
			btn: this
		})
	});
	dialog.show();
}

cur_frm.set_query("contact_person",  function (frm) {
		return {
        filters: [
            ['customer', '=', cur_frm.doc.customer]
        ],
		}
});
