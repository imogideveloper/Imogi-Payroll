"""Pasang Client Script baris total Monthly Detail (cadangan jika doctype_js cache)."""

from pathlib import Path

import frappe

SCRIPT_NAME = "APH Monthly Detail Totals"


def execute():
	script_path = Path(
		frappe.get_app_path("imogi_payroll", "public", "js", "aph_monthly_totals_client.js")
	)
	if not script_path.exists():
		return

	script = script_path.read_text(encoding="utf-8")

	if frappe.db.exists("Client Script", SCRIPT_NAME):
		doc = frappe.get_doc("Client Script", SCRIPT_NAME)
		doc.script = script
		doc.enabled = 1
		doc.module = "Imogi Payroll"
		doc.save(ignore_permissions=True)
	else:
		frappe.get_doc(
			{
				"doctype": "Client Script",
				"name": SCRIPT_NAME,
				"dt": "Imogi Payroll Annual History",
				"view": "Form",
				"enabled": 1,
				"module": "Imogi Payroll",
				"script": script,
			}
		).insert(ignore_permissions=True)

	frappe.db.commit()
