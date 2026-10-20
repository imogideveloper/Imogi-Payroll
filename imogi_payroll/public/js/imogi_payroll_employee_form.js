// Imogi Payroll: label-left / input-right layout across the whole Employee
// form. Each field is only re-flowed INSIDE its own wrapper (label column +
// input column) - the outer wrapper/column width is left untouched, so
// ERPNext's native grouping (e.g. Series/Gender/Date of Joining sharing one
// row) stays intact; only the label-above-input stacking inside each field
// becomes label-left/input-right.

const IMOGI_PAYROLL_LABEL_WIDTH = "180px";

const IMOGI_PAYROLL_SKIP_FIELDTYPES = new Set([
	"Section Break",
	"Column Break",
	"Tab Break",
	"Table",
	"Table MultiSelect",
	"HTML",
	"Button",
	"Heading",
	"Fold",
	"Image",
	"Signature",
]);

function imogi_payroll_style_standard_field($wrapper) {
	const $form_group = $wrapper.find(".form-group").first();
	if (!$form_group.length) return;

	$form_group.css({
		display: "flex",
		"align-items": "flex-start",
		gap: "16px",
	});

	$form_group.children(".clearfix").css({
		flex: `0 0 ${IMOGI_PAYROLL_LABEL_WIDTH}`,
		"max-width": IMOGI_PAYROLL_LABEL_WIDTH,
		"padding-top": "7px",
		"margin-bottom": "0",
	});

	$form_group.children(".control-input-wrapper").css({
		flex: "1 1 auto",
		"min-width": "0",
	});

	$wrapper.css({ "margin-bottom": "4px", "padding-bottom": "0" });
	$form_group.css({ "margin-bottom": "0" });
}

// Checkbox markup is <div class="checkbox"><label><input-area/><disp-area/>
// <label-area/><help/></label><p class="help-box">...</p></div> - label text
// and checkbox are siblings inside one <label>, and the description is a
// separate sibling below that whole label. To get a clean [label | checkbox
// + description stacked] layout we actually move input-area/disp-area/help
// and the help-box paragraph into one new right-hand column, instead of
// trying to fake it with CSS `order` (which doesn't keep the description
// aligned under the checkbox reliably).
function imogi_payroll_style_check_field($wrapper) {
	const $checkbox_div = $wrapper.find(".checkbox").first();
	if (!$checkbox_div.length) return;
	if ($checkbox_div.hasClass("imogi-payroll-styled")) return; // idempotent across refreshes
	$checkbox_div.addClass("imogi-payroll-styled");

	const $label = $checkbox_div.find("> label").first();
	if (!$label.length) return;

	const $label_area = $label.children(".label-area");
	const $help_box = $wrapper.find(".help-box");

	// right column is itself a flex row: [checkbox] [description text],
	// so the checkbox and the first line of the description sit on the
	// same line (help-box is a <p>, block-level, so it forces a new line
	// unless it's a flex sibling here rather than stacked underneath).
	const $right_col = $('<div class="imogi-payroll-check-right"></div>').css({
		flex: "1 1 auto",
		"min-width": "0",
		display: "flex",
		"align-items": "flex-start",
		gap: "8px",
	});
	$label.children(".input-area, .disp-area, .help").appendTo($right_col);
	$help_box
		.appendTo($right_col)
		.css({ margin: "0", "flex": "1 1 auto", "min-width": "0" });
	$right_col.appendTo($label);

	$label.css({
		display: "flex",
		"align-items": "flex-start",
		gap: "12px",
		width: "100%",
		"margin-bottom": "4px",
	});
	$label_area.css({
		flex: `0 0 ${IMOGI_PAYROLL_LABEL_WIDTH}`,
		"max-width": IMOGI_PAYROLL_LABEL_WIDTH,
	});
	$right_col.children(".input-area").css({ "margin-top": "2px" });

	// Bootstrap's default .checkbox / form-group spacing is generous
	// (~16-24px between fields) - tighten it for our compact 2-col layout.
	$checkbox_div.css({ "margin-bottom": "0", "padding-bottom": "0" });
	$wrapper.css({ "margin-bottom": "10px", "padding-bottom": "0" });
}

