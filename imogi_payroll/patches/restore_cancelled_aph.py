import frappe

def execute():
    """Restore Payroll Annual History yang ter-cancel karena salary slip di-cancel."""
    cancelled_aph = frappe.get_all(
        "Payroll Annual History",
        filters={"docstatus": 2},
        fields=["name"]
    )
    for aph in cancelled_aph:
        frappe.db.set_value("Payroll Annual History", aph.name, "docstatus", 1)
        frappe.logger("imogi_payroll").info(f"Restored APH {aph.name} from Cancelled to Submitted")
    
    frappe.db.commit()
    print(f"✅ Restored {len(cancelled_aph)} cancelled Payroll Annual History records")
