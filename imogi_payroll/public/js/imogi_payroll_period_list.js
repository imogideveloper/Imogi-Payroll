// Kolom "Payroll Period" (payroll_sub_period) di list view: tampilkan label pendek ("Sep 2026") supaya tidak
// terpotong; label lengkap ("Sep 2026 (21 Aug 2026 – 20 Sep 2026)") muncul sebagai tooltip. Nilai yang
// tersimpan tidak berubah, jadi Group By dan filter tetap memakai label lengkap.
// Dimuat SETELAH list JS lain milik doctype yang sama (lihat doctype_list_js di hooks.py) agar tidak tertimpa.

(() => {
	const DOCTYPES = [
		"Payroll Entry",
		"Salary Slip",
		"Additional Salary",
		"Additional Multiple Salary",
		"Overtime",
	];

	const label_pendek = (value) => {
		const text = String(value || "");
		const i = text.indexOf(" (");
		return i > 0 ? text.slice(0, i) : text;
	};

	const format_payroll_period = (value) => {
		if (!value) return "";
		const full = frappe.utils.escape_html(value);
		return `<span title="${full}">${frappe.utils.escape_html(label_pendek(value))}</span>`;
	};

	DOCTYPES.forEach((doctype) => {
		const settings = (frappe.listview_settings[doctype] = frappe.listview_settings[doctype] || {});
		settings.formatters = settings.formatters || {};
		if (!settings.formatters.payroll_sub_period) {
			settings.formatters.payroll_sub_period = format_payroll_period;
		}
	});
})();
