# imogi_payroll/component_eval_globals.py
"""Daftarkan fungsi formula Imogi Payroll ke konteks eval komponen HRMS.

HRMS v16 mengevaluasi condition/formula Salary Component memakai satu dict
tingkat-modul, `hrms.payroll.utils.COMPONENT_EVAL_GLOBALS`, dan ada DUA jalur
yang membacanya:

  * Salary Slip
        salary_slip.py:74 -> self.whitelisted_globals = COMPONENT_EVAL_GLOBALS.copy()
  * Salary Structure Assignment
        salary_structure_assignment.py:433,437 -> _safe_eval(..., COMPONENT_EVAL_GLOBALS.copy(), ...)

Jalur SSA memanggil `_safe_eval` langsung tanpa melewati class yang bisa
kita override, sehingga menyuntik lewat subclass Salary Slip saja tidak
cukup - formula seperti `base * get_bpjs_rate('bpjs_jht_employee_rate') / 100`
gagal dengan "name 'get_bpjs_rate' is not defined" begitu dipakai dari
Salary Structure Assignment. Dict modul di atas adalah satu-satunya titik
yang dilewati kedua jalur.

CATATAN LETAK: modul ini sengaja TIDAK ditaruh di dalam paket `override/`.
`override/__init__.py` meng-import salary_slip, yang meng-import kembali
`imogi_payroll` - kalau patch ini dipanggil dari `imogi_payroll/__init__.py`
sementara paketnya belum selesai diinisialisasi, rantai itu jadi circular
import dan patch-nya gagal diam-diam.

Pembungkus di bawah melakukan import secara lazy karena patch ini dijalankan
saat app di-import (belum ada site context), sedangkan `imogi_payroll.config`
butuh akses database.
"""

from hrms.payroll.utils import COMPONENT_EVAL_GLOBALS


def get_bpjs_rate(fieldname: str) -> float:
	"""Persentase iuran BPJS dari Imogi Payroll Settings."""
	from imogi_payroll.config import get_bpjs_rate as _get_bpjs_rate

	return _get_bpjs_rate(fieldname)


def get_bpjs_cap(fieldname: str) -> float:
	"""Batas atas (cap) nilai iuran dari Imogi Payroll Settings."""
	from imogi_payroll.config import get_bpjs_cap as _get_bpjs_cap

	return _get_bpjs_cap(fieldname)


def get_jkk_rate(employee: str | None = None) -> float:
	"""Tarif JKK (%) menurut tingkat risiko pekerjaan karyawan (PP 6/2025).

	Jatuh kembali ke `bpjs_jkk_rate` bila karyawannya belum diisi tingkat
	risiko - persis seperti yang dijanjikan label field itu di Settings:
	"Cadangan, dipakai hanya kalau Employee belum diisi Risiko Pekerjaan".
	"""
	from imogi_payroll.config import get_jkk_rate as _get_jkk_rate

	return _get_jkk_rate(employee)


def get_bpjs_wage(employee: str | None = None, on_date=None, fallback=0, floor=0) -> float:
	"""Dasar upah iuran BPJS: UMP wilayah karyawan (mengikuti Odoo); tanpa wilayah
	jatuh ke `fallback` dengan lantai `floor`."""
	from imogi_payroll.config.ump import get_bpjs_wage as _get_bpjs_wage

	return _get_bpjs_wage(employee, on_date, fallback, floor)


def get_jp_factor(employee: str | None = None, on_date=None) -> int:
	"""1 = iuran JP berjalan, 0 = usia karyawan melewati batas usia JP (Settings)."""
	from imogi_payroll.config.ump import get_jp_factor as _get_jp_factor

	return _get_jp_factor(employee, on_date)


def get_overtime_amount(employee=None, start_date=None, end_date=None, base=0) -> float:
	"""Nilai lembur periode slip dari jam lembur (Overtime) x base / 173."""
	from imogi_payroll.config.overtime import get_overtime_amount as _get_overtime_amount

	return _get_overtime_amount(employee, start_date, end_date, base)


IMOGI_PAYROLL_EVAL_GLOBALS = {
	"get_bpjs_rate": get_bpjs_rate,
	"get_bpjs_cap": get_bpjs_cap,
	"get_jkk_rate": get_jkk_rate,
	"get_bpjs_wage": get_bpjs_wage,
	"get_jp_factor": get_jp_factor,
	"get_overtime_amount": get_overtime_amount,
}


def apply_component_eval_globals_patch() -> None:
	"""Tambahkan fungsi kita ke konteks eval, idempoten dan tidak menimpa HRMS."""
	for name, func in IMOGI_PAYROLL_EVAL_GLOBALS.items():
		# setdefault: kalau suatu saat HRMS punya fungsi bernama sama,
		# biarkan punya HRMS yang menang daripada diam-diam kita geser.
		COMPONENT_EVAL_GLOBALS.setdefault(name, func)
