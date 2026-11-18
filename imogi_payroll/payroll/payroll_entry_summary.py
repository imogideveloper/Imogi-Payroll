"""Auto-update ringkasan Payroll Entry (periode, total karyawan, total amount)."""

from __future__ import annotations

import frappe
from frappe.utils import flt, getdate

BULAN_ID = (
	"Jan",
	"Feb",
	"Mar",
	"Apr",
	"Mei",
	"Jun",
	"Jul",
	"Agu",
	"Sep",
	"Okt",
	"Nov",
	"Des",
)


def format_periode_label(start_date=None, end_date=None) -> str:
	"""Label periode list view — bulan gaji dari end_date (pola 25–24)."""
	d = getdate(end_date or start_date) if (end_date or start_date) else None
	if not d:
		return ""
	return f"{BULAN_ID[d.month - 1]} {d.year}"


def update_payroll_entry_summary(payroll_entry, *, persist=True) -> dict:
	"""Hitung ulang periode + agregat slip gaji yang sudah submit."""
	if not payroll_entry:
		return {}

	name = payroll_entry if isinstance(payroll_entry, str) else payroll_entry.name
	if not name or not frappe.db.exists("Payroll Entry", name):
		return {}

	start_date, end_date = frappe.db.get_value(
		"Payroll Entry", name, ["start_date", "end_date"]
	)
	periode = format_periode_label(start_date, end_date)

	slips = frappe.get_all(
		"Salary Slip",
		filters={"payroll_entry": name, "docstatus": 1},
		fields=["net_pay"],
	)
	total_karyawan = len(slips)
	total_amount = sum(flt(s.net_pay) for s in slips)

	summary = {
		"periode": periode,
		"total_karyawan": total_karyawan,
		"total_amount": total_amount,
	}

	if persist:
		frappe.db.set_value("Payroll Entry", name, summary, update_modified=False)
		try:
			from imogi_payroll.payroll.employer_contributions import (
				update_payroll_entry_employer_summary,
			)

			update_payroll_entry_employer_summary(name, persist=True)
		except Exception:
			pass
	else:
		doc = payroll_entry if not isinstance(payroll_entry, str) else None
		if doc:
			doc.periode = periode
			doc.total_karyawan = total_karyawan
			doc.total_amount = total_amount

	return summary


def format_departemen_karyawan(employees) -> str:
	"""Nama departemen unik (urut kemunculan) dari baris tabel Employee Details, dipisah koma.

	Pakai nama departemen tanpa akhiran singkatan perusahaan ("OPERATIONAL", bukan
	"OPERATIONAL - AIO"). Field `department` bawaan di bagian Filter Employees tidak dipakai
	karena itu hanya filter pencarian dan sering kosong.
	"""
	seen = []
	for row in employees or []:
		dept = row.get("department")
		if dept and dept not in seen:
			seen.append(dept)
	names = []
	for dept in seen:
		names.append(frappe.db.get_value("Department", dept, "department_name") or dept)
	return ", ".join(names)


def backfill_departemen_karyawan():
	"""Isi kolom Department untuk Payroll Entry lama yang masih kosong (dipanggil saat after_migrate).

	Dijalankan setelah fixture membuat Custom Field `departemen_karyawan`; Payroll Entry baru terisi otomatis
	saat disimpan. Hanya menyentuh baris yang masih kosong, tanpa mengubah `modified`. Idempoten.
	"""
	if not frappe.db.has_column("Payroll Entry", "departemen_karyawan"):
		return
	kosong = frappe.get_all(
		"Payroll Entry",
		filters={"departemen_karyawan": ["in", ["", None]]},
		pluck="name",
	)
	for name in kosong:
		karyawan = frappe.get_all(
			"Payroll Employee Detail", filters={"parent": name}, fields=["department"], order_by="idx"
		)
		nilai = format_departemen_karyawan(karyawan)
		if nilai:
			frappe.db.set_value("Payroll Entry", name, "departemen_karyawan", nilai, update_modified=False)
	if kosong:
		frappe.db.commit()


def format_cabang_karyawan(employees) -> str:
	"""Nama cabang (Branch) unik dari karyawan di tabel Employee Details (urut kemunculan), dipisah koma.

	Tabel Employee Details tidak menyimpan cabang, jadi diambil dari Employee. Field `branch` bawaan di
	Filter Employees tidak dipakai karena itu hanya filter pencarian dan sering kosong.
	"""
	ids = [row.get("employee") for row in employees or [] if row.get("employee")]
	if not ids:
		return ""
	cabang_per_karyawan = dict(
		frappe.get_all("Employee", filters={"name": ["in", ids]}, fields=["name", "branch"], as_list=True)
	)
	seen = []
	for emp in ids:
		branch = cabang_per_karyawan.get(emp)
		if branch and branch not in seen:
			seen.append(branch)
	return ", ".join(seen)


def backfill_cabang_karyawan():
	"""Isi kolom Branch untuk Payroll Entry lama yang masih kosong (dipanggil saat after_migrate).

	Pola sama dengan backfill_departemen_karyawan: hanya baris kosong, tanpa mengubah `modified`. Idempoten.
	"""
	if not frappe.db.has_column("Payroll Entry", "cabang_karyawan"):
		return
	kosong = frappe.get_all(
		"Payroll Entry",
		filters={"cabang_karyawan": ["in", ["", None]]},
		pluck="name",
	)
	for name in kosong:
		karyawan = frappe.get_all(
			"Payroll Employee Detail", filters={"parent": name}, fields=["employee"], order_by="idx"
		)
		nilai = format_cabang_karyawan(karyawan)
		if nilai:
			frappe.db.set_value("Payroll Entry", name, "cabang_karyawan", nilai, update_modified=False)
	if kosong:
		frappe.db.commit()


def sync_summary_on_validate(doc, method=None):
	"""Isi field ringkasan saat save Payroll Entry."""
	if doc.meta.has_field("departemen_karyawan"):
		doc.departemen_karyawan = format_departemen_karyawan(doc.get("employees"))
	if doc.meta.has_field("cabang_karyawan"):
		doc.cabang_karyawan = format_cabang_karyawan(doc.get("employees"))

	if not doc.get("name") or doc.get("__islocal"):
		doc.periode = format_periode_label(doc.get("start_date"), doc.get("end_date"))
		return

	summary = update_payroll_entry_summary(doc.name, persist=True)
	doc.periode = summary.get("periode", doc.get("periode"))
	doc.total_karyawan = summary.get("total_karyawan", 0)
	doc.total_amount = summary.get("total_amount", 0)


def refresh_summary_from_salary_slip(doc, method=None):
	"""Dipanggil saat Salary Slip submit/cancel."""
	if doc.get("payroll_entry"):
		update_payroll_entry_summary(doc.payroll_entry, persist=True)
		try:
			from imogi_payroll.payroll.employer_contributions import (
				update_payroll_entry_employer_summary,
			)

			update_payroll_entry_employer_summary(doc.payroll_entry, persist=True)
		except Exception:
			pass
