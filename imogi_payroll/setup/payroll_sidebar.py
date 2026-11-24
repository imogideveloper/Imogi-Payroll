"""Susun sidebar "Payroll" bawaan HRMS mengikuti alur pembentukan slip gaji (dipanggil saat after_migrate).

Sidebar "Payroll" adalah record standar milik HRMS (hrms/workspace_sidebar/payroll.json) dan bisa ditulis ulang
saat HRMS diperbarui, jadi susunan Otoexpert dipasang ulang di sini setiap migrate (idempoten):

  Home, Dashboard, Salary Structure Assignment
  Monthly Input : Overtime, Additional Multiple Salary, Additional Salary, Salary Withholding
  Payroll Run   : Payroll Entry, Salary Slip
  Reports       : Payroll Annual History + laporan bawaan HRMS
  Setup         : Salary Component, Salary Structure, Payroll Period
  Settings

Menu lain yang ada di sidebar tetapi tidak disebut di sini tetap dipertahankan (ditaruh sebelum Settings).
Tidak mengekspor ke file HRMS (flags.in_import).
"""

import frappe

SIDEBAR = "Payroll"


def _link(label, link_to, link_type="DocType", icon=None, child=0):
	return {
		"type": "Link", "label": label, "link_to": link_to, "link_type": link_type, "icon": icon or "",
		"child": child, "indent": 0, "collapsible": 1, "keep_closed": 0, "show_arrow": 0,
	}


def _section(label, icon, keep_closed=1):
	return {
		"type": "Section Break", "label": label, "link_type": "DocType", "icon": icon,
		"child": 0, "indent": 1, "collapsible": 1, "keep_closed": keep_closed, "show_arrow": 0,
	}


def _susunan():
	return [
		_link("Home", "Payroll", "Workspace", "home"),
		_link("Dashboard", "Payroll", "Dashboard", "layout-dashboard"),
		_link("Salary Structure Assignment", "Salary Structure Assignment", icon="loan"),
		_section("Monthly Input", "calendar", keep_closed=0),
		_link("Overtime", "Overtime", child=1),
		_link("Additional Multiple Salary", "Additional Multiple Salary", child=1),
		_link("Additional Salary", "Additional Salary", child=1),
		_link("Salary Withholding", "Salary Withholding", child=1),
		_section("Payroll Run", "banknote-arrow-up", keep_closed=0),
		_link("Payroll Entry", "Payroll Entry", child=1),
		_link("Salary Slip", "Salary Slip", child=1),
		_section("Reports", "notepad-text"),
		_link("Payroll Annual History", "Payroll Annual History", child=1),
		_link("Employee CTC Break-up", "Employee CTC Break-up", "Report", child=1),
		_link("Salary Register", "Salary Register", "Report", child=1),
		_link("Income Tax Deductions", "Income Tax Deductions", "Report", child=1),
		_link("Professional Tax Deductions", "Professional Tax Deductions", "Report", child=1),
		_link("General Ledger", "General Ledger", "Report", child=1),
		_link("Accounts Payable", "Accounts Payable", "Report", child=1),
		_section("Setup", "database"),
		_link("Salary Component", "Salary Component", child=1),
		_link("Salary Structure", "Salary Structure", child=1),
		_link("Payroll Period", "Payroll Period", child=1),
		_link("Settings", "Payroll Settings", icon="settings"),
	]


def _ada(item):
	"""Link hanya dipasang bila target-nya ada di situs ini."""
	if item["type"] != "Link":
		return True
	lt, target = item["link_type"], item["link_to"]
	if lt in ("DocType", "Report", "Workspace", "Dashboard"):
		return bool(frappe.db.exists(lt, target))
	return True


def _kunci(r):
	return (r.get("type"), r.get("label"), r.get("link_type") if r.get("type") == "Link" else None, r.get("link_to") or None, int(r.get("child") or 0))


def ensure_payroll_sidebar_items():
	if not frappe.db.exists("Workspace Sidebar", SIDEBAR):
		return
	doc = frappe.get_doc("Workspace Sidebar", SIDEBAR)
	target = [i for i in _susunan() if _ada(i)]

	# Pertahankan menu lain (mis. tambahan HRMS versi baru) yang tidak ada di susunan ini.
	dikenal = {(i["type"], i.get("link_to")) for i in target if i["type"] == "Link"} | {
		("Section Break", i["label"]) for i in target if i["type"] == "Section Break"
	}
	lain = []
	for r in doc.items:
		k = (r.type, r.link_to) if r.type == "Link" else (r.type, r.label)
		if k not in dikenal:
			d = r.as_dict()
			lain.append({f: d.get(f) for f in ("type", "label", "link_to", "link_type", "icon", "child", "indent", "collapsible", "keep_closed", "show_arrow", "url", "filters", "route_options", "navigate_to_tab")})
	if lain:
		pos = next((n for n, i in enumerate(target) if i["label"] == "Settings"), len(target))
		target[pos:pos] = lain

	if [_kunci(r.as_dict()) for r in doc.items] == [_kunci(i) for i in target]:
		return

	doc.set("items", [])
	for i in target:
		doc.append("items", i)
	frappe.flags.in_import = True  # jangan ekspor ke file hrms/workspace_sidebar saat developer_mode
	try:
		doc.save(ignore_permissions=True)
	finally:
		frappe.flags.in_import = False
	frappe.clear_cache()
