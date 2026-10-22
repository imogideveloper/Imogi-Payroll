app_name = "imogi_payroll"
app_title = "Imogi Payroll"
app_publisher = "IMOGI"
app_description = "Imogi Payroll - Modul Perhitungan BPJS & PPh 21 untuk ERPNext Indonesia"
app_email = "hello@imogi.tech"
app_license = "MIT"
app_logo_url = "/assets/imogi_payroll/images/imogi-payroll-logo.svg"
app_home = "/desk/imogi-payroll"

add_to_apps_screen = [
    {
        "name": "imogi_payroll",
        "logo": app_logo_url,
        "title": "Imogi Payroll",
        "route": app_home,
        "has_permission": "frappe.permissions.check_app_permission",
        "sequence_id": 3,
    }
]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_css = "/assets/imogi_payroll/css/imogi_payroll_desk.css"
app_include_js = [
    "/assets/imogi_payroll/js/checkin_gate.js?v=1",
    # memasang kelas .imogi-wide saat berada di workspace Imogi Payroll
    "/assets/imogi_payroll/js/imogi_payroll_desk.js",
]

# include js, css files in header of web template
# web_include_css = "/assets/imogi_payroll/css/imogi_payroll.css"
# web_include_js = "/assets/imogi_payroll/js/imogi_payroll.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "imogi_payroll/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
    "Imogi Payroll Annual History": "public/js/imogi_payroll_annual_history.js",
    "Employee": "public/js/imogi_payroll_employee_form.js",
    "Imogi Payroll Settings": "public/js/imogi_payroll_form_layout.js",
    "Salary Slip": [
        "public/js/imogi_payroll_form_layout.js",
        "public/js/imogi_payroll_salary_slip.js",
    ],
    "Payroll Entry": [
        "public/js/imogi_payroll_form_layout.js",
        "public/js/imogi_payroll_entry.js",
    ],
    "Salary Structure": [
        "public/js/imogi_payroll_form_layout.js",
        "public/js/imogi_payroll_salary_structure.js",
    ],
    "Payroll Period": "public/js/imogi_payroll_form_layout.js",
    "Salary Component": "public/js/imogi_payroll_form_layout.js",
    "Bulk Salary Structure Assignment": "public/js/imogi_payroll_form_layout.js",
    "Salary Structure Assignment": [
        "public/js/imogi_payroll_form_layout.js",
        "public/js/imogi_payroll_ssa.js",
        "public/js/imogi_payroll_ssa_ux.js",
    ],
}
doctype_list_js = {
    "Payroll Entry": "public/js/imogi_payroll_entry_list.js",
    "Salary Structure Assignment": "public/js/imogi_payroll_ssa_list.js",
    "Salary Slip": "public/js/imogi_payroll_salary_slip_list.js",
}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Boot
# ----------

# force karyawan yang belum absen hari ini untuk mampir ke /checkin dulu
boot_session = "imogi_payroll.checkin_gate.boot_session"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
#	"methods": "imogi_payroll.utils.jinja_methods",
#	"filters": "imogi_payroll.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "imogi_payroll.install.before_install"
# after_install = "imogi_payroll.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "imogi_payroll.uninstall.before_uninstall"
# after_uninstall = "imogi_payroll.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps.
#
# `after_sync` is executed immediately after DocType sync while
# `after_migrate` runs later once all patches have been applied.
# Running both hooks would call the setup twice, so we only use
# `after_migrate`.
after_migrate = [
    "imogi_payroll.setup.setup_module.after_sync",
    "imogi_payroll.setup.install.after_migrate",
    "imogi_payroll.setup.salary_component_accounts.sync_salary_component_accounts"
]

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "imogi_payroll.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

override_doctype_class = {
    "Payroll Entry": "imogi_payroll.override.payroll_entry.CustomPayrollEntry",
    "Salary Slip": "imogi_payroll.override.salary_slip.CustomSalarySlip",
    # Perilaku SSA tidak diubah - override ini dipakai sebagai titik import
    # yang pasti, supaya get_bpjs_rate()/get_bpjs_cap() sudah terdaftar di
    # COMPONENT_EVAL_GLOBALS sebelum SSA mengevaluasi formula komponen.
    "Salary Structure Assignment": (
        "imogi_payroll.override.salary_structure_assignment.CustomSalaryStructureAssignment"
    ),
}

