// List Salary Slip: indikator status yang lebih informatif daripada
// Draft/Submitted saja, plus penanda kalau PPh 21 tidak pernah dihitung.

frappe.listview_settings["Salary Slip"] = {
	add_fields: ["docstatus", "pph21_amount", "net_pay", "start_date", "end_date"],

	refresh(listview) {
		put_id_column_first(listview);
		setTimeout(() => put_id_column_first(listview), 150);
	},

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

/**
 * Urutan kolom list: ID, Employee Name, Posting Date, Net Pay.
 *
 * Kolom pertama list Frappe selalu "judul" dokumen (di Salary Slip = Employee Name) dan kolom ID
 * selalu paling kanan; urutan ini tidak bisa diatur lewat List View Settings. Jadi isi kedua kolom
 * ditukar di tampilan saja: kolom pertama menampilkan ID, kolom terakhir menampilkan nama karyawan.
 * Link ke dokumen tetap sama. Tidak ada data yang berubah.
 */
function put_id_column_first(listview) {
	const $result = listview?.$result;
	if (!$result?.length) {
		return;
	}

	const text_el = (col) => col.querySelector("a") || col.querySelector("span:not(.select-like)") || col;
	const swap = (subject_col, id_col, subject_text_el) => {
		const id_el = text_el(id_col);
		const a = subject_text_el.textContent;
		subject_text_el.textContent = id_el.textContent;
		id_el.textContent = a;
		// teks ID dulu dapat filter "name = ..."; setelah ditukar isinya nama, jadi filter itu dilepas.
		id_el.removeAttribute("data-filter");
	};

	// Judul kolom
	const head_cols = $result.find(".list-row-head .list-header-subject .list-row-col").toArray();
	if (head_cols.length > 1) {
		const subject_label = head_cols[0].querySelector("span.level-item:not(.select-like)");
		const id_head = head_cols[head_cols.length - 1];
		if (subject_label && text_el(id_head).textContent.trim() === __("ID")) {
			swap(head_cols[0], id_head, subject_label);
			move_after_subject(head_cols, id_head);
		}
	}

	// Isi baris
	$result.find(".list-row-container .list-row").each((_, row) => {
		const cols = $(row).find(".level-left > .list-row-col").toArray();
		if (cols.length < 2) {
			return;
		}
		const subject_link = cols[0].querySelector("span.level-item.bold a, span.level-item.bold");
		const id_col = cols[cols.length - 1];
		if (!subject_link) {
			return;
		}
		// Sudah ditukar bila kolom pertama sudah berisi nomor dokumen.
		if (is_slip_id(subject_link.textContent)) {
			return;
		}
		if (is_slip_id(text_el(id_col).textContent)) {
			swap(cols[0], id_col, subject_link);
			move_after_subject(cols, id_col);
		}
	});
}

/** Nomor slip: bawaan HRMS "Sal Slip/<karyawan>/00001", atau seri situs seperti "SLIP/1" (Otoexpert). */
function is_slip_id(text) {
	const t = (text || "").trim();
	return t.startsWith("Sal Slip/") || t.startsWith("SLIP/");
}

/** Pindahkan kolom (yang kini berisi nama karyawan) ke posisi kedua, tepat setelah kolom pertama (ID). */
function move_after_subject(cols, moved) {
	// cols[1] = kolom Tag (tersembunyi); kolom data pertama = cols[2].
	const first_data_col = cols[2];
	if (first_data_col && first_data_col !== moved) {
		first_data_col.parentNode.insertBefore(moved, first_data_col);
	}
}
