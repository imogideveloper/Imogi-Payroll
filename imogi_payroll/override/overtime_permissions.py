"""Izin akses Imogi Payroll Overtime untuk atasan penyetuju.

Hook has_permission Frappe hanya boleh menolak: nilai kosong (None) dianggap menolak, jadi
fungsi ini harus mengembalikan True untuk mengizinkan.

Role "Employee" diberi read/write di DocType supaya atasan bisa membuka dan menyetujui
lembur lewat workflow. Aturan di sini membatasi: user non-HR hanya melihat lembur yang
`overtime_approver`-nya dirinya, dan hanya boleh menyimpan (write) saat statusnya
"Pending Atasan". HR (HR User, HR Manager, System Manager) mengikuti izin DocType biasa.
"""

import frappe

HR_ROLES = {"HR Manager", "HR User", "System Manager"}


def _is_hr(user: str) -> bool:
	return user == "Administrator" or bool(HR_ROLES & set(frappe.get_roles(user)))


def get_permission_query_conditions(user=None):
	user = user or frappe.session.user
	if _is_hr(user):
		return ""
	return f"`tabImogi Payroll Overtime`.`overtime_approver` = {frappe.db.escape(user)}"


def has_permission(doc, ptype=None, user=None, **kwargs):
	user = user or frappe.session.user
	if _is_hr(user):
		return True
	if doc.get("overtime_approver") != user:
		return False
	if ptype in ("create", "delete", "submit", "cancel", "amend"):
		return False
	if ptype == "write":
		# Pakai status yang tersimpan: saat workflow berjalan, dokumen di memori sudah berisi
		# status tujuan (mis. "Pending HR") sebelum disimpan.
		stored = frappe.db.get_value(doc.doctype, doc.name, "workflow_state") if doc.name else None
		if stored != "Pending Atasan":
			return False
	return True
