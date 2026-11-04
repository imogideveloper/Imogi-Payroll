"""Wajibkan karyawan (System User) mampir ke /checkin dulu sebelum masuk Desk,
selama dia belum absen (Employee Checkin log_type=IN) hari ini.

Ini bukan default Frappe/HRMS, dan gak nyala otomatis buat semua Employee.
Aktif per-orang lewat custom field "Wajib Absen Sebelum Masuk" (checkbox)
di form Employee, satu section sama field User ID -- default kosong/mati,
jadi harus dicentang manual per Employee.

Dipasang lewat hook `boot_session`: dijalankan setiap kali Desk (/app) dimuat,
jadi bukan cuma sekali pas login, tapi tiap kali dia buka/refresh Desk selama
belum absen hari itu.

Selain itu:
- `after_login` bikin dia mendarat di /checkin tiap kali login, bukan di Desk --
  jadi status absen hari itu selalu kelihatan duluan, sudah absen atau belum.
- `one_punch_per_day` nolak check-in kedua atau check-out kedua di hari yang sama.
  Aturannya di server, bukan cuma di tombol, karena tombol gampang dilewati
  dengan manggil API-nya langsung.
"""

import frappe
from frappe import _
from frappe.utils import now_datetime, today


def force_server_time(doc, method=None):
	"""before_insert Employee Checkin: cegah karyawan absen pakai jam palsu
	(jam device diubah, atau panggil API langsung) lewat halaman /checkin.

	Aturannya bukan berdasarkan role (role kayak "HR User" ternyata nempel
	juga ke akun karyawan biasa di sistem ini, jadi gak bisa dipercaya buat
	nentuin siapa yang "berhak"). Yang dipakai: SIAPA yang lagi diabsenin.
	- Ngabsenin diri sendiri (Employee.user_id == user yang lagi login)
	  -> jam server dipaksa, titik. Siapapun dia, HR sekalipun.
	- Nginput/ngoreksi jam punya ORANG LAIN (lewat Desk, misal lupa absen)
	  -> jam yang diinput dipercaya, karena itu jelas bukan self-checkin.
	"""
	employee_user = frappe.db.get_value("Employee", doc.employee, "user_id")
	if employee_user and employee_user == frappe.session.user:
		doc.time = now_datetime()


def gated_employee(user: str) -> str | None:
	"""The Employee record of someone whose Desk is held behind a check-in, if any."""
	if not user or user in ("Administrator", "Guest"):
		return None
	return frappe.db.get_value(
		"Employee",
		{"user_id": user, "status": "Active", "wajib_absen_sebelum_masuk": 1},
		"name",
	)


def after_login(login_manager=None):
	"""Land on /checkin after logging in, rather than on the Desk.

	Set through `frappe.local.flags.home_page`, which `website.utils.get_home_page()` reads before
	anything else; `set_user_info()` calls that a moment later to decide where to send the browser.
	Writing `frappe.local.response["home_page"]` here instead would be overwritten by it.

	Only for the people this applies to: everyone else keeps the landing page they had.
	"""
	user = getattr(login_manager, "user", None) or frappe.session.user
	if gated_employee(user):
		frappe.local.flags.home_page = "/checkin"


def one_punch_per_day(doc, method=None):
	"""One check-in and one check-out per day, and no more.

	Enforced here rather than by hiding a button: the button posts to an ordinary REST endpoint
	that anyone signed in can call again.

	Drawn at the same line as force_server_time(): this binds someone punching their own card.
	HR entering or fixing another employee's log -- the usual reason a second line exists at all
	-- is left alone.
	"""
	employee_user = frappe.db.get_value("Employee", doc.employee, "user_id")
	if not employee_user or employee_user != frappe.session.user:
		return

	already = frappe.db.exists(
		"Employee Checkin",
		{
			"employee": doc.employee,
			"log_type": doc.log_type,
			"time": [">=", f"{today()} 00:00:00"],
			"name": ["!=", doc.name or ""],
		},
	)
	if already:
		frappe.throw(
			_("Kamu sudah {0} hari ini. Absen berikutnya baru bisa besok.").format(
				_("check-in") if doc.log_type == "IN" else _("check-out")
			),
			title=_("Sudah Absen"),
		)


def refresh_boot(doc, method=None):
	"""Drop this employee's cached Desk boot after a punch.

	The gate reads `frappe.boot.needs_checkin`, and sessions.py serves the whole bootinfo from
	`frappe.cache.hget("bootinfo", user)` -- computed once per session and kept. /checkin is a
	website page, so clocking in there never refreshes it: the Desk went on answering "belum
	absen", the gate bounced the cashier back to /checkin, and the loop only broke when something
	else happened to clear the cache.

	Also on delete, so resetting a day's attendance puts the gate back up straight away.
	"""
	user = frappe.db.get_value("Employee", doc.employee, "user_id")
	if user:
		frappe.clear_cache(user=user)


def boot_session(bootinfo):
	bootinfo.needs_checkin = False
	# Whether this person clocks in at all -- separate from whether they still owe one today.
	# After checking in, needs_checkin goes false, so it cannot be used to decide who should be
	# offered a way to clock OUT. That is what this one is for.
	bootinfo.checkin_enabled = False

	user = frappe.session.user
	if user in ("Administrator", "Guest"):
		return

	employee = gated_employee(user)
	if not employee:
		# bukan karyawan, belum ditautkan ke akun ini, atau toggle "Wajib Absen
		# Sebelum Masuk" di form Employee belum dicentang -> jangan di-gate
		return

	already_checked_in = frappe.db.exists(
		"Employee Checkin",
		{
			"employee": employee,
			"log_type": "IN",
			"time": [">=", f"{today()} 00:00:00"],
		},
	)

	bootinfo.checkin_enabled = True
	bootinfo.needs_checkin = not bool(already_checked_in)
