"""Hitungan lembur dari jam (mengikuti Odoo `altech_overtime_indonesia`).

Nilai lembur = jam berbobot x Upah / pembagi (173).
Jam berbobot = jumlah (pengali jam ke-i x jam yang terpakai di jam ke-i); jam pecahan
dihitung proporsional. Pengali tergantung jenis hari. Tabel pengali bisa diubah di
tab "Overtime" pada "Imogi Payroll Settings"; bila kosong dipakai nilai bawaan Odoo di bawah.
"""

import frappe
from frappe.utils import flt

DAY_TYPES = ("Workday", "Offday (5)", "Holiday (5)", "Offday (6)", "Public Holiday (6)")
DEFAULT_DIVISOR = 173.0
DEFAULT_COEFFICIENTS = {
	"Workday": [1.5, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
	"Offday (5)": [2, 2, 2, 2, 2, 2, 2, 2, 3, 4, 4],
	"Holiday (5)": [2, 2, 2, 2, 2, 2, 2, 2, 3, 4, 4],
	"Offday (6)": [2, 2, 2, 2, 2, 2, 2, 3, 4, 4, 4],
	"Public Holiday (6)": [2, 2, 2, 2, 2, 3, 4, 4, 4, 4, 4],
}


def _settings():
	# Pengaturan lembur ada di tab "Overtime" pada Imogi Payroll Settings
	# (dulu doctype terpisah "Imogi Payroll Overtime Settings").
	try:
		return frappe.get_cached_doc("Imogi Payroll Settings")
	except Exception:
		return None


def get_divisor() -> float:
	s = _settings()
	return flt(s.get("overtime_divisor")) if s and flt(s.get("overtime_divisor")) > 0 else DEFAULT_DIVISOR


def get_coefficients(day_type: str) -> list:
	s = _settings()
	if s:
		for row in s.get("overtime_coefficients") or []:
			if row.day_type == day_type:
				return [flt(row.get("jam_%d" % i)) for i in range(1, 12)]
	return list(DEFAULT_COEFFICIENTS.get(day_type or "Workday", DEFAULT_COEFFICIENTS["Workday"]))


def weighted_hours(hours: float, day_type: str) -> float:
	"""Jam berbobot untuk `hours` jam lembur di hari berjenis `day_type`."""
	table = get_coefficients(day_type)
	total, remaining, i = 0.0, flt(hours), 0
	while remaining > 1e-9:
		total += table[min(i, 10)] * min(1.0, remaining)
		remaining -= 1.0
		i += 1
	return total


def get_base_for_date(employee, date) -> float:
	"""Gaji Pokok (variabel `base` formula slip) dari SSA Submit yang berlaku di tanggal itu.

	Bila belum ada SSA yang mulai sebelum tanggal itu (mis. SSA kontrak baru mulai di tengah
	periode), pakai SSA terdekat sesudahnya, karena slip periode itu juga memakai SSA tersebut."""
	if not employee or not date:
		return 0.0
	ssa = frappe.db.get_value(
		"Salary Structure Assignment",
		{"employee": employee, "docstatus": 1, "from_date": ["<=", date]},
		"name",
		order_by="from_date desc, creation desc",
	) or frappe.db.get_value(
		"Salary Structure Assignment",
		{"employee": employee, "docstatus": 1, "from_date": [">", date]},
		"name",
		order_by="from_date asc, creation desc",
	)
	if not ssa:
		return 0.0
	from imogi_payroll.payroll.salary_structure_assignment import get_assignment_formula_context

	return flt(get_assignment_formula_context(ssa).get("base"))


def estimate_overtime_amount(employee, date, weighted) -> float:
	"""Estimasi nilai lembur satu hari = jam berbobot x Gaji Pokok / pembagi (seperti
	"Estimasi Nilai OT" di Odoo). Hanya informasi; nilai di slip tetap dari get_overtime_amount."""
	base = get_base_for_date(employee, date)
	return flt(flt(weighted) * base / get_divisor(), 2) if base else 0.0


def get_overtime_amount(employee=None, start_date=None, end_date=None, base=0) -> float:
	"""Nilai lembur satu periode slip = jam berbobot (lembur yang sudah Submit) x base / pembagi.

	Dipakai sebagai formula komponen gaji "Lembur":
	get_overtime_amount(employee, start_date, end_date, base)
	"""
	if not employee or not start_date or not end_date or not flt(base):
		return 0.0
	rows = frappe.db.sql(
		"""select ot1_from, ot1_to, ot2_from, ot2_to, day_type, weighted_hours
		from `tabOvertime`
		where employee = %s and docstatus = 1 and overtime_date between %s and %s""",
		(employee, start_date, end_date),
		as_dict=True,
	)
	total = sum(_exact_weighted_hours(r) for r in rows)
	return flt(total) * flt(base) / get_divisor()


def _exact_weighted_hours(row) -> float:
	"""Jam berbobot satu hari lembur dihitung ulang dari jam mulai/selesai, tanpa pembulatan.

	Field weighted_hours disimpan 2 desimal (2 jam 50 menit -> 5,1667 tersimpan 5,17); kalau
	angka bulat itu yang dijumlah, nilai lembur selisih beberapa rupiah dari Odoo, yang
	menghitung dengan angka penuh. Tanpa jam sesi (data lama), pakai nilai tersimpan."""
	from frappe.utils import time_diff_in_hours

	hours = 0.0
	for a, b in ((row.ot1_from, row.ot1_to), (row.ot2_from, row.ot2_to)):
		if a and b:
			hours += max(time_diff_in_hours(b, a), 0.0)
	if hours <= 0:
		return flt(row.weighted_hours)
	return weighted_hours(hours, row.day_type)
