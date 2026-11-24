"""Pengaturan lembur dipindah ke tab "Overtime" di Imogi Payroll Settings.

Dulu ada doctype Single terpisah "Imogi Payroll Overtime Settings" (pembagi + tabel koefisien).
Patch ini:
1. Menyalin pembagi dan baris koefisien lama ke Imogi Payroll Settings
   (field overtime_divisor / overtime_coefficients), hanya bila tab Overtime masih kosong.
   Bila data lama tidak ada, diisi nilai bawaan Odoo.
2. Menghapus doctype lama "Imogi Payroll Overtime Settings" beserta baris koefisien yatimnya.
Child table "Imogi Payroll Overtime Coefficient" tetap dipakai. Idempoten.
"""

import frappe
from frappe.utils import flt

from imogi_payroll.config.overtime import DEFAULT_COEFFICIENTS, DEFAULT_DIVISOR

OLD = "Imogi Payroll Overtime Settings"
CHILD = "Imogi Payroll Overtime Coefficient"
JAM = ["jam_%d" % i for i in range(1, 12)]


def execute():
	frappe.reload_doc("imogi_payroll", "doctype", "imogi_payroll_overtime_coefficient")
	frappe.reload_doc("imogi_payroll", "doctype", "imogi_payroll_settings")

	settings = frappe.get_single("Imogi Payroll Settings")
	if not settings.get("overtime_coefficients"):
		old_rows = frappe.get_all(
			CHILD,
			filters={"parenttype": OLD, "parent": OLD},
			fields=["day_type"] + JAM,
			order_by="idx",
		)
		old_divisor = frappe.db.sql("select value from `tabSingles` where doctype=%s and field='divisor'", OLD)
		old_divisor = flt(old_divisor[0][0]) if old_divisor else 0
		settings.overtime_divisor = old_divisor if old_divisor > 0 else DEFAULT_DIVISOR
		if old_rows:
			for r in old_rows:
				settings.append("overtime_coefficients", {"day_type": r.day_type, **{f: flt(r.get(f)) for f in JAM}})
		else:
			for day_type, table in DEFAULT_COEFFICIENTS.items():
				settings.append("overtime_coefficients", {"day_type": day_type, **dict(zip(JAM, table))})
		settings.save(ignore_permissions=True)

	# Hapus doctype lama + data yatimnya (nilainya sudah tersalin di atas).
	frappe.db.delete(CHILD, {"parenttype": OLD})
	frappe.db.delete("Singles", {"doctype": OLD})
	if frappe.db.exists("DocType", OLD):
		frappe.delete_doc("DocType", OLD, force=True, ignore_missing=True)
	frappe.clear_cache()
