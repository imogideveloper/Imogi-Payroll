# imogi_payroll/override/salary_structure_assignment.py
"""Override tipis Salary Structure Assignment.

Tujuannya BUKAN mengubah perilaku SSA, melainkan menjamin
`apply_component_eval_globals_patch()` sudah dijalankan sebelum SSA
mengevaluasi formula komponen.

Kenapa perlu: `SalaryStructureAssignment._evaluate_component_table()`
memanggil `_safe_eval(formula, COMPONENT_EVAL_GLOBALS.copy(), data)`. Kalau
`get_bpjs_rate`/`get_bpjs_cap` belum terdaftar di dict itu, formula seperti
`base * get_bpjs_rate('bpjs_jht_employee_rate') / 100` gagal dengan
"name 'get_bpjs_rate' is not defined".

Patch-nya juga dipanggil dari `imogi_payroll/__init__.py`, tapi itu saja
tidak cukup: `frappe.get_hooks()` membaca hooks dari cache tanpa meng-import
paket app, sehingga pada worker yang cache-nya sudah panas `__init__.py`
belum tentu pernah dijalankan saat SSA disimpan. Mendaftarkan modul ini
lewat `override_doctype_class` membuat Frappe meng-import-nya tepat saat
controller SSA dimuat - selalu sebelum method apa pun di atas berjalan.
"""

import frappe

from hrms.payroll.doctype.salary_structure_assignment.salary_structure_assignment import (
	SalaryStructureAssignment,
)

from imogi_payroll.component_eval_globals import apply_component_eval_globals_patch

apply_component_eval_globals_patch()


class CustomSalaryStructureAssignment(SalaryStructureAssignment):
	"""Perilaku sama dengan HRMS, plus variabel `bpjs_base` untuk formula."""

	def _get_component_eval_context(self):
		"""Tambahkan `bpjs_base` ke konteks evaluasi formula komponen.

		Di v16 formula Salary Component dievaluasi LEBIH DULU di sini (lewat
		get_evaluated_components), baru hasilnya dipakai Salary Slip. Formula
		potongan BPJS memakai `bpjs_base` (Gaji Pokok + tunjangan tetap), yang
		bukan field bawaan SSA - tanpa penambahan ini formulanya gagal dengan
		"name 'bpjs_base' is not defined" dan seluruh payroll ikut berhenti.
		"""
		data = super()._get_component_eval_context()

		if data.get("bpjs_base") is None:
			from imogi_payroll.payroll.salary_structure_assignment import (
				get_assignment_formula_context,
			)

			ctx = {}
			try:
				ctx = get_assignment_formula_context(self.name) or {}
			except Exception:
				frappe.log_error(
					message=frappe.get_traceback(),
					title="Imogi Payroll: gagal menyusun bpjs_base untuk SSA",
				)

			# Jatuhkan ke `base` kalau tabel komponen belum terisi - lebih baik
			# kurang tunjangan daripada seluruh payroll macet.
			data.bpjs_base = ctx.get("bpjs_base", data.get("base") or 0)

		return data
