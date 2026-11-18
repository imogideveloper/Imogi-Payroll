import frappe
from frappe.utils import today, add_days, getdate, cint
from erpnext.setup.doctype.employee.employee import is_holiday


def get_auto_attendance_shift(employee, on_date):
    """Shift Type karyawan pada tanggal itu bila auto attendance menyala, selain itu None.

    Urutan: Shift Assignment aktif yang mencakup tanggal, lalu Employee.default_shift."""
    row = frappe.db.sql(
        """select shift_type from `tabShift Assignment`
           where employee = %s and docstatus = 1 and status = 'Active'
             and start_date <= %s and (end_date is null or end_date >= %s)
           order by start_date desc limit 1""",
        (employee, on_date, on_date),
    )
    shift = row[0][0] if row else frappe.db.get_value("Employee", employee, "default_shift")
    if not shift:
        return None
    values = frappe.db.get_value(
        "Shift Type", shift, ["name", "enable_auto_attendance", "process_attendance_after", "holiday_list"], as_dict=True
    )
    if not values or not cint(values.enable_auto_attendance):
        return None
    return values


def _is_off_day(employee, on_date, shift):
    """Hari libur menurut Holiday List shift; bila shift tanpa Holiday List, menurut Holiday List
    karyawan atau default Company (Minggu dan hari besar)."""
    if shift.holiday_list:
        return bool(frappe.db.exists("Holiday", {"parent": shift.holiday_list, "holiday_date": on_date}))
    return bool(is_holiday(employee, on_date, raise_exception=False))


def process_yesterday_attendance(for_date=None):
    """Tandai Absent otomatis untuk karyawan yang tidak punya absensi di hari kerja kemarin.

    Pengaman (semua harus terpenuhi, kalau tidak, karyawan itu dilewati):
      a. Imogi Payroll Settings.auto_mark_absent_enabled dicentang (default mati: job tidak berbuat apa-apa).
      b. Karyawan punya shift (Shift Assignment aktif atau Employee.default_shift) dengan
         Shift Type.enable_auto_attendance = 1.
      c. Tanggalnya hari kerja (bukan hari libur menurut Holiday List shift, karyawan, atau Company)
         dan masih dalam masa kerja (date_of_joining sampai relieving_date).
      d. Tanggalnya sama atau setelah Shift Type.process_attendance_after.
      e. Tanggalnya sudah lewat (bukan hari ini atau depan), sehingga HR sudah punya kesempatan
         koreksi di hari yang sama.
    `for_date` hanya untuk uji manual; scheduler memanggil tanpa argumen (kemarin)."""

    if not cint(frappe.db.get_single_value("Imogi Payroll Settings", "auto_mark_absent_enabled")):
        return

    yesterday = getdate(for_date) if for_date else getdate(add_days(today(), -1))
    if yesterday >= getdate(today()):
        return

    employees = frappe.get_all("Employee",
        filters={"status": "Active"},
        fields=["name", "employee_name", "company", "date_of_joining", "relieving_date"]
    )

    for emp in employees:
        # Bukan hari kerja karyawan ini: belum masuk atau sudah keluar
        if emp.date_of_joining and getdate(emp.date_of_joining) > yesterday:
            continue
        if emp.relieving_date and getdate(emp.relieving_date) < yesterday:
            continue

        shift = get_auto_attendance_shift(emp.name, yesterday)
        if not shift:
            continue
        if shift.process_attendance_after and yesterday < getdate(shift.process_attendance_after):
            continue
        # Hari libur (Minggu / hari besar): kerja di hari libur dibayar lewat lembur, bukan Absent
        if _is_off_day(emp.name, yesterday, shift):
            continue

        existing = frappe.db.exists("Attendance", {
            "employee": emp.name,
            "attendance_date": yesterday
        })

        if existing:
            continue

        has_checkin = frappe.db.exists("Employee Checkin", {
            "employee": emp.name,
            "time": ["between", [f"{yesterday} 00:00:00", f"{yesterday} 23:59:59"]]
        })

        if not has_checkin:
            create_absent_attendance(emp, yesterday)


def create_absent_attendance(employee_data, date):
    """Create Absent attendance"""
    
    try:
        attendance = frappe.get_doc({
            "doctype": "Attendance",
            "employee": employee_data.name,
            "employee_name": employee_data.employee_name,
            "attendance_date": date,
            "status": "Absent",
            "company": employee_data.company,
            "working_hours": 0,
            "naming_series": "HR-ATT-.YYYY.-"
        })
        
        # Dibuat sistem, bukan koreksi HR: lewati validasi koreksi absensi manual
        attendance.flags.imogi_system_attendance = True
        attendance.insert(ignore_permissions=True)
        attendance.submit()
        frappe.db.commit()
        
    except Exception as e:
        frappe.log_error(message=frappe.get_traceback(), title=f"Absent Attendance Failed")
