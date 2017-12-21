from frappe import _

def get_data():
	return {
		'fieldname': 'inquiry',
		'transactions': [
			{
				'items': ['Request for Supplier Quotation', 'Quotation', 'Sales Order', 'Delivery Note', 'Sales Invoice']
			},
		]
    }
