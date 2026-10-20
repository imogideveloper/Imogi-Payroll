// Imogi Payroll: shared label-left / input-right form layout, reused across
// every doctype related to this app (not just Employee). Each field is only
// re-flowed INSIDE its own wrapper (label column + input column) - the
// outer wrapper/column width is left untouched, so any native multi-column
// grouping a doctype already has stays intact; only the label-above-input
// stacking inside each field becomes label-left/input-right.

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
		"margin-bottom": "0",
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
}

// Checkbox markup is <div class="checkbox"><label><input-area/><disp-area/>
// <label-area/><help/></label><p class="help-box">...</p></div> - label text
// and checkbox are siblings inside one <label>, and the description is a
// separate sibling below that whole label. To get a clean [label | checkbox
// + description] layout, input-area/disp-area/help and the help-box
// paragraph are moved into one new right-hand column that's itself a flex
// row, so the checkbox and the first line of the description sit on the
// same line (help-box is a <p>, block-level, so it forces a new line unless
// it's a flex sibling here rather than stacked underneath).
function imogi_payroll_style_check_field($wrapper) {
	const $checkbox_div = $wrapper.find(".checkbox").first();
	if (!$checkbox_div.length) return;
	if ($checkbox_div.hasClass("imogi-payroll-styled")) return; // idempotent across refreshes
	$checkbox_div.addClass("imogi-payroll-styled");

	const $label = $checkbox_div.find("> label").first();
	if (!$label.length) return;

	const $label_area = $label.children(".label-area");
	const $help_box = $wrapper.find(".help-box");

	const $right_col = $('<div class="imogi-payroll-check-right"></div>').css({
		flex: "1 1 auto",
		"min-width": "0",
		display: "flex",
		"align-items": "flex-start",
		gap: "8px",
	});
	$label.children(".input-area, .disp-area, .help").appendTo($right_col);
	$help_box.appendTo($right_col).css({ margin: "0", flex: "1 1 auto", "min-width": "0" });
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

		field.$wrapper.closest(".form-column").css({
			"margin-bottom": "0",
			"padding-bottom": "0",
		});
	});
}

// Frappe centers every form section at --page-max-width (900px by default),
// leaving a lot of empty space on wide screens. Override that variable on
// the form's own wrapper only, so it cascades to every .section-head /
// .section-body inside THIS form without touching any other doctype.
function imogi_payroll_widen_form(frm) {
	if (frm.wrapper) {
		$(frm.wrapper).css("--page-max-width", "1400px");
	}
}

function imogi_payroll_generic_refresh(frm) {
	imogi_payroll_widen_form(frm);
	imogi_payroll_apply_horizontal_layout(frm);
}

// Doctypes this layout applies to - everything Imogi Payroll has added
// custom fields to, plus our own settings doctype. Deliberately excludes
// child-table doctypes (PTKP/TER tables, Annual History Child) since those
// render as grid rows, not a standalone form, and excludes Employee (which
// has its own more tailored script, imogi_payroll_employee_form.js).
// NOTE: menambah doctype di sini saja tidak cukup - file ini hanya dimuat
// pada doctype yang terdaftar di doctype_js (hooks.py). Keduanya harus sejalan.
const IMOGI_PAYROLL_GENERIC_LAYOUT_DOCTYPES = [
	"Imogi Payroll Settings",
	"Salary Slip",
	"Salary Structure",
	"Payroll Entry",
	"Payroll Period",
	"Salary Component",
	"Salary Structure Assignment",
	"Bulk Salary Structure Assignment",
];

IMOGI_PAYROLL_GENERIC_LAYOUT_DOCTYPES.forEach((doctype) => {
	frappe.ui.form.on(doctype, {
		refresh: imogi_payroll_generic_refresh,
		onload: imogi_payroll_generic_refresh,
	});
});
