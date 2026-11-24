"""Isi field Type (Earning / Deduction) Additional Multiple Salary yang sudah ada, dari tipe Salary Component-nya.

Field Type baru ditambahkan; dokumen lama (termasuk yang sudah Submit) masih kosong sehingga kolom Type di list
tidak terisi. Ditulis langsung tanpa mengubah `modified`. Idempoten.
"""

import frappe


def execute():
	frappe.reload_doc("imogi_payroll", "doctype", "additional_multiple_salary")
	frappe.db.sql(
		"""update `tabAdditional Multiple Salary` ams
		join `tabSalary Component` sc on sc.name = ams.salary_component
		set ams.type = sc.type
		where ifnull(ams.type, '') = ''"""
	)
