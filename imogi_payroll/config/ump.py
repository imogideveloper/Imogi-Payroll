"""UMP/UMK per wilayah - dasar iuran BPJS (mengikuti Odoo).

Di Odoo, seluruh iuran BPJS (JHT, JP, JKK, JKM, Kesehatan) dihitung dari UMP
wilayah yang tercatat di kontrak karyawan untuk tahun pajak slip, bukan dari
gaji. Karena itu Employee punya field `ump_region` (Link ke
Imogi Payroll UMP Region) dan tiap wilayah menyimpan nilai UMP per tahun.
"""

import frappe
from frappe.utils import cint, flt, getdate, nowdate


def _employee_has_ump_field() -> bool:
	return bool(frappe.get_meta("Employee").has_field("ump_region"))


def _ump_of_region(region: str | None, on_date=None) -> float:
	"""UMP wilayah `region` untuk tahun `on_date`; tahun belum ada -> tahun terdekat sebelumnya."""
	if not region:
		return 0.0
	year = cint(getdate(on_date or nowdate()).year)
	rows = frappe.get_all(
		"Imogi Payroll UMP Year",
		filters={"parent": region, "parenttype": "Imogi Payroll UMP Region", "year": ["<=", year]},
		fields=["year", "amount"],
		order_by="year desc",
		limit=1,
	)
	return flt(rows[0].amount) if rows else 0.0


def get_default_ump(on_date=None) -> float:
	"""UMP wilayah default (Imogi Payroll Settings.default_ump_region); 0 bila belum diatur."""
	if not frappe.get_meta("Imogi Payroll Settings").has_field("default_ump_region"):
		return 0.0
	region = frappe.db.get_single_value("Imogi Payroll Settings", "default_ump_region")
	return _ump_of_region(region, on_date)


def get_jp_factor(employee: str | None, on_date=None) -> int:
	"""1 bila karyawan masih kena iuran JP, 0 bila usianya (pada `on_date`) sudah mencapai
	usia pensiun `bpjs_jp_max_age` (usia di bawahnya masih kena). Tanpa tanggal lahir atau
	batas usia, tetap 1 (iuran JP berjalan)."""
	if not employee or not frappe.get_meta("Imogi Payroll Settings").has_field("bpjs_jp_max_age"):
		return 1
	max_age = cint(frappe.db.get_single_value("Imogi Payroll Settings", "bpjs_jp_max_age"))
	dob = frappe.db.get_value("Employee", employee, "date_of_birth")
	if not max_age or not dob:
		return 1
	dob, today = getdate(dob), getdate(on_date or nowdate())
	age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
	return 0 if age >= max_age else 1


def get_ump(employee: str | None, on_date=None) -> float:
	"""UMP wilayah karyawan untuk tahun `on_date` (default hari ini).

	Mengembalikan 0 bila karyawan belum diisi wilayahnya atau wilayah itu belum
	punya nilai UMP. Kalau tahunnya belum ada, dipakai tahun terdekat sebelumnya
	(lebih aman daripada iuran 0 yang lolos tanpa terlihat).
	"""
	if not employee or not _employee_has_ump_field():
		return 0.0
	region = frappe.db.get_value("Employee", employee, "ump_region")
	if not region:
		return 0.0
	year = cint(getdate(on_date or nowdate()).year)
	rows = frappe.get_all(
		"Imogi Payroll UMP Year",
		filters={"parent": region, "parenttype": "Imogi Payroll UMP Region", "year": ["<=", year]},
		fields=["year", "amount"],
		order_by="year desc",
		limit=1,
	)
	return flt(rows[0].amount) if rows else 0.0


def get_bpjs_wage(employee: str | None, on_date=None, fallback=0, floor=0) -> float:
	"""Dasar upah iuran BPJS: UMP wilayah karyawan; kalau tidak ada, UMP wilayah default
	(Imogi Payroll Settings, mengikuti Odoo); kalau itu juga belum diatur, `fallback`
	(dengan lantai `floor` bila diberikan) seperti perilaku sebelumnya."""
	ump = get_ump(employee, on_date)
	if ump > 0:
		return ump
	default_ump = get_default_ump(on_date)
	if default_ump > 0:
		return default_ump
	return max(flt(fallback), flt(floor))
