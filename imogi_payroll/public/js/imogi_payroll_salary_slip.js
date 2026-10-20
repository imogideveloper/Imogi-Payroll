// Salary Slip: panel rincian PPh 21 + kunci grid iuran perusahaan.
//
// Field `pph21_info` menyimpan hasil perhitungan pajak sebagai JSON. Isinya
// justru informasi paling berharga di slip - menjelaskan KENAPA pajaknya
// sekian - tapi kalau ditampilkan mentah tidak ada yang bisa membacanya.
// Berkas ini merendernya jadi tabel di field HTML `imogi_pph21_breakdown`.

const IMOGI_RP = (v) => format_currency(flt(v), frappe.defaultCurrency || "IDR");

function imogi_pph21_rows(info, frm) {
	const ada_tarif = (info.rate ?? null) !== null;
	// Pada metode TER bulanan, PPh 21 = bruto x tarif. PTKP/netto/PKP ikut
	// dihitung tapi TIDAK dipakai untuk angka bulanan - hanya bekal koreksi
	// progresif di Desember. Diredupkan agar tidak disangka bagian hitungan.
	const info_saja = frm.doc.tax_type === "TER";

	return [
		{ label: __("Bruto (dasar pengenaan)"), value: info.bruto, strong: true },
		{ label: __("Pengurang netto"), value: info.pengurang_netto, negative: true },
		{ label: __("Biaya jabatan"), value: info.biaya_jabatan, negative: true },
		{ label: __("Netto"), value: info.netto, muted: info_saja },
		{ label: __("PTKP"), value: info.ptkp, negative: true, muted: info_saja },
		{ label: __("PKP"), value: info.pkp, muted: info_saja },
		{
			label: __("Tarif TER"),
			value: ada_tarif ? `${flt(info.rate)}%` : "-",
			raw: true,
			highlight: true,
		},
		{ label: __("PPh 21"), value: info.pph21, strong: true, highlight: true },
	];
}

function imogi_natura_rows(frm) {
	// HANYA iuran perusahaan yang benar-benar menambah bruto, yaitu yang
	// ber-flag Is Tax Applicable. Ini sumber kebingungan paling sering:
	// bruto lebih besar dari gross pay, dan selisihnya datang dari sini.
	// JHT dan JP perusahaan sengaja tidak ikut - belum dipajaki saat ini.
	return (frm.doc.employer_contributions || []).filter(
		(r) => flt(r.amount) > 0 && cint(r.is_tax_applicable)
	);
}

function imogi_render_pph21(frm) {
	const field = frm.fields_dict.imogi_pph21_breakdown;
	if (!field || !field.$wrapper) return;
	imogi_inject_style();
	const $el = field.$wrapper.empty();

	let info = {};
	try {
		info = JSON.parse(frm.doc.pph21_info || "{}");
	} catch (e) {
		info = {};
	}

	if (!frm.doc.pph21_info || !Object.keys(info).length) {
		$el.html(
			`<div class="imogi-pph21-empty text-muted">${__(
				"Rincian muncul setelah slip dihitung - simpan slip terlebih dulu."
			)}</div>`
		);
		return;
	}

	// Perhitungan dilewati karena Employment Type bukan Full-time.
	if (info.employment_type_checked === false) {
		$el.html(`
			<div class="imogi-pph21-alert">
				<div class="imogi-pph21-alert-title">${__("PPh 21 tidak dihitung")}</div>
				<div>${__(
					"Employment Type karyawan ini bukan Full-time, sehingga perhitungan PPh 21 dilewati dan nilainya 0. Perbaiki Employment Type kalau seharusnya dikenakan pajak."
				)}</div>
			</div>`);
		return;
	}

	const metode =
		frm.doc.tax_type === "DECEMBER"
			? __("Koreksi Progresif Desember")
			: __("TER Bulanan");

	const baris = imogi_pph21_rows(info, frm)
		.map((r) => {
			const cls = [
				r.strong ? "is-strong" : "",
				r.highlight ? "is-highlight" : "",
				r.muted ? "is-muted" : "",
			]
				.filter(Boolean)
				.join(" ");
			const nilai = r.raw ? r.value : IMOGI_RP(r.value);
			const tanda = r.negative && flt(r.value) ? "&minus;&nbsp;" : "";
			return `<tr class="${cls}">
					<td class="imogi-label">${r.label}</td>
					<td class="imogi-value">${tanda}${nilai}</td>
				</tr>`;
		})
		.join("");

	const natura = imogi_natura_rows(frm);
	const natura_total = natura.reduce((a, r) => a + flt(r.amount), 0);
	const natura_html = natura.length
		? `<div class="imogi-pph21-sub">
				<div class="imogi-pph21-sub-title">${__(
					"Iuran perusahaan yang menambah bruto"
				)}</div>
				<table class="imogi-pph21-table is-sub">
					<tr>
						<td class="imogi-label">${__("Gaji bruto (earnings)")}</td>
						<td class="imogi-value">${IMOGI_RP(frm.doc.gross_pay)}</td>
					</tr>
					${natura
						.map(
							(r) =>
								`<tr>
									<td class="imogi-label">+ ${frappe.utils.escape_html(
										r.salary_component || ""
									)}</td>
									<td class="imogi-value">${IMOGI_RP(r.amount)}</td>
								</tr>`
						)
						.join("")}
					<tr class="is-strong">
						<td class="imogi-label">${__("Bruto dasar pengenaan")}</td>
						<td class="imogi-value">${IMOGI_RP(flt(frm.doc.gross_pay) + natura_total)}</td>
					</tr>
				</table>
				<div class="imogi-pph21-note">${__(
					"Hanya iuran ber-flag Is Tax Applicable yang menambah bruto. JHT dan JP yang dibayar perusahaan tidak dipajaki saat ini, jadi tidak ikut di sini."
				)}</div>
			</div>`
		: "";

	const catatan_ter =
		frm.doc.tax_type === "TER"
			? `<div class="imogi-pph21-note">${__(
					"Metode TER: PPh 21 = bruto x tarif. Baris yang diredupkan (netto, PTKP, PKP) tidak dipakai untuk angka bulanan - hanya bekal koreksi progresif di Desember."
			  )}</div>`
			: "";

	$el.html(`
		<div class="imogi-pph21">
			<div class="imogi-pph21-head">
				<span class="imogi-pph21-badge">${metode}</span>
			</div>
			<table class="imogi-pph21-table">${baris}</table>
			${catatan_ter}
			${natura_html}
		</div>`);
}

