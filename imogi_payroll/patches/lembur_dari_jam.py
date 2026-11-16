"""Lembur dari jam (mengikuti Odoo): doctype input harian + komponen gaji "Lembur" otomatis.

1. Reload doctype Imogi Payroll Overtime / Overtime Settings / Overtime Coefficient.
2. Isi tabel koefisien bawaan (nilai Odoo) dan pembagi 173 bila belum ada.
3. Buat/perbarui Salary Component "Lembur": formula get_overtime_amount(employee, start_date,
   end_date, base), tanpa prorata hari bayar (seperti Odoo).
4. Tambahkan "Lembur" ke Salary Structure "Indonesian Payroll Standard" bila masih Draft.
Idempoten.
"""

import frappe

from imogi_payroll.config.overtime import DEFAULT_COEFFICIENTS, DEFAULT_DIVISOR

FORMULA = "get_overtime_amount(employee, start_date, end_date, base)"
STRUCTURE = "Indonesian Payroll Standard"


def execute():
	for dt in ("imogi_payroll_overtime_coefficient", "imogi_payroll_overtime_settings", "imogi_payroll_overtime"):
		frappe.reload_doc("imogi_payroll", "doctype", dt)

	settings = frappe.get_single("Imogi Payroll Overtime Settings")
	if not settings.get("coefficients"):
		settings.divisor = DEFAULT_DIVISOR
		for day_type, table in DEFAULT_COEFFICIENTS.items():
			row = {"day_type": day_type}
			row.update({"jam_%d" % (i + 1): v for i, v in enumerate(table)})
			settings.append("coefficients", row)
		settings.save(ignore_permissions=True)

	values = {
		"type": "Earning",
		"salary_component_abbr": "LMB",
		"amount_based_on_formula": 1,
		"formula": FORMULA,
		"depends_on_payment_days": 0,
		"is_tax_applicable": 1,
		"round_to_the_nearest_integer": 1,
		"description": "Lembur dari jam (Imogi Payroll Overtime): jam berbobot x Upah / 173.",
	}
	if frappe.db.exists("Salary Component", "Lembur"):
		comp = frappe.get_doc("Salary Component", "Lembur")
		comp.update(values)
		comp.save(ignore_permissions=True)
	else:
		frappe.get_doc({"doctype": "Salary Component", "salary_component": "Lembur", **values}).insert(ignore_permissions=True)

	if frappe.db.exists("Salary Structure", STRUCTURE):
		ss = frappe.get_doc("Salary Structure", STRUCTURE)
		if ss.docstatus == 0 and not any(r.salary_component == "Lembur" for r in ss.earnings):
			ss.append("earnings", {"salary_component": "Lembur", "abbr": "LMB", "amount_based_on_formula": 1, "formula": FORMULA, "depends_on_payment_days": 0})
			ss.save(ignore_permissions=True)
		elif ss.docstatus == 1 and not any(r.salary_component == "Lembur" for r in ss.earnings):
			frappe.log_error(
				"Salary Structure '%s' sudah Submit: tambahkan komponen Lembur lewat revisi/struktur baru." % STRUCTURE,
				"Imogi Payroll: Lembur belum masuk struktur",
			)
