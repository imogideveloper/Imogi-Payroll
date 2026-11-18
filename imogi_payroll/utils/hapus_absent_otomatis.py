"""Hapus Attendance Absent yang dibuat otomatis oleh job harian (bukan input HR).

Ciri record job: status Absent, Submit, dibuat Administrator, tanpa shift, jam masuk/keluar,
cuti, Attendance Request, alasan input manual, dan jam kerja 0. Hanya yang cocok SEMUA ciri
itu yang disentuh. Default dry run: hanya menghitung dan melaporkan.

  bench --site <site> execute imogi_payroll.utils.hapus_absent_otomatis.execute \
      --kwargs "{'dari': '2026-11-16', 'sampai': '2026-11-16'}"          # dry run
  bench --site <site> execute imogi_payroll.utils.hapus_absent_otomatis.execute \
      --kwargs "{'dari': '2026-11-16', 'sampai': '2026-11-16', 'dry_run': 0}"   # hapus

Menolak menghapus bila ada Absent Administrator dalam rentang yang TIDAK cocok ciri job
(kemungkinan input manual), supaya tidak ada yang terhapus tanpa disengaja.
"""

import frappe


def execute(dari: str, sampai: str, dry_run: int = 1) -> dict:
	filters = {
		"attendance_date": ["between", [dari, sampai]],
		"status": "Absent",
		"docstatus": 1,
		"owner": "Administrator",
	}
	rows = frappe.get_all(
		"Attendance",
		filters=filters,
		fields=["name", "shift", "in_time", "out_time", "leave_application", "attendance_request", "alasan_input_manual", "working_hours"],
	)
	job = [
		r for r in rows
		if not (r.shift or r.in_time or r.out_time or r.leave_application or r.attendance_request or r.alasan_input_manual or r.working_hours)
	]
	result = {"kandidat": len(rows), "cocok_ciri_job": len(job), "dihapus": 0, "dry_run": int(bool(int(dry_run)))}
	if len(job) != len(rows):
		result["dibatalkan"] = "ada Absent yang tidak cocok ciri job (kemungkinan manual); tidak ada yang dihapus"
		return result
	if int(dry_run):
		return result
	for r in job:
		doc = frappe.get_doc("Attendance", r.name)
		doc.flags.ignore_permissions = True
		doc.cancel()
		frappe.delete_doc("Attendance", r.name, force=1, ignore_permissions=True)
		result["dihapus"] += 1
	frappe.db.commit()
	return result
