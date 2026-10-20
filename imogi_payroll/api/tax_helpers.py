"""Helper pajak yang dibutuhkan payroll_sync.

Dicabut dari imogi_finance.tax_operations supaya imogi_payroll berdiri
sendiri. Perbedaan dengan aslinya: `_get_tax_profile` TIDAK melempar error
kalau doctype/record "Tax Profile" tidak ada (doctype itu milik modul
finance yang sengaja tidak ikut diport). Pemanggilnya cuma memakai profil
ini untuk mencari akun GL BPJS/PPh21 sebagai pelengkap, jadi tanpa Tax
Profile laporan tetap jalan - hanya angka pembanding dari GL yang kosong.
"""

from __future__ import annotations

from datetime import date

import frappe
from frappe.utils import flt


def _get_gl_total(
    company: str,
    accounts: list[str],
    date_from: date | str | None,
    date_to: date | str | None,
) -> float:
    accounts = [a for a in (accounts or []) if a]
    if not accounts:
        return 0.0

    filters = [
        ["company", "=", company],
        ["is_cancelled", "=", 0],
        ["account", "in", accounts],
    ]

    if date_from and date_to:
        filters.append(["posting_date", "between", [date_from, date_to]])
    elif date_from:
        filters.append(["posting_date", ">=", date_from])
    elif date_to:
        filters.append(["posting_date", "<=", date_to])

    aggregates = frappe.get_all(
        "GL Entry",
        filters=filters,
        fields=["sum(credit) as credit_total", "sum(debit) as debit_total"],
    )
    if not aggregates:
        return 0.0

    return flt(aggregates[0].get("credit_total")) - flt(aggregates[0].get("debit_total"))


def _get_tax_profile(company: str) -> frappe._dict:
    """Tax Profile kalau ada; kalau tidak, dict kosong (bukan error)."""
    if not frappe.db.exists("DocType", "Tax Profile"):
        return frappe._dict()

    profile_name = frappe.db.get_value("Tax Profile", {"company": company}, "name")
    if not profile_name:
        return frappe._dict()

    return frappe.get_cached_doc("Tax Profile", profile_name)
