"""Muat DocType input massal Additional Salary (Additional Multiple Salary + item; dulu Imogi Payroll Input Manual) tanpa menunggu
migrate penuh. Idempoten."""

import frappe


def execute():
	frappe.reload_doc("imogi_payroll", "doctype", "additional_multiple_salary_item")
	frappe.reload_doc("imogi_payroll", "doctype", "additional_multiple_salary")
	frappe.clear_cache()
