"""Perangkat koreksi absensi oleh HR (kebijakan 16 Nov 2026).

1. Custom field di Attendance: `alasan_input_manual` (Small Text) dan
   `dikonfirmasi_oleh` (Link User, read only, diisi otomatis). Validasinya ada di
   imogi_payroll.override.attendance.validate.
2. Laporan "Koreksi Absensi Manual" (Report Builder, Attendance yang punya alasan input
   manual) untuk dicek atasan atau finance per periode.
3. Setting baru `attendance_backdate_role` (pengecualian darurat) dimuat ulang.

Idempoten: boleh dijalankan berulang.
"""

import json

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

REPORT = "Koreksi Absensi Manual"


def execute():
	frappe.reload_doc("imogi_payroll", "doctype", "imogi_payroll_settings")

	create_custom_fields(
		{
			"Attendance": [
				{
					"fieldname": "alasan_input_manual",
					"label": "Alasan Input Manual",
					"fieldtype": "Small Text",
					"insert_after": "attendance_request",
					"description": "Wajib diisi bila absensi dibuat HR tanpa Employee Checkin (lupa absen).",
				},
				{
					"fieldname": "dikonfirmasi_oleh",
					"label": "Dikonfirmasi Oleh",
					"fieldtype": "Link",
					"options": "User",
					"read_only": 1,
					"insert_after": "alasan_input_manual",
				},
			]
		},
		ignore_validate=True,
	)

	if not frappe.db.exists("Report", REPORT):
		columns = [
			["name", "Attendance"],
			["attendance_date", "Attendance"],
			["employee", "Attendance"],
			["employee_name", "Attendance"],
			["status", "Attendance"],
			["alasan_input_manual", "Attendance"],
			["dikonfirmasi_oleh", "Attendance"],
			["creation", "Attendance"],
			["docstatus", "Attendance"],
		]
		frappe.get_doc(
			{
				"doctype": "Report",
				"report_name": REPORT,
				"ref_doctype": "Attendance",
				"report_type": "Report Builder",
				"is_standard": "No",
				"json": json.dumps(
					{
						"filters": [["Attendance", "alasan_input_manual", "is", "set"]],
						"fields": columns,
						"order_by": "`tabAttendance`.`attendance_date` desc",
						"add_totals_row": 0,
						"page_length": 50,
						"column_widths": {},
						"group_by": None,
					}
				),
				"roles": [{"role": "HR Manager"}, {"role": "HR User"}],
			}
		).insert(ignore_permissions=True)

	frappe.db.commit()
	frappe.clear_cache(doctype="Attendance")
