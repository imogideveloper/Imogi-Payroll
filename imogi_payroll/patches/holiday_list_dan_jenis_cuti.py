"""Holiday List nasional (2024-2026) + 12 jenis cuti Odoo.

- Holiday List "Libur Nasional <tahun>": Minggu libur mingguan + libur nasional/cuti bersama dari
  setup/default_holidays.json (2024-2025 dari Odoo, 2026 dari SKB 3 Menteri; Odoo tidak punya 2026).
- Holiday List Assignment tingkat Company per tahun (karyawan tanpa assignment sendiri memakainya).
- Jenis cuti dari setup/default_leave_types.json (nama mengikuti Odoo). Tidak memotong gaji (bukan LWP).
Idempoten: hanya menambah yang belum ada.
"""

import json
import os

import frappe


def _load(name):
	with open(os.path.join(frappe.get_app_path("imogi_payroll"), "setup", name)) as fh:
		return json.load(fh)


def _holiday_lists():
	data = _load("default_holidays.json")
	companies = frappe.get_all("Company", pluck="name")
	for year, days in sorted(data["years"].items()):
		name = "Libur Nasional %s" % year
		if not frappe.db.exists("Holiday List", name):
			hl = frappe.new_doc("Holiday List")
			hl.holiday_list_name = name
			hl.from_date = "%s-01-01" % year
			hl.to_date = "%s-12-31" % year
			hl.weekly_off = data.get("weekly_off", "Sunday")
			for d in days:
				hl.append("holidays", {"holiday_date": d["date"], "description": d["name"], "weekly_off": 0})
			hl.get_weekly_off_dates()
			hl.insert(ignore_permissions=True)
		for company in companies:
			if frappe.db.exists(
				"Holiday List Assignment",
				{"applicable_for": "Company", "assigned_to": company, "holiday_list": name, "docstatus": ["<", 2]},
			):
				continue
			a = frappe.get_doc(
				{
					"doctype": "Holiday List Assignment",
					"applicable_for": "Company",
					"assigned_to": company,
					"holiday_list": name,
					"from_date": "%s-01-01" % year,
				}
			)
			a.insert(ignore_permissions=True)
			a.submit()


def _leave_types():
	for lt in _load("default_leave_types.json"):
		if frappe.db.exists("Leave Type", lt["name"]):
			continue
		frappe.get_doc(
			{
				"doctype": "Leave Type",
				"leave_type_name": lt["name"],
				"max_leaves_allowed": lt.get("max_leaves_allowed", 0),
				"allow_negative": lt.get("allow_negative", 0),
				"is_compensatory": lt.get("is_compensatory", 0),
				"is_lwp": 0,
				"include_holiday": 0,
				"is_carry_forward": 0,
			}
		).insert(ignore_permissions=True)


def execute():
	_holiday_lists()
	_leave_types()
