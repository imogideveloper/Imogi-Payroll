frappe.listview_settings["Payroll Entry"] = {
	has_indicator_for_draft: 1,
	add_fields: ["posting_date", "start_date", "end_date", "periode", "status"],
	onload(listview) {
		ensure_payroll_entry_salary_month_sort(listview);
	},
	refresh(listview) {
		ensure_payroll_entry_salary_month_sort(listview);
		center_payroll_entry_columns(listview);
		setTimeout(() => center_payroll_entry_columns(listview), 150);
	},
	get_indicator(doc) {
		const status_color = {
			Draft: "red",
			Submitted: "blue",
			Queued: "orange",
			Failed: "red",
			Cancelled: "red",
		};
		return [__(doc.status), status_color[doc.status] || "gray", "status,=," + doc.status];
	},
};

/**
 * Kolom Posting Date dan Status rata tengah (judul dan isi). Kolom dicari lewat judulnya
 * karena urutan kolom bisa diubah lewat List View Settings.
 */
function center_payroll_entry_columns(listview) {
	const $result = listview?.$result;
	if (!$result?.length) {
		return;
	}
	const wanted = new Set([__("Posting Date"), __("Status")]);
	const $head_cols = $result.find(".list-row-head .list-row-col");
	const idx = [];
	$head_cols.each((i, el) => {
		if (wanted.has(el.textContent.trim())) {
			idx.push(i);
		}
	});
	if (!idx.length) {
		return;
	}
	const center = (cols) => idx.forEach((i) => cols[i] && (cols[i].style.textAlign = "center"));
	center($head_cols.toArray());
	$result.find(".list-row-container .list-row").each((_, row) => {
		center($(row).find(".list-row-col").toArray());
	});
}

function ensure_payroll_entry_salary_month_sort(listview) {
	if (!listview || listview.__imogi_salary_month_sort_applied) {
		return;
	}

	listview.__imogi_salary_month_sort_applied = true;
	const old_sort = listview.sort_by;

	// Payroll Entry uses 25-24 cutoff. List grouping must follow salary month
	// (posting_date/end_date), not start_date, otherwise Feb payroll appears under Jan.
	if (!old_sort || old_sort === "start_date" || old_sort === "modified") {
		listview.sort_by = "posting_date";
		listview.sort_order = "desc";
		listview.sort_selector?.set_value?.("posting_date", "desc");
		listview.save_view_user_settings?.({
			filters: listview.filter_area && listview.filter_area.get(),
			sort_by: "posting_date",
			sort_order: "desc",
		});

		if (old_sort !== "posting_date") {
			setTimeout(() => listview.refresh(), 100);
		}
	}
}
