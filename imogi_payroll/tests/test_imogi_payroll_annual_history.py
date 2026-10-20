import types
import sys
import types


def test_get_or_create_creates(monkeypatch):
    frappe = sys.modules.get("frappe")

    from imogi_payroll.utils.sync_imogi_payroll_annual_history import (
        get_or_create_imogi_payroll_annual_history,
    )

    employee = types.SimpleNamespace(company="Test Co", employee_name="John Doe")
    monkeypatch.setattr(
        frappe,
        "get_doc",
        lambda dt, name: employee if dt == "Employee" else {},
    )

    doc = get_or_create_imogi_payroll_annual_history(employee_id="EMP001", fiscal_year="2024")
    assert doc.name == "EMP001-2024"
    assert doc.fiscal_year == "2024"
    assert doc.company == "Test Co"
    assert doc.employee_name == "John Doe"


def test_get_or_create_returns_existing(monkeypatch):
    frappe = sys.modules.get("frappe")

    from imogi_payroll.utils.sync_imogi_payroll_annual_history import (
        get_or_create_imogi_payroll_annual_history,
    )

    expected_name = "-".join(["EMP001", "2024"])
    existing = types.SimpleNamespace(name=expected_name)
    monkeypatch.setattr(frappe, "get_doc", lambda dt, name: existing)
    monkeypatch.setattr(
        frappe.db, "get_value", lambda dt, filters, field: expected_name
    )

    doc = get_or_create_imogi_payroll_annual_history(employee_id="EMP001", fiscal_year="2024")
    assert doc is existing
