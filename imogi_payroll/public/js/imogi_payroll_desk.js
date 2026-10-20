// Penyesuaian tampilan desk untuk Imogi Payroll:
//   1. menandai <body> saat berada di workspace kita, untuk aturan lebar di
//      imogi_payroll_desk.css
//   2. mencegah ikon aplikasi di halaman Desktop membuka tab baru

(() => {
	const TARGET = "imogi-payroll";
	const LABEL = "Imogi Payroll";
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
		try {
			const route = frappe.get_route() || [];
			if (route.some((bagian) => slug(bagian) === TARGET)) return true;
		} catch (e) {
			// router belum siap; jatuh ke pemeriksaan URL di bawah
		}
		const path = slug(window.location.pathname.split("?")[0]);
		return path.endsWith(`-${TARGET}`) || path.endsWith(`/${TARGET}`);
	}

	function tandai_lebar() {
		document.body.classList.toggle(KELAS, di_workspace_kita());
	}

	// ---------------------------------------------------------------
	// Ikon aplikasi di halaman Desktop (/desk) membuka tab baru.
	//
	// Penyebabnya di desktop_icons.bundle.js:
	//
	//   function N(s) {                       // menghitung route ikon
	//     if (s.link_type == "External" && s.link)
	//       e = window.location.origin + s.link;   // SELALU jadi absolut
	//     ...
	//   }
	//
	//   setup_click() {
	//     if (this.child_icons?.length && (icon_type == "App" || "Folder")) {
	//       ... buka modal daftar workspace, tanpa href      // ERPNext, HRMS
	//     } else {
	//       icon_route.startsWith("http") && attr("target", "_blank");
	//       attr("href", icon_route);                        // <- kita
	//     }
	//   }
	//
	// Semua ikon aplikasi memakai link_type "External", tapi ERPNext,
	// Framework, dan Frappe HR punya ikon anak sehingga masuk cabang modal
	// dan tidak pernah diberi href. Aplikasi kita belum punya ikon anak,
	// jadi jatuh ke cabang else: href absolut -> diawali "http" -> dipaksa
	// target="_blank".
	//
	// Diperbaiki pada ikon kita saja: target dilepas dan href absolut
	// diubah jadi relatif, lalu kliknya diserahkan ke router SPA. Ctrl/
	// Cmd/Shift-klik sengaja dibiarkan apa adanya supaya pengguna tetap
	// bisa membuka tab baru kalau memang mau.
	// ---------------------------------------------------------------
	function perbaiki_ikon_desktop() {
		const ikon = document.querySelectorAll(
			`a.desktop-icon[data-id="${LABEL}"][target="_blank"]`
		);

		ikon.forEach((a) => {
			a.removeAttribute("target");

			let relatif = a.getAttribute("href") || "";
			try {
				const url = new URL(relatif, window.location.origin);
				// hanya tangani tautan ke situs ini sendiri
				if (url.origin !== window.location.origin) return;
				relatif = url.pathname + url.search + url.hash;
				a.setAttribute("href", relatif);
			} catch (e) {
				return;
			}

			a.addEventListener("click", (e) => {
				// hormati niat pengguna membuka di tab/jendela baru
				if (e.ctrlKey || e.metaKey || e.shiftKey || e.button !== 0) return;
				if (!window.frappe || !frappe.set_route) return;
				e.preventDefault();
				frappe.set_route(relatif);
			});
		});
	}

	function terapkan() {
		tandai_lebar();
		perbaiki_ikon_desktop();
	}

	function pasang() {
		if (!window.frappe || !frappe.router || !frappe.router.on) {
			setTimeout(pasang, 300);
			return;
		}
		frappe.router.on("change", terapkan);

		// Grid ikon dirender belakangan dan dibangun ulang saat tata letak
		// berubah, jadi perubahan DOM ikut diawasi - bukan sekadar sekali
		// saat rute berpindah.
		const pengamat = new MutationObserver(() => perbaiki_ikon_desktop());
		pengamat.observe(document.body, { childList: true, subtree: true });

		terapkan();
	}

	if (document.readyState === "loading") {
		document.addEventListener("DOMContentLoaded", pasang);
	} else {
		pasang();
	}
})();
