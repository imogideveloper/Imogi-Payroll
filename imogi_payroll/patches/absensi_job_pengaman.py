"""Pengaman job harian absensi (imogi_payroll.attendance.daily_attendance).

Job lama menandai Absent semua karyawan aktif tiap hari kerja, walau belum ada shift,
belum ada Employee Checkin, dan belum ada keputusan HR; di lokal membuat 82 Attendance Absent
dalam sekali jalan (2026-11-17). Sekarang job hanya berjalan bila
`Imogi Payroll Settings.auto_mark_absent_enabled` dicentang (default mati), dan hanya untuk
karyawan ber-shift dengan Auto Attendance menyala (lihat docstring job).

Patch ini memuat field baru dan memastikan nilainya 0 (mati) bila belum pernah diatur. Idempoten.
Untuk membersihkan Absent otomatis yang sudah telanjur ada: utils/hapus_absent_otomatis.py.
"""

import frappe


def execute():
	frappe.reload_doc("imogi_payroll", "doctype", "imogi_payroll_settings")
	if frappe.db.get_single_value("Imogi Payroll Settings", "auto_mark_absent_enabled") in (None, ""):
		frappe.db.set_single_value("Imogi Payroll Settings", "auto_mark_absent_enabled", 0)
	frappe.db.commit()
