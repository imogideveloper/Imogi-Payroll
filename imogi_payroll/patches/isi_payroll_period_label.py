"""Isi field "Payroll Period" (payroll_sub_period) untuk Salary Slip, Additional Salary, Additional Multiple Salary,
dan Overtime yang sudah ada (field baru; dokumen baru terisi lewat doc_events before_validate).

Label diambil dari baris cutoff Payroll Period yang memuat tanggal dokumen (Salary Slip: end_date, Additional
Salary / Additional Multiple Salary: payroll_date, Overtime: overtime_date). Ditulis langsung tanpa mengubah
`modified`; dokumen yang sudah Submit/Cancel ikut diisi (kolom informasi saja). Idempoten.
"""

import frappe

from imogi_payroll.payroll.payroll_period_integration import PAYROLL_PERIOD_DATE_FIELD, get_payroll_period_label


def execute():
	for doctype in ("Additional Multiple Salary", "Overtime"):
		frappe.reload_doc("imogi_payroll", "doctype", frappe.scrub(doctype))
	for doctype, date_field in PAYROLL_PERIOD_DATE_FIELD.items():
		if not frappe.db.has_column(doctype, "payroll_sub_period"):
			continue
		meta = frappe.get_meta(doctype)
		fields = ["name", date_field]
		if meta.has_field("company"):
			fields.append("company")
		if meta.has_field("employee"):
			fields.append("employee")
		if doctype == "Additional Salary":
			fields.append("from_date")
		cache = {}
		for r in frappe.get_all(doctype, fields=fields, filters={"payroll_sub_period": ["is", "not set"]}):
			company = r.get("company") or (frappe.db.get_value("Employee", r.employee, "company") if r.get("employee") else None)
			tanggal = r.get(date_field) or r.get("from_date")
			kunci = (str(tanggal), company)
			if kunci not in cache:
				cache[kunci] = get_payroll_period_label(tanggal, company)
			if cache[kunci]:
				frappe.db.set_value(doctype, r.name, "payroll_sub_period", cache[kunci], update_modified=False)
	frappe.db.commit()
