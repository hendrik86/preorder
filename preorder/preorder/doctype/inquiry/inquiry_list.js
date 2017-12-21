frappe.listview_settings['Inquiry'] = {
	add_fields: ["customer_name", "status",	"company"],
	get_indicator: function(doc) {
		if(doc.status==="Submitted") {
			return [__("Submitted"), "blue", "status,=,Submitted"];
		} else if(doc.status==="Completed") {
			return [__("Completed"), "green", "status,=,Completed"];
		} else if(doc.status==="Engineered") {
			return [__("Engineered"), "purple", "status,=,Engineered"];
		} else if(doc.status==="Lost") {
			return [__("Lost"), "darkgrey", "status,=,Lost"];
		}
	}
};
