// Additional Multiple Salary: field Type (Earning / Deduction) menyaring pilihan Komponen Gaji.
// Type kosong = semua komponen ditampilkan; Type lalu terisi otomatis dari komponen yang dipilih.

frappe.ui.form.on("Additional Multiple Salary", {
	setup(frm) {
		frm.set_query("salary_component", () => {
			const filters = { disabled: 0, statistical_component: 0 };
			if (frm.doc.type) filters.type = frm.doc.type;
			// Dropdown Link bawaan hanya 10 hasil; tampilkan semua komponen (Earning ~56).
			return { filters, page_length: 200 };
		});
	},

	type(frm) {
		// Komponen yang sudah dipilih tapi tipenya beda dengan Type baru -> dikosongkan.
		if (!frm.doc.type || !frm.doc.salary_component) return;
		frappe.db.get_value("Salary Component", frm.doc.salary_component, "type").then((r) => {
			const tipe = (r.message || {}).type;
			if (tipe && tipe !== frm.doc.type) frm.set_value("salary_component", "");
		});
	},

	salary_component(frm) {
		if (!frm.doc.salary_component || frm.doc.type) return;
		frappe.db.get_value("Salary Component", frm.doc.salary_component, "type").then((r) => {
			const tipe = (r.message || {}).type;
			if (tipe) frm.set_value("type", tipe);
		});
	},
});
