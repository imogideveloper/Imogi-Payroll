"""Payroll Entry: Start Date / End Date tidak wajib (tetap disembunyikan).

Kedua field bawaan HRMS itu disembunyikan (Property Setter "-hidden") karena selalu diisi dari Payroll Period
(bulan gaji). Field wajib yang disembunyikan tanpa default ditolak Frappe (HiddenAndMandatoryWithoutDefaultError)
setiap kali meta Payroll Entry divalidasi, mis. saat fixture Custom Field diimpor waktu migrate. Dijalankan di
[pre_model_sync] supaya Property Setter "-reqd" sudah ada sebelum fixture diimpor. Tanggal tetap diisi oleh
payroll_period_integration.fill_dates_from_sub_period (before_validate). Idempoten.
"""

import frappe
from frappe.custom.doctype.property_setter.property_setter import make_property_setter


def execute():
	for fieldname in ("start_date", "end_date"):
		make_property_setter("Payroll Entry", fieldname, "reqd", "0", "Check", validate_fields_for_doctype=False)
	frappe.clear_cache(doctype="Payroll Entry")
