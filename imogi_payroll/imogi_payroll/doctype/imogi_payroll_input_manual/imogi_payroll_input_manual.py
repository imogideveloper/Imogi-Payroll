import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class ImogiPayrollInputManual(Document):
	"""Input massal Additional Salary: satu dokumen = satu komponen gaji, satu tanggal payroll,
	banyak karyawan (padanan "Input Manual" per kategori per cutoff di Odoo).

	Saat Submit, tiap baris dibuat dan di-Submit sebagai Additional Salary; saat Cancel,
	Additional Salary itu ikut dibatalkan."""

	def validate(self):
		if not self.company:
			self.company = frappe.defaults.get_user_default("Company") or frappe.defaults.get_global_default("company")
		if not self.items:
			frappe.throw(_("Isi minimal satu karyawan."))
		if frappe.db.get_value("Salary Component", self.salary_component, "statistical_component"):
			frappe.throw(_("Komponen statistik tidak bisa dipakai di input manual."))
		seen = set()
		for row in self.items:
			if row.employee in seen:
				frappe.throw(_("Baris {0}: karyawan {1} muncul dua kali.").format(row.idx, row.employee))
			seen.add(row.employee)
			if flt(row.amount) <= 0:
				frappe.throw(_("Baris {0}: nilai harus lebih dari 0.").format(row.idx))
			status = frappe.db.get_value("Employee", row.employee, "status")
			if status != "Active":
				frappe.throw(_("Baris {0}: karyawan {1} tidak aktif.").format(row.idx, row.employee))

	def on_submit(self):
		for row in self.items:
			additional_salary = frappe.get_doc(
				{
					"doctype": "Additional Salary",
					"employee": row.employee,
					"company": self.company,
					"salary_component": self.salary_component,
					"amount": row.amount,
					"payroll_date": self.payroll_date,
					"ref_doctype": self.doctype,
					"ref_docname": self.name,
				}
			)
			additional_salary.insert(ignore_permissions=True)
			additional_salary.submit()
			frappe.db.set_value("Imogi Payroll Input Manual Item", row.name, "additional_salary", additional_salary.name)

	def on_cancel(self):
		for row in self.items:
			if not row.additional_salary:
				continue
			additional_salary = frappe.get_doc("Additional Salary", row.additional_salary)
			if additional_salary.docstatus == 1:
				additional_salary.cancel()
