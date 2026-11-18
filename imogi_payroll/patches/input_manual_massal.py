"""Muat DocType input massal Additional Salary (Imogi Payroll Input Manual + item) tanpa menunggu
migrate penuh. Idempoten."""

import frappe


def execute():
	frappe.reload_doc("imogi_payroll", "doctype", "imogi_payroll_input_manual_item")
	frappe.reload_doc("imogi_payroll", "doctype", "imogi_payroll_input_manual")
	frappe.clear_cache()
