"""Perbarui formula JKK di Salary Structure yang sudah terlanjur dibuat.

Mengubah formula di master Salary Component TIDAK merambat ke Salary
Structure: tiap baris struktur menyimpan salinan formulanya sendiri, dan
set_missing_values() milik HRMS hanya mengisinya kalau formula DAN amount
sama-sama kosong. Jadi tanpa patch ini, struktur yang dibuat sebelum
perbaikan akan terus memakai tarif JKK cadangan 0,24% untuk semua
karyawan, berapa pun tingkat risikonya.

Penggantian sengaja dicocokkan PERSIS dengan formula lama. Struktur yang
formulanya sudah disesuaikan sendiri oleh pengguna tidak ikut tersentuh.
"""

import frappe

GANTI = [
    (
        "BPJS JKK Employer",
        "base * get_bpjs_rate('bpjs_jkk_rate') / 100",
        "base * get_jkk_rate(employee) / 100",
    ),
    (
        "Contra BPJS JKK Employer",
        "(base if base <= get_bpjs_cap('bpjs_jkk_cap') "
        "else get_bpjs_cap('bpjs_jkk_cap')) * get_bpjs_rate('bpjs_jkk_rate') / 100",
        "(base if base <= get_bpjs_cap('bpjs_jkk_cap') "
        "else get_bpjs_cap('bpjs_jkk_cap')) * get_jkk_rate(employee) / 100",
    ),
]


def execute():
    total = 0
    for komponen, lama, baru in GANTI:
        # Ditulis langsung lewat SQL: Salary Structure umumnya sudah
        # disubmit, dan menyimpan ulang dokumennya akan memicu validasi
        # penuh yang tidak ada hubungannya dengan perubahan ini.
        hasil = frappe.db.sql(
            """
            update `tabSalary Detail`
            set formula = %(baru)s
            where parenttype = 'Salary Structure'
              and salary_component = %(komponen)s
              and formula = %(lama)s
            """,
            {"komponen": komponen, "lama": lama, "baru": baru},
        )
        n = frappe.db.sql(
            """
            select count(*) from `tabSalary Detail`
            where parenttype = 'Salary Structure'
              and salary_component = %(komponen)s
              and formula = %(baru)s
            """,
            {"komponen": komponen, "baru": baru},
        )[0][0]
        total += n
        print(f"  {komponen}: {n} baris memakai tarif per tingkat risiko")

    if total:
        frappe.clear_cache()
