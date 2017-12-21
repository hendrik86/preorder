frappe.listview_settings['Request for Supplier Quotation'] = {
	add_fields: ["supplier_name", "company", "action_status"],
	get_indicator: function(doc) {
		/*
		if(doc.status==="Submitted") {
			return [__("Submitted"), "blue", "status,=,Submitted"];
		} else if(doc.status==="Completed") {
			return [__("Completed"), "green", "status,=,Completed"];
		} else if(doc.status==="Lost") {
			return [__("Lost"), "darkgrey", "status,=,Lost"];
		}
		*/
		if(doc.action_status==="Clarify to Customer") {
			return [__("Clarify to Customer"), "blue", "action_status,=,Clarify to Customer"];
		}
		if(doc.action_status==="Clarify to Vendor") {
			return [__("Clarify to Vendor"), "orange", "action_status,=,Clarify to Vendor"];
		}
		if(doc.action_status==="Completed") {
			return [__("Completed"), "green", "action_status,=,Completed"];
		}
		if(doc.action_status==="Submitted and Waiting") {
			return [__("Submitted and Waiting"), "purple", "action_status,=,Submitted and Waiting"];
		}
		if(doc.action_status==="No Quote") {
			return [__("No Quote"), "darkgrey", "action_status,=,No Quote"];
		}
	}
};
