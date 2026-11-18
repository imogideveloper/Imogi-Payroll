"""Validasi koreksi absensi manual oleh HR (kebijakan 16 Nov 2026).

Absensi normal dibuat sistem: dari Employee Checkin (attendance/auto_attendance.py) dan
penanda Absent harian (attendance/daily_attendance.py); keduanya memberi flag
`imogi_system_attendance` sehingga tidak diperiksa di sini.

Selain itu (HR membuat Attendance langsung, atau Attendance dari Attendance Request),
dianggap koreksi dan berlaku:
  - alasan wajib diisi (`alasan_input_manual`),
  - hanya boleh di HARI YANG SAMA (zona waktu Asia/Jakarta): karyawan lapor ke HR HO
    di hari lupa absen, HR menginput hari itu juga. Tanggal mundur ditolak, begitu
    juga tanggal depan, kecuali Attendance dari Attendance Request (rencana WFH/dinas
    boleh tanggal depan, tetap tidak boleh mundur),
  - `dikonfirmasi_oleh` diisi otomatis dengan user yang menyimpan.
User dengan role pada `Imogi Payroll Settings.attendance_backdate_role` (kondisi
darurat) boleh melewati aturan tanggal; alasan tetap wajib dan tercatat di laporan
"Koreksi Absensi Manual". Kosong = tidak ada pengecualian.

Yang diperiksa hanya status Present, Work From Home, dan Half Day pada dokumen baru.
Absent dan On Leave (cuti) tidak diperiksa.
"""

from datetime import datetime
from zoneinfo import ZoneInfo

import frappe
from frappe import _

STATUS_DIKOREKSI = ("Present", "Work From Home", "Half Day")


def _today_jakarta():
	return datetime.now(ZoneInfo("Asia/Jakarta")).date()


def _can_backdate() -> bool:
	if not frappe.get_meta("Imogi Payroll Settings").has_field("attendance_backdate_role"):
		return False
	role = frappe.db.get_single_value("Imogi Payroll Settings", "attendance_backdate_role")
	return bool(role) and role in frappe.get_roles()


def validate(doc, method=None):
	if doc.flags.get("imogi_system_attendance") or not doc.is_new():
		return
	if frappe.flags.in_patch or frappe.flags.in_install or frappe.flags.in_migrate or frappe.flags.in_test:
		return
	if doc.status not in STATUS_DIKOREKSI or doc.get("leave_application"):
		return
	if not frappe.get_meta("Attendance").has_field("alasan_input_manual"):
		return

	from_request = doc.get("attendance_request")
	if not doc.get("alasan_input_manual"):
		if from_request:
			doc.alasan_input_manual = _("Attendance Request {0}").format(from_request)
		else:
			frappe.throw(
				_("Alasan input manual wajib diisi untuk absensi yang dibuat tanpa Employee Checkin."),
				title=_("Koreksi Absensi"),
			)

	attendance_date = frappe.utils.getdate(doc.attendance_date)
	today = _today_jakarta()
	if not _can_backdate():
		if attendance_date < today or (attendance_date > today and not from_request):
			frappe.throw(
				_(
					"Koreksi absensi hanya boleh untuk hari yang sama ({0}). Karyawan harus lapor ke HR di hari "
					"lupa absen; tanggal {1} tidak bisa dikoreksi."
				).format(today.strftime("%d-%m-%Y"), attendance_date.strftime("%d-%m-%Y")),
				title=_("Koreksi Absensi"),
			)

	doc.dikonfirmasi_oleh = frappe.session.user
