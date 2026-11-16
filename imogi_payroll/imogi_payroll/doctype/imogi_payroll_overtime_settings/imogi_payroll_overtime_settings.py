import frappe
from frappe import _
from frappe.model.document import Document


class ImogiPayrollOvertimeSettings(Document):
	def validate(self):
		seen = set()
		for row in self.coefficients or []:
			if row.day_type in seen:
				frappe.throw(_("Jenis hari {0} muncul lebih dari sekali di tabel koefisien.").format(row.day_type))
			seen.add(row.day_type)
