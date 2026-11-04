// Paksa ke halaman /checkin selama karyawan belum absen (IN) hari ini.
// frappe.boot sudah tersedia di titik ini (disisipkan server sebelum script ini di-load).
(function () {
	if (frappe.boot && frappe.boot.needs_checkin && !window.location.pathname.startsWith("/checkin")) {
		window.location.href = "/checkin";
	}
})();

// Absen pulang belongs with the other things you do to yourself -- editing your profile, logging
// out -- not in the POS "..." menu beside Open Form View, which is about the document on screen.
// So it goes in the avatar menu on the Desktop.
//
// And Logout is taken out of that menu for these people: leaving without clocking out is the one
// mistake this whole feature exists to prevent, and a Logout sitting one row below Absen Pulang
// is an invitation to make it. Their way out is on /checkin, and it appears only after the
// check-out is recorded.
//
// Only for someone who actually clocks in (boot.checkin_enabled). Everyone else keeps their
// Logout exactly where it was.
(function () {
	if (!frappe.boot || !frappe.boot.checkin_enabled) return;
	if (!frappe.ui || typeof frappe.ui.create_menu !== "function") return;
	if (frappe.ui.create_menu.__imf_checkin_patched) return;

	var create_menu = frappe.ui.create_menu;

	function patched(opts) {
		try {
			// the Desktop avatar menu, not every menu on the page
			if (opts && opts.menu_items && opts.parent && $(opts.parent).hasClass("desktop-avatar")) {
				var items = opts.menu_items.filter(function (item) {
					return item && item.label !== "Logout";
				});
				items.push({
					icon: "log-out",
					label: __("Absen Pulang"),
					onClick: function () {
						window.location.href = "/checkin";
					},
				});
				opts = $.extend({}, opts, { menu_items: items });
			}
		} catch (e) {
			// a menu that fails to be adjusted must still open
			console.error("imogi_payroll: checkin menu", e);
		}
		return create_menu.call(this, opts);
	}

	patched.__imf_checkin_patched = true;
	frappe.ui.create_menu = patched;
})();
