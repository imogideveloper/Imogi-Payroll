"""Impor saldo awal pajak (bruto, pengurang netto, PPh 21 per bulan) ke Payroll Annual History.

Dipakai saat pindah dari sistem lain (Odoo): slip bulan-bulan sebelum go-live tidak ada di
ERPNext, padahal perhitungan PPh 21 Desember butuh total bruto dan PPh Januari s/d bulan
terakhir sebelum go-live. Baris yang diimpor TIDAK punya Salary Slip.

File JSON (disiapkan dari sistem lama; berisi data gaji, jangan masuk repo):
  [{"employee": "HR-EMP-00001", "fiscal_year": "2026",
    "months": [{"bulan": 1, "bruto": 6243422.75, "pengurang_netto": 176605.59,
                "biaya_jabatan": 312171.14, "netto": 5754646.02, "pph21": 46826}, ...]}, ...]
`bulan` = bulan akhir periode gaji (periode 21 Des - 20 Jan = 1), sama dengan yang dipakai
sinkronisasi slip. `biaya_jabatan` dan `netto` boleh dikosongkan; dihitung dari bruto.

Jalankan:
  bench --site <site> execute imogi_payroll.utils.import_opening_balance.execute \\
      --kwargs "{'path': '/path/saldo_awal.json'}"

Idempoten: baris bulan yang sama diperbarui. Bulan yang sudah punya baris dari Salary Slip
asli dilewati (tidak ditimpa). Mengembalikan ringkasan.
"""

import json

import frappe
from frappe.utils import flt

from imogi_payroll.utils.aph_month import normalize_bulan
from imogi_payroll.utils.sync_imogi_payroll_annual_history import sync_imogi_payroll_annual_history

BIAYA_JABATAN_BULANAN_MAX = 500_000.0


def _months_with_slip(employee: str, fiscal_year: str) -> set:
	name = frappe.db.get_value(
		"Payroll Annual History", {"employee": employee, "fiscal_year": fiscal_year}, "name"
	)
	if not name:
		return set()
	rows = frappe.get_all(
		"Imogi Payroll Annual History Child",
		filters={"parent": name, "salary_slip": ["is", "set"]},
		fields=["bulan"],
	)
	return {normalize_bulan(r.bulan) for r in rows}


def execute(path: str | None = None, data: list | None = None) -> dict:
	"""`path` = berkas JSON (format di atas), atau `data` = daftar yang sama langsung."""
	if data is None:
		with open(path) as fh:
			data = json.load(fh)

	summary = {"employees": 0, "months_imported": 0, "months_skipped_has_slip": 0, "missing_employee": []}
	for item in data:
		employee, fiscal_year = item["employee"], str(item["fiscal_year"])
		if not frappe.db.exists("Employee", employee):
			summary["missing_employee"].append(employee)
			continue
		has_slip = _months_with_slip(employee, fiscal_year)
		rows = []
		for m in item["months"]:
			bulan = normalize_bulan(m["bulan"])
			if not bulan:
				continue
			if bulan in has_slip:
				summary["months_skipped_has_slip"] += 1
				continue
			bruto = flt(m.get("bruto"))
			pengurang = flt(m.get("pengurang_netto"))
			biaya_jabatan = flt(m.get("biaya_jabatan")) or min(bruto * 0.05, BIAYA_JABATAN_BULANAN_MAX)
			rows.append(
				{
					"bulan": bulan,
					"bruto": bruto,
					"pengurang_netto": pengurang,
					"biaya_jabatan": biaya_jabatan,
					"netto": flt(m.get("netto")) or (bruto - pengurang - biaya_jabatan),
					"pph21": flt(m.get("pph21")),
				}
			)
		if rows:
			sync_imogi_payroll_annual_history(employee, fiscal_year, monthly_results=rows)
			summary["employees"] += 1
			summary["months_imported"] += len(rows)
	frappe.db.commit()
	return summary
