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
 * Urutan kolom list: ID, (Posting Date bila kolom data pertama), Employee Name, lalu kolom lain.
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
		// Cari <a> dulu. querySelector("x a, x") mengembalikan elemen yang lebih dulu di dokumen, yaitu span
		// pembungkusnya; menulis teks ke span itu menghapus <a> di dalamnya sehingga baris tidak bisa dibuka.
		const subject_link =
			cols[0].querySelector("span.level-item.bold a") || cols[0].querySelector("span.level-item.bold");
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

/**
 * Pindahkan kolom (yang kini berisi nama karyawan) tepat setelah kolom ID, atau setelah kolom Posting Date
 * bila Posting Date adalah kolom data pertama (Otoexpert: ID, Posting Date, Employee Name, ...).
 */
function move_after_subject(cols, moved) {
	// cols[1] = kolom Tag (tersembunyi); kolom data pertama = cols[2].
	let index = 2;
	if (cols[2] && cols[2] !== moved && is_posting_date_col(cols[2])) {
		index = 3;
	}
	const target = cols[index];
	if (target && target !== moved) {
		target.parentNode.insertBefore(moved, target);
	}
}

/** Kolom Posting Date: sel baris punya filter "posting_date,...", sel judul berteks "Posting Date". */
function is_posting_date_col(col) {
	if (col.querySelector('[data-filter^="posting_date,"]')) {
		return true;
	}
	return col.textContent.trim() === __("Posting Date");
}