// Gaya memakai variabel CSS desk supaya ikut tema terang maupun gelap.
function imogi_inject_style() {
	if (document.getElementById("imogi-pph21-style")) return;
	const tag = document.createElement("style");
	tag.id = "imogi-pph21-style";
	tag.textContent = `
		.imogi-pph21 { max-width: 560px; }
		.imogi-pph21-head { margin-bottom: 10px; }
		.imogi-pph21-badge {
			display: inline-block; padding: 3px 10px; border-radius: 12px;
			font-size: 11px; font-weight: 600; letter-spacing: .02em;
			background: var(--control-bg); color: var(--text-muted);
			border: 1px solid var(--border-color);
		}
		.imogi-pph21-table { width: 100%; border-collapse: collapse; }
		.imogi-pph21-table td {
			padding: 7px 0; border-bottom: 1px solid var(--border-color);
			font-size: var(--text-md); vertical-align: baseline;
		}
		.imogi-pph21-table tr:last-child td { border-bottom: none; }
		.imogi-pph21-table .imogi-label { color: var(--text-muted); }
		.imogi-pph21-table .imogi-value {
			text-align: right; font-variant-numeric: tabular-nums;
			color: var(--text-color); white-space: nowrap; padding-left: 16px;
		}
		.imogi-pph21-table tr.is-strong .imogi-label,
		.imogi-pph21-table tr.is-strong .imogi-value { font-weight: 600; }
		.imogi-pph21-table tr.is-highlight .imogi-value { font-weight: 600; }
		.imogi-pph21-table tr.is-highlight { background: var(--control-bg); }
		.imogi-pph21-table tr.is-muted .imogi-label,
		.imogi-pph21-table tr.is-muted .imogi-value { opacity: .5; }
		.imogi-pph21-table.is-sub td { padding: 5px 0; font-size: 12px; }
		.imogi-pph21-sub { margin-top: 18px; }
		.imogi-pph21-sub-title {
			font-size: 11px; font-weight: 600; text-transform: uppercase;
			letter-spacing: .04em; color: var(--text-muted); margin-bottom: 4px;
		}
		.imogi-pph21-note {
			margin-top: 8px; font-size: 11px; line-height: 1.5; color: var(--text-muted);
		}
		.imogi-pph21-alert {
			max-width: 560px; padding: 12px 14px; border-radius: 6px;
			border: 1px solid var(--border-color);
			border-left: 3px solid var(--orange-500);
			background: var(--control-bg);
			font-size: var(--text-md); color: var(--text-color);
		}
		.imogi-pph21-alert-title { font-weight: 600; margin-bottom: 4px; }
		.imogi-pph21-empty { font-size: var(--text-md); padding: 4px 0; }
	`;
	document.head.appendChild(tag);
}

frappe.ui.form.on("Salary Slip", {
	refresh(frm) {
		imogi_render_pph21(frm);

		// Iuran perusahaan dihitung sistem - jangan sampai diedit manual.
		if (frm.fields_dict.employer_contributions) {
			frm.set_df_property("employer_contributions", "cannot_add_rows", true);
			frm.set_df_property("employer_contributions", "cannot_delete_rows", true);
		}
	},

	pph21_info(frm) {
		imogi_render_pph21(frm);
	},
});
