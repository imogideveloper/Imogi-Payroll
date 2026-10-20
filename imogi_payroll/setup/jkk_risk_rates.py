"""Isi tarif JKK per tingkat risiko di Imogi Payroll Settings.

Besaran mengacu PP Nomor 6 Tahun 2025.

Kenapa perlu fungsi sendiri: Imogi Payroll Settings adalah doctype Single,
dan nilai `default` pada definisi field hanya dipakai saat dokumennya
PERTAMA KALI dibuat. Field yang ditambahkan belakangan tetap kosong di site
yang sudah berjalan, sehingga tarifnya terbaca 0 dan perhitungan diam-diam
jatuh ke tarif cadangan. Fungsi ini mengisi yang masih kosong saja, jadi
aman dipanggil berulang dan tidak akan menimpa angka yang sudah disetel
sendiri oleh pengguna.
"""

import frappe
from frappe.utils import flt

# tingkat risiko -> (fieldname, tarif default %)
JKK_DEFAULT_RATES = {
	"Sangat Rendah": ("bpjs_jkk_rate_sangat_rendah", 0.24),
	"Rendah": ("bpjs_jkk_rate_rendah", 0.54),
	"Sedang": ("bpjs_jkk_rate_sedang", 0.89),
	"Tinggi": ("bpjs_jkk_rate_tinggi", 1.27),
	"Sangat Tinggi": ("bpjs_jkk_rate_sangat_tinggi", 1.74),
}

SETTINGS = "Imogi Payroll Settings"


def setup_jkk_risk_rates() -> None:
	"""Isi tarif JKK yang masih kosong dengan besaran PP 6/2025."""
	meta = frappe.get_meta(SETTINGS)
	terisi = []

	for level, (fieldname, default_rate) in JKK_DEFAULT_RATES.items():
		if not meta.has_field(fieldname):
			# migrate belum menyinkronkan doctype-nya
			continue
		if flt(frappe.db.get_single_value(SETTINGS, fieldname)):
			continue
		frappe.db.set_single_value(SETTINGS, fieldname, default_rate)
		terisi.append(f"{level} = {default_rate}%")

	if terisi:
		frappe.clear_cache(doctype=SETTINGS)
		print("✓ Tarif JKK per risiko diisi: " + ", ".join(terisi))
