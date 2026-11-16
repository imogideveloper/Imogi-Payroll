"""Dasar iuran BPJS = UMP wilayah karyawan (mengikuti Odoo).

1. Buat master Imogi Payroll UMP Region dari setup/default_ump.json (UMP 2024-2026,
   diambil dari Odoo hr.master.ump). Hanya menambah wilayah yang belum ada.
2. Ganti formula komponen BPJS supaya memakai get_bpjs_wage() - memakai UMP
   wilayah karyawan; tanpa wilayah tetap berperilaku seperti sebelumnya - dan
   matikan "depends on payment days" di komponen itu (Odoo tidak memprorata BPJS).
Idempoten: boleh dijalankan berulang.
"""

import json
import os
import re

import frappe


def _convert(formula: str) -> str:
	if not formula or "get_bpjs_wage" in formula:
		return formula
	f = formula.replace(
		"(base if base >= 5396761 else 5396761)",
		"get_bpjs_wage(employee, end_date, base, 5396761)",
	)
	f = re.sub(
		r"\(base if base <= get_bpjs_cap\('(\w+)'\) else get_bpjs_cap\('\1'\)\)",
		r"min(get_bpjs_wage(employee, end_date, base), get_bpjs_cap('\1'))",
		f,
	)
	return re.sub(r"^base \*", "get_bpjs_wage(employee, end_date, base) *", f)


def execute():
	frappe.reload_doc("imogi_payroll", "doctype", "imogi_payroll_ump_year")
	frappe.reload_doc("imogi_payroll", "doctype", "imogi_payroll_ump_region")

	path = os.path.join(frappe.get_app_path("imogi_payroll"), "setup", "default_ump.json")
	with open(path) as fh:
		regions = json.load(fh)
	for r in regions:
		if frappe.db.exists("Imogi Payroll UMP Region", r["region_name"]):
			continue
		doc = frappe.get_doc(
			{
				"doctype": "Imogi Payroll UMP Region",
				"region_name": r["region_name"],
				"ump_years": [{"year": y["year"], "amount": y["amount"]} for y in r["years"]],
			}
		)
		doc.insert(ignore_permissions=True)

	for name, formula in frappe.get_all(
		"Salary Component", filters={"name": ["like", "%BPJS%"]}, fields=["name", "formula"], as_list=True
	):
		new = _convert(formula or "")
		if new != (formula or ""):
			frappe.db.set_value("Salary Component", name, "formula", new, update_modified=False)
		# Odoo tidak memprorata iuran BPJS (dasarnya UMP penuh), jadi komponen ini
		# tidak boleh ikut hari kerja.
		if "get_bpjs_wage" in new:
			frappe.db.set_value("Salary Component", name, "depends_on_payment_days", 0, update_modified=False)