# Safe Eval Globals
# -----------------
# Fungsi tambahan untuk formula Salary Component (get_bpjs_rate/get_bpjs_cap)
# TIDAK didaftarkan lewat hooks. Frappe/HRMS tidak punya hook untuk itu -
# `salary_slip_globals` yang dulu ada di sini adalah nama karangan yang tidak
# pernah dibaca siapa pun. Pendaftarannya sekarang di
# imogi_payroll/override/component_eval_globals.py, yang menambal
# hrms.payroll.utils.COMPONENT_EVAL_GLOBALS - satu-satunya titik yang
# dilewati jalur Salary Slip MAUPUN Salary Structure Assignment.

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "Employee": {
        "on_update": "imogi_payroll.override.employee.on_update",
    },
    "Salary Structure": {
        # Sinkronisasi tabel employer dijalankan di before_validate, BUKAN
        # validate. validate milik HRMS berjalan LEBIH DULU daripada hook
        # app, dan di dalamnya validate_payment_days_based_dependent_component
        # membaca abbr setiap baris employer_contributions. Kalau sinkronisasi
        # baru berjalan sesudahnya, dokumen yang barisnya terlanjur tersimpan
        # tanpa abbr tidak akan pernah bisa disubmit - HRMS gagal lebih dulu
        # sebelum app sempat memperbaikinya.
        "before_validate": "imogi_payroll.payroll.employer_contributions.sync_salary_structure_employer_display",
        "validate": "imogi_payroll.utils.validate_salary_structure.validate_salary_structure_required_components",
    },
    "Salary Structure Assignment": {
        "validate": (
            "imogi_payroll.payroll.salary_structure_assignment"
            ".validate_salary_structure_assignment"
        ),
        "on_submit": (
            "imogi_payroll.payroll.salary_structure_assignment"
            ".handle_salary_structure_assignment_submit"
        ),
        "on_update_after_submit": (
            "imogi_payroll.payroll.salary_structure_assignment"
            ".update_submitted_salary_structure_assignment"
        ),
    },
    "Payroll Entry": {
        "validate": [
            "imogi_payroll.payroll.payroll_period_integration.validate_payroll_entry",
            "imogi_payroll.payroll.payroll_entry_summary.sync_summary_on_validate",
        ],
    },
    "Payroll Period": {
        "validate": "imogi_payroll.payroll.payroll_period_integration.validate_payroll_period"
    },
    "Salary Slip": {
        "validate": "imogi_payroll.override.salary_slip.strip_bpjs_hook",
        # Other apps' "validate" doc_events (e.g. imogi_finance's
        # validate_pph21_exemption) run AFTER this one and call
        # doc.calculate_net_pay(), which re-derives every deduction
        # amount from its salary component formula - silently undoing
        # the zero-out above. before_save/before_submit run strictly
        # after ALL "validate" hooks from every app (see document.py's
        # run_before_save_methods), so re-running the strip there
        # guarantees it is the last mutation before the amounts are
        # persisted, regardless of what any other app's validate hook
        # does in between.
        "before_save": "imogi_payroll.override.salary_slip.strip_bpjs_hook",
        "before_submit": "imogi_payroll.override.salary_slip.strip_bpjs_hook",
        # Frappe only runs "validate"/"before_save"/"before_submit" for
        # action="save"/"submit" - editing an already-Submitted doc
        # (allow_on_submit fields) takes the "update_after_submit"
        # action instead, which only fires before_update_after_submit.
        # Without this, exemption flags toggled after a slip is already
        # submitted would never re-trigger the strip.
        "before_update_after_submit": "imogi_payroll.override.salary_slip.strip_bpjs_hook",
        # override.* harus jalan duluan (hitung ulang slip), baru payroll_sync
        # yang mencatat liabilitas BPJS/PPh21 dan me-refresh ringkasan di
        # Payroll Entry induknya.
        "on_submit": [
            "imogi_payroll.override.salary_slip.on_submit",
            "imogi_payroll.api.payroll_sync.handle_salary_slip_submit",
        ],
        "on_cancel": [
            "imogi_payroll.override.salary_slip.on_cancel",
            "imogi_payroll.api.payroll_sync.handle_salary_slip_cancel",
        ],
    },
    "Employee Checkin": {
        "before_insert": "imogi_payroll.checkin_gate.force_server_time",
        "after_insert": "imogi_payroll.attendance.auto_attendance.auto_create_from_checkin"
    },
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
#	"all": [
#		"imogi_payroll.tasks.all"
#	],
#	"daily": [
#		"imogi_payroll.tasks.daily"
#	],
#	"hourly": [
#		"imogi_payroll.tasks.hourly"
#	],
#	"weekly": [
#		"imogi_payroll.tasks.weekly"
#	],
#	"monthly": [
#		"imogi_payroll.tasks.monthly"
#	],
# }

