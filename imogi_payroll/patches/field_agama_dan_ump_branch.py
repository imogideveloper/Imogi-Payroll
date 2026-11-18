"""Field Agama di Employee dan UMP Region di Branch.

1. Employee.religion (Select): dipakai memfilter Payroll Entry THR per agama.
   Di Odoo asalnya hr.employee.religion_id.
2. Branch.ump_region (Link ke Imogi Payroll UMP Region): wilayah UMP default tiap
   cabang. Employee.ump_region terisi otomatis dari Branch lewat hook
   override.employee.validate (tetap bisa diubah manual).
3. Isi Branch.ump_region menurut nama cabang, lalu isi Employee.ump_region yang
   masih kosong dari cabangnya. Employee yang sudah punya wilayah tidak disentuh.

Idempoten: boleh dijalankan berulang.
"""

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

RELIGION_OPTIONS = "\nIslam\nKristen\nKatolik\nHindu\nBuddha\nKonghucu"

# Nama cabang -> wilayah UMP (Imogi Payroll UMP Region). Dasarnya nama lokasi
# cabang; HR boleh mengoreksi per cabang atau per karyawan.
BRANCH_UMP = {
	"101 KELAPA GADING": "DKI JAKARTA",
	"109 RAWASARI": "DKI JAKARTA",
	"111 ROXY": "DKI JAKARTA",
	"112 FATMAWATI": "DKI JAKARTA",
	"HEAD OFFICE": "DKI JAKARTA",
	"AIO HO OTOXPERT AUTO2000": "DKI JAKARTA",
	"103 CIATER BARAT": "KOTA TANGERANG SELATAN CIATER",
	"104 KARAWANG": "KARAWANG",
	"105 PETA": "KOTA BANDUNG PETA",
	"106 BOJONGSOANG": "KAB BANDUNG",
	"107 TAMBUN": "KAB BEKASI TAMBUN",
	"108 CIPONDOH": "KOTA TANGERANG CIPONDOH",
	"110 BOGOR": "KOTA BOGOR",
	"003 MEDAN RING": "KOTA MEDAN",
	"004 PADANG": "PADANG",
	"005 PALEMBANG": "KOTA PALEMBANG",
	"302 BALIKPAPAN": "BALIKPAPAN",
	"503 RUNGKUT": "KOTA SURABAYA RUNGKUT",
}


def execute():
	create_custom_fields(
		{
			"Employee": [
				{
					"fieldname": "religion",
					"label": "Religion (Agama)",
					"fieldtype": "Select",
					"options": RELIGION_OPTIONS,
					"insert_after": "number_of_children",
					"description": "Dipakai untuk filter Payroll Entry THR per agama.",
				}
			],
			"Branch": [
				{
					"fieldname": "ump_region",
					"label": "UMP Region (BPJS Basis)",
					"fieldtype": "Link",
					"options": "Imogi Payroll UMP Region",
					"insert_after": "cost_center",
					"description": "Wilayah UMP default karyawan cabang ini; dasar iuran BPJS.",
				}
			],
		},
		ignore_validate=True,
	)

	filled_branch = 0
	for branch, region in BRANCH_UMP.items():
		if not frappe.db.exists("Branch", branch) or not frappe.db.exists("Imogi Payroll UMP Region", region):
			continue
		if not frappe.db.get_value("Branch", branch, "ump_region"):
			frappe.db.set_value("Branch", branch, "ump_region", region, update_modified=False)
			filled_branch += 1

	filled_emp = frappe.db.sql(
		"""
		update `tabEmployee` e
		join `tabBranch` b on b.name = e.branch
		set e.ump_region = b.ump_region
		where ifnull(e.ump_region, '') = '' and ifnull(b.ump_region, '') != ''
		"""
	)
	frappe.db.commit()
	frappe.clear_cache(doctype="Employee")
	frappe.clear_cache(doctype="Branch")
	print(f"field_agama_dan_ump_branch: {filled_branch} cabang terisi wilayah UMP")
