"""Pengaman patch untuk situs lain yang memakai app imogi_payroll yang sama.

Beberapa patch mengubah perilaku, bukan hanya menambah data: rumus komponen BPJS, batas upah,
format cetak slip default, struktur gaji, dan sebagainya. Patch seperti itu hanya boleh jalan di situs
Otoexpert; di situs lain dilewati (tercatat selesai di Patch Log).
"""

import frappe

OTOEXPERT_COMPANY = "ASTRA INOVASI OTOMOTIF"


def is_otoexpert_site() -> bool:
	return bool(frappe.db.exists("Company", OTOEXPERT_COMPANY))
