// Copyright (c) 2017, ridhosribumi and contributors
// For license information, please see license.txt

frappe.ui.form.on('Item Settings', {
	refresh: function(frm) {

	},
	default_item_for_inquiry: function(frm){
		frappe.call({
			method: "frappe.client.get",
			args: {
					doctype: "Item",
					name: frm.doc.default_item_for_inquiry,
			},
			callback: function (data) {
					frm.set_value("inquiry_item_name", data.message.item_name);
					frm.set_value("inquiry_item_descrition", data.message.description);
					frm.set_value("inquiry_item_uom", data.message.stock_uom);
			}
		})
	}
});
cur_frm.fields_dict.selling_write_off_account.get_query = function(doc) {
	return{
		filters:{
			'is_group': 0,
			'company': doc.company
		}
	}
}
cur_frm.fields_dict.buying_write_off_account.get_query = function(doc) {
	return{
		filters:{
			'is_group': 0,
			'company': doc.company
		}
	}
}
cur_frm.fields_dict.default_item_group.get_query = function(doc) {
	return{
		filters:{
			'is_group': 0
		}
	}
}
