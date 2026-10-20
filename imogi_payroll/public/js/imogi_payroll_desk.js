// Pasang kelas .imogi-wide pada <body> hanya ketika rute sedang berada di
// workspace Imogi Payroll, supaya aturan lebar di imogi_payroll_desk.css
// aktif di modul kita saja.
//
// Kenapa lewat JS dan bukan CSS murni: lebar dikunci oleh selektor
// `body:not(.full-width) .layout-main`, sementara penanda rute ada di elemen
// lain (.page-container[data-page-route]). CSS tidak bisa menaikkan kondisi
// dari elemen anak ke <body>, jadi penandanya dipasang dari sini.
//
// Preferensi "Toggle Full Width" milik pengguna sengaja tidak disentuh -
// itu berlaku global untuk semua aplikasi, bukan cuma punya kita.

(() => {
	const WORKSPACE = "imogi-payroll";
	const KELAS = "imogi-wide";

	function di_workspace_kita() {
		const route = frappe.get_route() || [];
		// Rute workspace berbentuk ["Workspaces", "<nama>"]; di sebagian versi
		// nama workspace juga muncul sebagai rute tunggal.
		const nama = (route[1] || route[0] || "").toString().toLowerCase();
		return route[0] === "Workspaces" ? nama === WORKSPACE : nama === WORKSPACE;
	}

	function terapkan() {
		document.body.classList.toggle(KELAS, di_workspace_kita());
	}

	// router mungkin belum siap saat berkas ini dimuat.
	function pasang() {
		if (!window.frappe || !frappe.router || !frappe.router.on) {
			setTimeout(pasang, 300);
			return;
		}
		frappe.router.on("change", terapkan);
		terapkan();
	}

	if (document.readyState === "loading") {
		document.addEventListener("DOMContentLoaded", pasang);
	} else {
		pasang();
	}
})();
