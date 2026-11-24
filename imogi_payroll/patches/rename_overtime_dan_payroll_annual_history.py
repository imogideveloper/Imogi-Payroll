"""Ganti nama DocType: "Imogi Payroll Overtime" -> "Overtime", "Imogi Payroll Annual History" -> "Payroll Annual History".

[pre_model_sync]: tabel & record DocType sudah bernama baru sebelum file DocType baru disinkronkan. frappe.rename_doc
memindahkan tabel dan memperbarui field Link/Dynamic Link yang menunjuk DocType ini (Workflow, Client Script,
Property Setter, Custom Field, dsb.) serta parenttype baris anak. Child table (Imogi Payroll Annual History Child,
Imogi Payroll Overtime Coefficient) tidak di-rename. Tidak menyentuh file (flags.in_patch). Idempoten, termasuk
merapikan rename yang berhenti di tengah (record sudah bernama baru tetapi tabel masih lama).
"""

import frappe

PASANGAN = (
	("Imogi Payroll Overtime", "Overtime"),
	("Imogi Payroll Annual History", "Payroll Annual History"),
)
CHILD_APH = "Imogi Payroll Annual History Child"


def execute():
	frappe.flags.in_patch = True
	for lama, baru in PASANGAN:
		if frappe.db.exists("DocType", lama) and not frappe.db.exists("DocType", baru):
			frappe.rename_doc("DocType", lama, baru, force=True)
		elif frappe.db.exists("DocType", baru) and frappe.db.table_exists(lama) and not frappe.db.table_exists(baru):
			frappe.db.rename_table(lama, baru)
	if frappe.db.table_exists(CHILD_APH):
		frappe.db.sql(
			f"update `tab{CHILD_APH}` set parenttype=%s where parenttype=%s",
			("Payroll Annual History", "Imogi Payroll Annual History"),
		)
	frappe.db.commit()
	frappe.clear_cache()
