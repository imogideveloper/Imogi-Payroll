"""Salary Structure otomatis menurut cabang karyawan (tabel "Imogi Payroll Structure Mapping").

Di HRMS struktur slip diambil dari Salary Structure Assignment (SSA), bukan dideteksi saat slip dibuat.
Karena itu pemetaan dipakai saat SSA dibuat: struktur terisi dari cabang karyawan. Odoo memilih struktur
dengan cara yang sama, per batch cabang.
"""

import frappe
from frappe import _


@frappe.whitelist()
def get_structure_for_employee(employee: str | None = None) -> str | None:
	"""Salary Structure menurut cabang karyawan, atau None bila cabang belum dipetakan."""
	if not employee or not frappe.db.exists("DocType", "Imogi Payroll Structure Mapping"):
		return None
	branch = frappe.db.get_value("Employee", employee, "branch")
	if not branch:
		return None
	return frappe.db.get_value("Imogi Payroll Structure Mapping", {"branch": branch}, "salary_structure")


def fill_salary_structure(doc, method=None):
	"""SSA before_validate: isi struktur dari pemetaan bila kosong; bila beda dari pemetaan, beri peringatan
	(tidak memblokir: HR boleh memilih struktur lain dengan sengaja)."""
	mapped = get_structure_for_employee(doc.get("employee"))
	if not mapped:
		return
	if not doc.get("salary_structure"):
		doc.salary_structure = mapped
	elif doc.salary_structure != mapped:
		frappe.msgprint(
			_("Cabang karyawan ini biasanya memakai {0}, tetapi dipilih {1}.").format(mapped, doc.salary_structure),
			indicator="orange",
			alert=True,
		)
