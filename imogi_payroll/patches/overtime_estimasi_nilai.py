"""Isi field "Estimasi Nilai Lembur" (estimated_amount) untuk Overtime yang sudah ada.

Nilai = jam berbobot (dihitung ulang dari jam sesi, tanpa pembulatan) x Gaji Pokok SSA yang berlaku
di tanggal lembur / pembagi. Hanya kolom informasi: ditulis langsung (db_set) tanpa mengubah
`modified` dan tanpa menyentuh status/approval. Idempoten.
"""

import frappe

from imogi_payroll.config.overtime import _exact_weighted_hours, estimate_overtime_amount


def execute():
	frappe.reload_doc("imogi_payroll", "doctype", "overtime")
	rows = frappe.get_all(
		"Overtime",
		filters={"docstatus": ["<", 2]},
		fields=["name", "employee", "overtime_date", "ot1_from", "ot1_to", "ot2_from", "ot2_to", "day_type", "weighted_hours"],
	)
	for r in rows:
		amount = estimate_overtime_amount(r.employee, r.overtime_date, _exact_weighted_hours(r))
		frappe.db.set_value("Overtime", r.name, "estimated_amount", amount, update_modified=False)