scheduler_events = {
    "daily": [
        "imogi_payroll.attendance.daily_attendance.process_yesterday_attendance",
        "imogi_payroll.payroll.salary_structure_assignment.sync_expired_salary_structure_assignments",
    ]
}

# Overriding Methods
# ------------------
# filter daftar karyawan di Payroll Entry ke yang punya SSA aktif saja
override_whitelisted_methods = {
    "hrms.payroll.doctype.payroll_entry.payroll_entry.employee_query":
        "imogi_payroll.payroll.payroll_entry.employee_query",
}

# Testing
# -------

# before_tests = "imogi_payroll.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
#	"frappe.desk.doctype.event.event.get_events": "imogi_payroll.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "imogi_payroll.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["imogi_payroll.utils.before_request"]
# after_request = ["imogi_payroll.utils.after_request"]

# Job Events
# ----------
# before_job = ["imogi_payroll.utils.before_job"]
# after_job = ["imogi_payroll.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
#	{
#		"doctype": "{doctype_1}",
#		"filter_by": "{filter_by}",
#		"redact_fields": ["{field_1}", "{field_2}"],
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_2}",
#		"filter_by": "{filter_by}",
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_3}",
#		"strict": False,
#	},
#	{
#		"doctype": "{doctype_4}"
#	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"imogi_payroll.auth.validate"
# ]