function imogi_payroll_apply_horizontal_layout(frm) {
	Object.keys(frm.fields_dict).forEach((fieldname) => {
		const field = frm.fields_dict[fieldname];
		const df = field && field.df;
		if (!field || !field.$wrapper || !df) return;
		if (IMOGI_PAYROLL_SKIP_FIELDTYPES.has(df.fieldtype)) return;

		if (df.fieldtype === "Check") {
			imogi_payroll_style_check_field(field.$wrapper);
		} else {
			imogi_payroll_style_standard_field(field.$wrapper);
		}

		// the column each field sits in can carry its own bottom
		// padding/margin on top of the field's own - tighten that too.
		field.$wrapper.closest(".form-column").css({
			"margin-bottom": "0",
			"padding-bottom": "0",
		});
	});
}

// Our own section ("Informasi Pajak & BPJS" / "Dokumen Identitas") has no
// Column Break, so each field there is already alone in a full-width
// column - make sure it actually fills that width edge to edge.
const IMOGI_PAYROLL_FULL_WIDTH_FIELDS = [
	"tax_status",
	"exempt_from_pph21",
	"bebas_bpjs",
	"bebas_bpjs_kesehatan",
	"bebas_bpjs_jht",
	"bebas_bpjs_jp",
	"ktp_no",
	"npwp_no",
	"ktp_attachment",
	"npwp_attachment",
];

function imogi_payroll_fill_own_column(frm) {
	IMOGI_PAYROLL_FULL_WIDTH_FIELDS.forEach((fieldname) => {
		const field = frm.fields_dict[fieldname];
		if (!field || !field.$wrapper) return;
		field.$wrapper.css({ width: "100%", "max-width": "100%" });
	});
}

// "Bebas PPh 21" / "Bebas BPJS" have long 3-line descriptions and naturally
// need more width; "Bebas BPJS Kesehatan/JHT/JP" are short one-liners that
// would otherwise each burn a full row of mostly-empty space below them.
// Pull the 3 short ones into their own narrower column that sits beside
// the two long ones instead.
function imogi_payroll_two_column_bpjs_section(frm) {
	const left_fieldnames = ["exempt_from_pph21", "bebas_bpjs"];
	const right_fieldnames = ["bebas_bpjs_kesehatan", "bebas_bpjs_jht", "bebas_bpjs_jp"];

	const anchor = frm.fields_dict["exempt_from_pph21"];
	if (!anchor || !anchor.$wrapper) return;
	if (anchor.$wrapper.parent().hasClass("imogi-payroll-bpjs-col-left")) return; // idempotent

	const $row = $(
		'<div class="imogi-payroll-bpjs-row" style="display:flex; gap:24px; align-items:flex-start; width:100%;"></div>'
	);
	const $left = $(
		'<div class="imogi-payroll-bpjs-col-left" style="flex:1 1 60%; min-width:0;"></div>'
	);
	const $right = $(
		'<div class="imogi-payroll-bpjs-col-right" style="flex:0 0 380px; max-width:380px;"></div>'
	);

	$row.insertBefore(anchor.$wrapper);
	$row.append($left).append($right);

	left_fieldnames.forEach((fieldname) => {
		const field = frm.fields_dict[fieldname];
		if (field && field.$wrapper) $left.append(field.$wrapper);
	});
	right_fieldnames.forEach((fieldname) => {
		const field = frm.fields_dict[fieldname];
		if (field && field.$wrapper) $right.append(field.$wrapper);
	});
}

// Frappe centers every form section at --page-max-width (900px by default),
// leaving a lot of empty space on wide screens. Override that variable on
// the form's own wrapper only, so it cascades to every .section-head /
// .section-body inside this Employee form without touching any other
// doctype's forms.
function imogi_payroll_widen_form(frm) {
	if (frm.wrapper) {
		$(frm.wrapper).css("--page-max-width", "1400px");
	}
}

function imogi_payroll_refresh(frm) {
	imogi_payroll_widen_form(frm);
	imogi_payroll_apply_horizontal_layout(frm);
	imogi_payroll_fill_own_column(frm);
	imogi_payroll_two_column_bpjs_section(frm);
}

frappe.ui.form.on("Employee", {
	refresh: imogi_payroll_refresh,
	onload: imogi_payroll_refresh,
});
