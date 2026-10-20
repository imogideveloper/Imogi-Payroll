// List Salary Slip: indikator status yang lebih informatif daripada
// Draft/Submitted saja, plus penanda kalau PPh 21 tidak pernah dihitung.

frappe.listview_settings["Salary Slip"] = {
	add_fields: ["docstatus", "pph21_amount", "net_pay", "start_date", "end_date"],

	get_indicator(doc) {
		if (doc.docstatus === 2) {
			return [__("Dibatalkan"), "red", "docstatus,=,2"];
		}
		if (doc.docstatus === 0) {
			return [__("Draft"), "orange", "docstatus,=,0"];
		}
		// Sudah submit. Bedakan yang kena PPh 21 dan yang tidak, supaya slip
		// bernilai 0 - entah karena bebas pajak atau karena perhitungannya
		// terlewat - langsung kelihatan tanpa harus dibuka satu per satu.
		if (!flt(doc.pph21_amount)) {
			return [__("Submit - tanpa PPh 21"), "blue", "pph21_amount,=,0"];
		}
		return [__("Submit"), "green", "docstatus,=,1"];
	},

	formatters: {
		pph21_amount(value) {
			if (!flt(value)) {
				return `<span class="text-muted">—</span>`;
			}
			return format_currency(flt(value), frappe.defaultCurrency || "IDR");
		},
	},
};
