import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate, time_diff_in_hours

from imogi_payroll.config.overtime import weighted_hours


class ImogiPayrollOvertime(Document):
	"""Input lembur harian (OT1 dan OT2 per hari, seperti di Odoo)."""

	def validate(self):
		self._check_duplicate()
		sessions = self._sessions()
		self.total_hours = round(sum(h for _s, _e, h in sessions), 4)
		if not self.day_type:
			self.day_type = self._detect_day_type()
		self.weighted_hours = round(weighted_hours(self.total_hours, self.day_type), 4)

	def _sessions(self):
		out = []
		for label, a, b in (("1", self.ot1_from, self.ot1_to), ("2", self.ot2_from, self.ot2_to)):
			if not a and not b:
				continue
			if not (a and b):
				frappe.throw(_("Lembur {0}: jam mulai dan jam selesai harus diisi dua-duanya.").format(label))
			hours = time_diff_in_hours(b, a)
			if hours <= 0:
				frappe.throw(_("Lembur {0}: jam selesai harus setelah jam mulai. Kalau melewati tengah malam, pecah jadi dua sesi.").format(label))
			out.append((a, b, hours))
		if not out:
			frappe.throw(_("Isi minimal satu sesi lembur."))
		if len(out) == 2 and time_diff_in_hours(self.ot2_from, self.ot1_to) < 0:
			frappe.throw(_("Sesi Lembur 2 tidak boleh mulai sebelum Lembur 1 selesai."))
		return out

	def _check_duplicate(self):
		exists = frappe.db.exists(
			"Imogi Payroll Overtime",
			{"employee": self.employee, "overtime_date": self.overtime_date, "docstatus": ["<", 2], "name": ["!=", self.name or ""]},
		)
		if exists:
			frappe.throw(_("Sudah ada lembur {0} untuk {1} pada {2}.").format(exists, self.employee, self.overtime_date))

	def _detect_day_type(self) -> str:
		try:
			from hrms.utils.holiday_list import get_holiday_list_for_employee

			hl = get_holiday_list_for_employee(self.employee, raise_exception=False, as_on=self.overtime_date)
			if hl:
				weekly = frappe.db.get_value("Holiday", {"parent": hl, "holiday_date": getdate(self.overtime_date)}, "weekly_off")
				if weekly is not None:
					return "Offday (6)" if weekly else "Public Holiday (6)"
		except Exception:
			# Tanpa Holiday List / error lain: jatuh ke Workday, tapi jangan diam-diam.
			frappe.log_error(frappe.get_traceback(), "Imogi Payroll Overtime: deteksi jenis hari gagal")
		return "Workday"
