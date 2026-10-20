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
	const TARGET = "imogi-payroll";
	const KELAS = "imogi-wide";

	// Rute bisa memakai nama workspace ("Imogi Payroll") maupun slug URL
	// ("imogi-payroll"), tergantung dari mana navigasinya datang. Keduanya
	// diratakan ke bentuk yang sama sebelum dibandingkan.
	function slug(nilai) {
		return (nilai || "")
			.toString()
			.trim()
			.toLowerCase()
			.replace(/[\s_]+/g, "-");
	}

	function di_workspace_kita() {
		// 1) lewat router - sumber paling tepat saat berpindah halaman
		try {
			const route = frappe.get_route() || [];
			if (route.some((bagian) => slug(bagian) === TARGET)) return true;
		} catch (e) {
			// router belum siap; jatuh ke pemeriksaan URL di bawah
		}

		// 2) cadangan lewat URL - menangani muat-ulang halaman langsung,
		//    sekaligus bench yang menyajikan desk di /desk maupun /app
		const path = slug(window.location.pathname.split("?")[0]);
		return path.endsWith(`-${TARGET}`) || path.endsWith(`/${TARGET}`);
	}

	function terapkan() {
		document.body.classList.toggle(KELAS, di_workspace_kita());
	}

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
