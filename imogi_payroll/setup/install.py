import frappe
from .setup_module import setup_payroll_settings
from .salary_components import setup_allowance_components
from .jkk_risk_rates import setup_jkk_risk_rates
from .dashboard import setup_dashboard
from imogi_payroll.patches.set_default_salary_slip_print_format import (
    set_default_salary_slip_print_format,
)

def _setup_dashboard_safely():
    """Kartu & grafik workspace.

    Dibungkus try/except: workspace tanpa kartu hanya tampil kosong,
    sedangkan migrate yang gagal gara-gara ini menghentikan seluruh
    sinkronisasi app.
    """
    try:
        setup_dashboard()
    except Exception:
        frappe.log_error(
            title="Imogi Payroll: gagal menyiapkan dashboard",
            message=frappe.get_traceback(),
        )


def after_install():
    """Run setelah app di-install"""
    print("\n" + "="*60)
    print("Setting up Imogi Payroll...")
    print("="*60 + "\n")

    setup_payroll_settings()
    setup_allowance_components()
    setup_jkk_risk_rates()
    set_default_salary_slip_print_format()
    _setup_dashboard_safely()

    print("\n" + "="*60)
    print("✓ Imogi Payroll setup completed!")
    print("="*60 + "\n")

def after_migrate():
    """Run setelah bench migrate"""
    # Re-apply settings untuk ensure tetap correct
    setup_payroll_settings()
    setup_allowance_components()
    setup_jkk_risk_rates()
    set_default_salary_slip_print_format()
    _setup_dashboard_safely()
