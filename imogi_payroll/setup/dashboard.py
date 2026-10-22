"""Number Card dan Dashboard Chart untuk workspace Imogi Payroll.

Workspace hanya MENYIMPAN NAMA kartu dan grafiknya, bukan definisinya.
Selama ini kelima kartu dan dua grafik itu hanya ada di database tempat
mereka dibuat lewat UI, sehingga site hasil install baru menampilkan
workspace dengan bagian "Ringkasan Payroll" dan "Tren" yang kosong
melompong - persis yang terjadi di rcm.imogi.co.id.

Didefinisikan di sini supaya ikut terbawa ke site mana pun. Idempoten:
dipanggil pada after_install dan after_migrate.
"""

import frappe

MODULE = "Imogi Payroll"

#: Dasar yang sama untuk semua kartu; hanya pembeda yang ditulis di bawah.
_KARTU_DASAR = {
    "type": "Document Type",
    "is_public": 1,
    "is_standard": 0,
    "module": MODULE,
    "show_percentage_stats": 1,
    "stats_time_interval": "Monthly",
    # Tanpa ini Frappe memendekkan angka jadi "1,2k". Dengan format angka
    # Indonesia, pemendekan itu pernah menghasilkan "Rp NaN".
    "show_full_number": 1,
    "currency": "IDR",
}

_BULAN_INI = [
    ["Salary Slip", "docstatus", "=", 1, False],
    ["Salary Slip", "end_date", "Timespan", "this month", False],
]

NUMBER_CARDS: list[dict] = [
    {
        "name": "Penugasan Gaji Aktif",
        "label": "Penugasan Gaji Aktif",
        "document_type": "Salary Structure Assignment",
        "function": "Count",
        "filters_json": [["Salary Structure Assignment", "docstatus", "=", 1, False]],
        "color": "#FF8C6B",
    },
    {
        "name": "Total PPh 21 (Bulan Ini)",
        "label": "Total PPh 21 (Bulan Ini)",
        "document_type": "Salary Slip",
        "function": "Sum",
        "aggregate_function_based_on": "pph21_amount",
        "filters_json": _BULAN_INI,
        "color": "#ECAD4B",
    },
    {
        "name": "Total Gaji Dibayar (Bulan Ini)",
        "label": "Total Gaji Dibayar (Bulan Ini)",
        "document_type": "Salary Slip",
        "function": "Sum",
        "aggregate_function_based_on": "net_pay",
        "filters_json": _BULAN_INI,
        "color": "#7575FF",
    },
    {
        "name": "Slip Gaji Bulan Ini",
        "label": "Slip Gaji Bulan Ini",
        "document_type": "Salary Slip",
        "function": "Count",
        "filters_json": _BULAN_INI,
        "color": "#449CF0",
    },
    {
        "name": "Karyawan Aktif",
        "label": "Karyawan Aktif",
        "document_type": "Employee",
        "function": "Count",
        "filters_json": [["Employee", "status", "=", "Active", False]],
        "color": "#29CD42",
    },
]

_GRAFIK_DASAR = {
    "chart_type": "Sum",
    "document_type": "Salary Slip",
    "based_on": "start_date",
    "timespan": "Last Year",
    "time_interval": "Monthly",
    "filters_json": [["Salary Slip", "docstatus", "=", 1, False]],
    "is_public": 1,
    "is_standard": 0,
    "module": MODULE,
    "currency": "IDR",
}

CHARTS: list[dict] = [
    {
        "name": "Total Potongan Bulanan",
        "chart_name": "Total Potongan Bulanan",
        "value_based_on": "total_deduction",
        "type": "Line",
        "color": "#ECAD4B",
    },
    {
        "name": "Tren Gaji Bulanan",
        "chart_name": "Tren Gaji Bulanan",
        "value_based_on": "net_pay",
        "type": "Bar",
        "color": "#449CF0",
    },
]


def _upsert(doctype: str, nilai: dict) -> bool:
    """Buat bila belum ada; kalau sudah, selaraskan definisinya.

    Yang diselaraskan hanya definisi (sumber data, filter, fungsi). Posisi
    di workspace tidak disentuh karena itu milik dokumen Workspace.
    """
    nama = nilai["name"]
    data = dict(nilai)
    for k, v in list(data.items()):
        if isinstance(v, (list, dict)):
            data[k] = frappe.as_json(v)

    if frappe.db.exists(doctype, nama):
        doc = frappe.get_doc(doctype, nama)
        berubah = False
        for k, v in data.items():
            if k == "name":
                continue
            if doc.get(k) != v:
                doc.set(k, v)
                berubah = True
        if berubah:
            doc.save(ignore_permissions=True)
        return berubah

    frappe.get_doc({"doctype": doctype, **data}).insert(ignore_permissions=True)
    return True


def setup_dashboard() -> None:
    """Pastikan kartu dan grafik workspace ada. Aman dipanggil berulang."""
    if not frappe.db.exists("Module Def", MODULE):
        return

    dibuat = 0
    for kartu in NUMBER_CARDS:
        if _upsert("Number Card", {**_KARTU_DASAR, **kartu}):
            dibuat += 1

    for grafik in CHARTS:
        if _upsert("Dashboard Chart", {**_GRAFIK_DASAR, **grafik}):
            dibuat += 1

    if dibuat:
        print(f"✓ Dashboard workspace: {dibuat} kartu/grafik disiapkan")
