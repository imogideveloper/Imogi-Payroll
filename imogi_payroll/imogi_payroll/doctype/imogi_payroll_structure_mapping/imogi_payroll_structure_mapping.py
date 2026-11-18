import frappe
from frappe import _
from frappe.model.document import Document


class ImogiPayrollStructureMapping(Document):
	"""Aturan: cabang -> Salary Structure (mengikuti Odoo: struktur dipilih per batch cabang,
	Head Office memakai Tax Gross, cabang operasional memakai Regular)."""

	def validate(self):
		if frappe.db.get_value("Salary Structure", self.salary_structure, "docstatus") != 1:
			frappe.throw(_("Salary Structure {0} harus sudah di-Submit.").format(self.salary_structure))
