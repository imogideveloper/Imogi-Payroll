__version__ = "1.0.0"

import frappe

try:
    from imogi_payroll.override.salary_slip_cutoff_patch import (
        apply_salary_slip_cutoff_patch,
    )

    apply_salary_slip_cutoff_patch()
except Exception:
    # Keep app import safe during install/build; Frappe will surface real errors at runtime.
    pass

try:
    # get_bpjs_rate()/get_bpjs_cap() dipakai formula Salary Component, dan
    # harus tersedia di SEMUA jalur eval - termasuk Salary Structure
    # Assignment yang memanggil _safe_eval langsung tanpa lewat class
    # Salary Slip kita.
    from imogi_payroll.component_eval_globals import (
        apply_component_eval_globals_patch,
    )

    apply_component_eval_globals_patch()
except Exception:
    # Jangan ditelan diam-diam: kalau patch ini gagal, formula BPJS akan
    # error "name 'get_bpjs_rate' is not defined" jauh di kemudian hari dan
    # sangat sulit dilacak balik ke sini. log_error butuh site context yang
    # belum tentu ada saat app di-import, jadi tulis ke stderr (masuk log bench).
    import traceback

    traceback.print_exc()


def _patch_salary_slip_globals():
    """Fungsi formula tambahan untuk konteks eval Salary Slip.

    Sumbernya sekarang satu: IMOGI_PAYROLL_EVAL_GLOBALS, yang juga dipakai
    untuk menambal COMPONENT_EVAL_GLOBALS di atas. Dulu fungsi ini membaca
    hook `salary_slip_globals`, tapi hook itu karangan sendiri - tidak ada
    yang membacanya selain kode ini - dan hanya menjangkau Salary Slip,
    sehingga Salary Structure Assignment tetap error.
    """
    from imogi_payroll.component_eval_globals import IMOGI_PAYROLL_EVAL_GLOBALS

    return dict(IMOGI_PAYROLL_EVAL_GLOBALS)
