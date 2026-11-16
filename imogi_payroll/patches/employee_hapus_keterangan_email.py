"""Hapus teks keterangan bawaan di field Company Email (Employee) supaya form lebih bersih."""

import frappe
from frappe.custom.doctype.property_setter.property_setter import make_property_setter


def execute():
	make_property_setter("Employee", "company_email", "description", "", "Small Text")
