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


IMOGI_PAYROLL_EVAL_GLOBALS = {
	"get_bpjs_rate": get_bpjs_rate,
	"get_bpjs_cap": get_bpjs_cap,
}


def apply_component_eval_globals_patch() -> None:
	"""Tambahkan fungsi kita ke konteks eval, idempoten dan tidak menimpa HRMS."""
	for name, func in IMOGI_PAYROLL_EVAL_GLOBALS.items():
		# setdefault: kalau suatu saat HRMS punya fungsi bernama sama,
		# biarkan punya HRMS yang menang daripada diam-diam kita geser.
		COMPONENT_EVAL_GLOBALS.setdefault(name, func)
