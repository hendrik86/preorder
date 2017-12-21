# -*- coding: utf-8 -*-
# Copyright (c) 2017, ridhosribumi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import msgprint, _
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc

class RequestforSupplierQuotation(Document):
	def validate(self):
		pass

	def on_update(self):
		frappe.db.set(self, 'status', 'Draft')

	def on_submit(self):
		frappe.db.set(self, 'status', 'Submitted')

	def on_cancel(self):
		frappe.db.set(self, 'status', 'Cancelled')

	def get_items(self):
#		tampung = []
		self.set('items', [])
		for row in self.inquiry_tbl:
			komponen = frappe.db.sql("""SELECT b.item_description, b.qty, b.uom, a.`name` as inq, b.`name` as inq_det
				FROM `tabInquiry` a, `tabInquiry All Item` b
				WHERE a.`name` = b.parent AND a.docstatus = '1' AND a.`name` = %s AND a.status != "Lost"
				ORDER by b.idx ASC""", row.inquiry, as_dict=1)

			for d in komponen:
				nl = self.append('items', {})
				nl.item_description = d.item_description
				nl.qty = d.qty
				nl.uom = d.uom
				nl.inquiry = d.inq
				nl.inquiry_detail = d.inq_det
#			tampung.append(row.inquiry)
#		temp = ', '.join(tampung)
#		frappe.msgprint(temp)

	def declare_order_lost(self, arg):
		frappe.db.set(self, 'status', 'Lost')
		frappe.db.set(self, 'order_lost_reason', arg)

	def send_to_supplier(self):
		if self.email_id:
			# make new user if required
			update_password_link = None

			self.supplier_rfq_mail(None, update_password_link, self.get_link())

	def get_link(self):
		# RFQ link for supplier portal
		return get_url("/rfsq/" + self.name)

	def supplier_rfq_mail(self, data, update_password_link, rfq_link):
		full_name = get_user_fullname(frappe.session['user'])
		if full_name == "Guest":
			full_name = "Administrator"

		args = {
			'update_password_link': update_password_link,
			'message': frappe.render_template(self.message_for_supplier, data.as_dict()),
			'rfq_link': rfq_link,
			'user_fullname': full_name
		}

		subject = _("Request for Quotation: {0}".format(self.name))
		template = "templates/emails/request_for_quotation.html"
		sender = frappe.session.user not in STANDARD_USERS and frappe.session.user or None
		message = frappe.get_template(template).render(args)
		attachments = self.get_attachments()

		self.send_email(data, sender, subject, message, attachments)

	def send_email(self, data, sender, subject, message, attachments):
		make(subject = subject, content=message,recipients=data.email_id,
			sender=sender,attachments = attachments, send_email=True,
		     	doctype=self.doctype, name=self.name)["name"]

		frappe.msgprint(_("Email sent to supplier {0}").format(data.supplier))

	def get_attachments(self):
		attachments = [d.name for d in get_attachments(self.doctype, self.name)]
		attachments.append(frappe.attach_print(self.doctype, self.name, doc=self))
		return attachments

@frappe.whitelist()
def send_supplier_emails(rfq_name):
	rfq = frappe.get_doc("Request for Supplier Quotation", rfq_name)
	if rfq.docstatus==1:
		rfq.send_to_supplier()
