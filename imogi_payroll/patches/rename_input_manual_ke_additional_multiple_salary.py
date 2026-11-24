"""Ganti nama DocType "Imogi Payroll Input Manual" (+ Item) menjadi "Additional Multiple Salary" (+ Item).

Dijalankan di [pre_model_sync] supaya tabel dan record DocType sudah bernama baru sebelum file DocType baru
disinkronkan (tanpa ini migrate akan membuat DocType baru yang kosong dan data lama tertinggal).
frappe.rename_doc memindahkan tabel, field Link/Table yang menunjuk DocType ini (mis. Additional
Salary.ref_doctype), dan parenttype baris anak. Tidak menyentuh file (flags.in_patch).

Idempoten, juga merapikan rename yang berhenti di tengah: record DocType sudah bernama baru tetapi tabelnya
masih bernama lama.
"""

import frappe

PASANGAN = (
	("Imogi Payroll Input Manual Item", "Additional Multiple Salary Item"),
	("Imogi Payroll Input Manual", "Additional Multiple Salary"),
)


def execute():
	frappe.flags.in_patch = True
	for lama, baru in PASANGAN:
		if frappe.db.exists("DocType", lama) and not frappe.db.exists("DocType", baru):
			frappe.rename_doc("DocType", lama, baru, force=True)
		elif frappe.db.exists("DocType", baru) and frappe.db.table_exists(lama) and not frappe.db.table_exists(baru):
			frappe.db.rename_table(lama, baru)
	# Rename induk tidak selalu ikut memperbarui parenttype di tabel anak yang sudah lebih dulu diganti namanya.
	if frappe.db.table_exists("Additional Multiple Salary Item"):
		frappe.db.sql(
			"update `tabAdditional Multiple Salary Item` set parenttype=%s where parenttype=%s",
			("Additional Multiple Salary", "Imogi Payroll Input Manual"),
		)
	frappe.db.sql(
		"update `tabAdditional Salary` set ref_doctype=%s where ref_doctype=%s",
		("Additional Multiple Salary", "Imogi Payroll Input Manual"),
	)
	frappe.db.commit()
	frappe.clear_cache()
