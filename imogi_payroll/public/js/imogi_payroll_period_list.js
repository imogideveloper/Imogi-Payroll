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

	// Kolom yang di-center (dicocokkan dari judul kolom di header list).
	const CENTER_COLUMNS = {
		"Payroll Entry": ["Payroll Period", "Posting Date"],
	};

	function center_columns(listview, labels) {
		const $result = listview?.$result;
		if (!$result?.length) return;
		const wanted = new Set(labels.map((l) => __(l)));
		const $head_cols = $result.find(".list-row-head .list-row-col");
		const idx = [];
		$head_cols.each((i, el) => {
			if (wanted.has(el.textContent.trim())) idx.push(i);
		});
		if (!idx.length) return;
		const center = (cols) => idx.forEach((i) => cols[i] && (cols[i].style.textAlign = "center"));
		center($head_cols.toArray());
		$result.find(".list-row-container .list-row").each((_, row) => {
			center($(row).find(".list-row-col").toArray());
		});
	}

	DOCTYPES.forEach((doctype) => {
		const settings = (frappe.listview_settings[doctype] = frappe.listview_settings[doctype] || {});
		settings.formatters = settings.formatters || {};
		if (!settings.formatters.payroll_sub_period) {
			settings.formatters.payroll_sub_period = format_payroll_period;
		}

		// Center kolom; onload/refresh bawaan (mis. dari list JS lain) tetap dipanggil lebih dulu.
		const labels = CENTER_COLUMNS[doctype] || ["Payroll Period"];
		const run_center = (listview) => {
			center_columns(listview, labels);
			setTimeout(() => center_columns(listview, labels), 150);
		};
		["onload", "refresh"].forEach((hook) => {
			const original = settings[hook];
			settings[hook] = function (listview) {
				if (typeof original === "function") original.apply(this, arguments);
				run_center(listview);
			};
		});
	});
})();