# Fixtures
# --------
# Fixtures are data that should be auto-imported when the app is installed
fixtures = [
    {
        "doctype": "Custom Field",
        "filters": [
            ["name", "in", [
                "Employee-imogi_payroll_tax_section",
                "Employee-tax_status",
                "Employee-exempt_from_pph21",
                "Employee-bebas_bpjs",
                "Employee-bebas_bpjs_kesehatan",
                "Employee-bebas_bpjs_jht",
                "Employee-bebas_bpjs_jp",
                "Employee-jkk_risk_level",
                "Employee-wajib_absen_sebelum_masuk",
                "Employee-id_section",
                "Employee-ktp_no",
                "Employee-npwp_no",
                "Employee-column_break_id",
                "Employee-ktp_attachment",
                "Employee-npwp_attachment",
                "Salary Slip-imogi_pph21_section",
                "Salary Slip-imogi_pph21_breakdown",
                "Salary Slip-pph21_amount",
                "Salary Slip-pph21_info",
                "Salary Slip-tax_type",
                "Payroll Entry-run_imogi_payroll",
                "Payroll Entry-run_imogi_payroll_december",
                "Payroll Entry-periode",
                "Payroll Entry-total_karyawan",
                "Payroll Entry-total_amount",
                "Salary Structure Assignment-meal_allowance",
                "Salary Structure Assignment-transport_allowance",
                "Salary Structure Assignment-assignment_contract_type",
                "Salary Structure Assignment-assignment_contract_tracking_section",
                "Salary Structure Assignment-previous_assignment_contract",
                "Salary Structure Assignment-assignment_contract_tracking_column",
                "Salary Structure Assignment-change_reason",
                "Salary Structure Assignment-renewed_by_assignment_contract",
                "Salary Structure Assignment-assignment_contract_history_section",
                "Salary Structure Assignment-assignment_contract_history",
                "Salary Structure Assignment-end_date",
                "Salary Structure Assignment-status",
                "Salary Structure Assignment-ssa_komponen_gaji_section",
                "Salary Structure Assignment-salary_component_amounts",
                "Salary Structure Assignment-assignment_contract_intro",
                "Salary Structure Assignment-ssa_legacy_fields_section",
                "Payroll Entry-payroll_period",
                "Payroll Entry-sb_periode_gaji_full",
                "Payroll Entry-payroll_sub_period",
                "Payroll Entry-cb_after_periode_gaji_full",
                "Payroll Entry-cb_ppa_status",
                "Payroll Entry-employer_contributions_section",
                "Payroll Entry-total_employer_contribution",
                "Payroll Entry-employer_contributions_summary",
                "Payroll Period-cutoff_start_day",
                "Payroll Period-column_break_cutoff",
                "Payroll Period-cutoff_end_day",
                "Payroll Period-sb_after_cutoff",
                "Payroll Period Date-period_label",
                "Salary Component-sequence_no",
                "Bulk Salary Structure Assignment-meal_allowance",
                "Bulk Salary Structure Assignment-transport_allowance"
            ]]
        ]
    },
    {
        # Tata letak / perilaku field bawaan HRMS yang disesuaikan untuk
        # payroll Indonesia. Hanya property setter yang field targetnya
        # benar-benar ada di v16 yang diikutkan.
        "doctype": "Property Setter",
        "filters": [
            ["name", "in", [
                "Attendance-column_break_18-hidden",
                "Attendance-details_section-hidden",
                "Employee Checkin-offshift-label",
                # Sengaja TIDAK memuat property setter insert_after untuk field
                # Employee milik imogi_payroll: posisinya sudah diatur di
                # custom_field.json. Versi imogi_finance mengacu ke tata letak
                # app itu dan di sini justru bikin rantai insert_after melingkar
                # (exempt_from_pph21 -> npwp_attachment -> ... -> exempt_from_pph21),
                # yang membuat Frappe membuang diam-diam semua checkbox bebas
                # PPh21/BPJS dari form tanpa pesan error apa pun.
                "Employee-employee_number-hidden",
                "Employee-employee_number-reqd",
                "Employee-naming_series-hidden",
                "Employee-naming_series-options",
                "Employee-naming_series-reqd",
                "Payroll Entry-column_break_13-hidden",
                "Payroll Entry-deduct_tax_for_unsubmitted_tax_exemption_proof-hidden",
                "Payroll Entry-employer_contributions_section-hidden",
                "Payroll Entry-employer_contributions_summary-hidden",
                "Payroll Entry-end_date-hidden",
                "Payroll Entry-end_date-in_standard_filter",
                "Payroll Entry-payroll_frequency-hidden",
                "Payroll Entry-payroll_payable_account-insert_after",
                "Payroll Entry-payroll_period-hidden",
                "Payroll Entry-periode-hidden",
                "Payroll Entry-posting_date-in_list_view",
                "Payroll Entry-posting_date-in_standard_filter",
                "Payroll Entry-start_date-hidden",
                "Payroll Entry-start_date-in_standard_filter",
                "Payroll Entry-status-insert_after",
                "Payroll Entry-total_employer_contribution-hidden",
                "Payroll Period Date-main-show_title_field_in_link",
                "Payroll Period Date-main-title_field",
                "Payroll Period-company-in_list_view",
                "Payroll Period-end_date-in_list_view",
                "Payroll Period-periods-hidden",
                "Payroll Period-periods-insert_after",
                "Payroll Period-section_break_5-hidden",
                "Payroll Period-section_break_5-label",
                "Payroll Period-start_date-in_list_view",
                "Salary Slip-company-in_list_view",
                "Salary Slip-employee-in_list_view",
                "Salary Slip-main-default_print_format",
                "Salary Slip-net_pay-in_list_view",
                "Salary Slip-rounded_total-hidden",
                "Salary Slip-rounded_total-print_hide",
                "Salary Slip-salary_structure-in_list_view",
                "Salary Structure Assignment-amended_from-hidden",
                "Salary Structure Assignment-assignment_contract_intro-hidden",
                "Salary Structure Assignment-assignment_contract_type-in_standard_filter",
                "Salary Structure Assignment-base-hidden",
                "Salary Structure Assignment-base-insert_after",
                "Salary Structure Assignment-column_break_9-hidden",
                "Salary Structure Assignment-column_break_kjvm-hidden",
                "Salary Structure Assignment-department-in_standard_filter",
                "Salary Structure Assignment-designation-in_standard_filter",
                "Salary Structure Assignment-employee_name-in_list_view",
                "Salary Structure Assignment-employee_name-in_standard_filter",
                "Salary Structure Assignment-end_date-allow_on_submit",
                "Salary Structure Assignment-from_date-in_list_view",
                "Salary Structure Assignment-from_date-in_standard_filter",
                "Salary Structure Assignment-leave_encashment_amount_per_day-hidden",
                "Salary Structure Assignment-main-field_order",
                "Salary Structure Assignment-main-title_field",
                "Salary Structure Assignment-meal_allowance-hidden",
                "Salary Structure Assignment-meal_allowance-in_list_view",
                "Salary Structure Assignment-previous_assignment_contract-in_standard_filter",
                "Salary Structure Assignment-renewed_by_assignment_contract-in_standard_filter",
                "Salary Structure Assignment-salary_component_amounts-allow_on_submit",
                "Salary Structure Assignment-salary_component_amounts-description",
                "Salary Structure Assignment-salary_component_amounts-label",
                "Salary Structure Assignment-section_break_17-hidden",
                "Salary Structure Assignment-section_break_7-label",
                "Salary Structure Assignment-ssa_komponen_gaji_section-description",
                "Salary Structure Assignment-ssa_komponen_gaji_section-label",
                "Salary Structure Assignment-status-options",
                "Salary Structure Assignment-transport_allowance-hidden",
                "Salary Structure Assignment-transport_allowance-in_list_view",
                "Salary Structure Assignment-variable-hidden"
            ]]
        ]
    },
    {
        "doctype": "Client Script",
        "filters": [
            ["name", "in", [
                "Imogi Payroll Salary Slip Grouping",
                "Imogi Payroll Salary Component Sort",
                "Imogi Payroll Entry List Script"
            ]]
        ]
    },
    {
        "doctype": "Salary Component",
        "validate": "imogi_payroll.override.salary_component.validate"
    },
    "Income Tax Slab",
    "Imogi Payroll PTKP Table",
    "Imogi Payroll TER Bracket Table",
    "Imogi Payroll TER Mapping Table",
    "Imogi Payroll Settings",
    {
        "doctype": "Report",
        "filters": [
            [
                "name",
                "in",
                [
                    "Imogi Payroll PPh21 Report",
                    "Imogi Payroll BPJS Report",
                    "Imogi Payroll BPJS Contribution Summary"
                ]
            ]
        ]
    },
    {
        "doctype": "Print Format",
        "filters": [
            [
                "name",
                "in",
                [
                    "Slip Gaji Imogi Payroll",
                    "Slip Gaji Modern"
                ]
            ]
        ]
    },
    {
        # Tanpa record ini Frappe membangun sidebar otomatis lewat
        # auto_generate_sidebar_from_module() dengan ikon seadanya
        # ('wallpaper', 'table', sebagian kosong, header 'hammer').
        # Fungsi itu melewati modul yang sudah punya record, jadi yang
        # ini yang dipakai.
        "doctype": "Workspace Sidebar",
        "filters": [["name", "in", ["Imogi Payroll"]]]
    },
]

after_install = "imogi_payroll.setup.install.after_install"
