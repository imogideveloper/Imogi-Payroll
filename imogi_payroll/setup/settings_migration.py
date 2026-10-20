import json
import os
from typing import Any, Optional

import frappe
from frappe.model.document import Document

def load_json(filename: str) -> Any:
    """
    Load a JSON file from the setup directory.
    """
    file_path = frappe.get_app_path("imogi_payroll", "setup", filename)
    if not os.path.exists(file_path):
        frappe.logger().warning(f"File not found: {file_path}")
        return None
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except Exception as e:
        frappe.logger().warning(f"Error loading {filename}: {str(e)}")
        return None

def import_imogi_payroll_ptkp_table_to_doctype() -> None:
    """
    Import default PTKP values into Imogi Payroll PTKP Table DocType.
    """
    ptkp_data = load_json("default_imogi_payroll_ptkp_table.json")
    if not ptkp_data or not ptkp_data[0].get("imogi_payroll_ptkp_table"):
        frappe.logger().warning("PTKP data not found or invalid format")
        return

    # Optional: Clear existing records
    frappe.db.sql("DELETE FROM `tabImogi Payroll PTKP Table`")

    settings = get_or_create_settings()

    for entry in ptkp_data[0]["imogi_payroll_ptkp_table"]:
        doc = frappe.get_doc({
            "doctype": "Imogi Payroll PTKP Table",
            "parent": settings.name,
            "parenttype": "Imogi Payroll Settings",
            "parentfield": "imogi_payroll_ptkp_table",
            "tax_status": entry["tax_status"],
            "ptkp_amount": entry["ptkp_amount"],
        })
        doc.insert(ignore_permissions=True)
    frappe.logger().info("Imported default Imogi Payroll PTKP Table DocType")

def import_ter_mapping_to_doctype() -> None:
    """
    Import default TER mapping into Imogi Payroll TER Mapping Table DocType.
    """
    ter_mapping_data = load_json("default_ter_mapping.json")
    if not ter_mapping_data:
        frappe.logger().warning("TER mapping data not found or invalid format")
        return

    frappe.db.sql("DELETE FROM `tabImogi Payroll TER Mapping Table`")

    settings = get_or_create_settings()

    for entry in ter_mapping_data:
        doc = frappe.get_doc({
            "doctype": "Imogi Payroll TER Mapping Table",
            "parent": settings.name,
            "parenttype": "Imogi Payroll Settings",
            "parentfield": "imogi_payroll_ter_mapping_table",
            "tax_status": entry["tax_status"],
            "ter_code": entry["ter_code"],
        })
        doc.insert(ignore_permissions=True)
    frappe.logger().info("Imported default Imogi Payroll TER Mapping Table DocType")

def import_ter_brackets_to_doctype() -> None:
    """
    Import default TER brackets into Imogi Payroll TER Bracket Table DocType.
    """
    ter_rate_data = load_json("default_ter_rate.json")
    if not ter_rate_data:
        frappe.logger().warning("TER rate data not found or invalid format")
        return

    frappe.db.sql("DELETE FROM `tabImogi Payroll TER Bracket Table`")

    settings = get_or_create_settings()

    for ter_code_data in ter_rate_data:
        ter_code = ter_code_data["ter_code"]
        for bracket in ter_code_data["brackets"]:
            doc = frappe.get_doc({
                "doctype": "Imogi Payroll TER Bracket Table",
                "parent": settings.name,
                "parenttype": "Imogi Payroll Settings",
                "parentfield": "imogi_payroll_ter_bracket_table",
                "ter_code": ter_code,
                "min_income": bracket["min_income"],
                "max_income": bracket["max_income"] if bracket["max_income"] is not None else 0,
                "rate_percent": bracket["rate_percent"],
            })
            doc.insert(ignore_permissions=True)
    frappe.logger().info("Imported default Imogi Payroll TER Bracket Table DocType")

def import_imogi_payroll_ptkp_table_to_settings() -> None:
    """(Optional) Import PTKP values into Imogi Payroll Settings for display/reference."""
    ptkp_data = load_json("default_imogi_payroll_ptkp_table.json")
    if not ptkp_data or not ptkp_data[0].get("imogi_payroll_ptkp_table"):
        frappe.logger().warning("PTKP data not found or invalid format")
        return
    settings = get_or_create_settings()
    if not settings:
        return
    settings.imogi_payroll_ptkp_table = []
    for entry in ptkp_data[0]["imogi_payroll_ptkp_table"]:
        settings.append(
            "imogi_payroll_ptkp_table", {"tax_status": entry["tax_status"], "ptkp_amount": entry["ptkp_amount"]}
        )
    settings.save()
    frappe.logger().info("Imported default PTKP table to Settings")

def import_ter_mapping_to_settings() -> None:
    """(Optional) Import TER mapping into Imogi Payroll Settings for display/reference."""
    ter_mapping_data = load_json("default_ter_mapping.json")
    if not ter_mapping_data:
        frappe.logger().warning("TER mapping data not found or invalid format")
        return
    settings = get_or_create_settings()
    if not settings:
        return
    settings.imogi_payroll_ter_mapping_table = []
    for entry in ter_mapping_data:
        settings.append(
            "imogi_payroll_ter_mapping_table", {"tax_status": entry["tax_status"], "ter_code": entry["ter_code"]}
        )
    settings.save()
    frappe.logger().info("Imported default TER mapping to Settings")

def import_ter_brackets_to_settings() -> None:
    """(Optional) Import TER brackets into Imogi Payroll Settings for display/reference."""
    ter_rate_data = load_json("default_ter_rate.json")
    if not ter_rate_data:
        frappe.logger().warning("TER rate data not found or invalid format")
        return
    settings = get_or_create_settings()
    if not settings:
        return
    settings.imogi_payroll_ter_bracket_table = []
    for ter_code_data in ter_rate_data:
        ter_code = ter_code_data["ter_code"]
        for bracket in ter_code_data["brackets"]:
            settings.append(
                "imogi_payroll_ter_bracket_table",
                {
                    "ter_code": ter_code,
                    "min_income": bracket["min_income"],
                    "max_income": bracket["max_income"] if bracket["max_income"] is not None else 0,
                    "rate_percent": bracket["rate_percent"],
                },
            )
    settings.save()
    frappe.logger().info("Imported default TER brackets to Settings")

def get_or_create_settings() -> Optional[Document]:
    """Get or create Imogi Payroll Settings document"""
    if not frappe.db.exists("Imogi Payroll Settings", "Imogi Payroll Settings"):
        settings = frappe.new_doc("Imogi Payroll Settings")
        settings.name = "Imogi Payroll Settings"
        settings.pph21_method = "TER"
        settings.validate_tax_status_strict = 1
        settings.salary_slip_use_component_cache = 1
        settings.auto_queue_salary_slip = 0
        settings.bpjs_health_employer_rate = 4.0
        settings.bpjs_health_employer_cap = 12000000
        settings.bpjs_health_employee_rate = 1.0
        settings.bpjs_health_employee_cap = 12000000
        settings.bpjs_jht_employer_rate = 3.7
        settings.bpjs_jht_employer_cap = 9077600
        settings.bpjs_jht_employee_rate = 2.0
        settings.bpjs_jht_employee_cap = 9077600
        settings.bpjs_jkk_rate = 0.24
        settings.bpjs_jkk_cap = 9077600
        settings.bpjs_jkm_rate = 0.3
        settings.bpjs_jkm_cap = 9077600
        settings.bpjs_pension_employer_rate = 2.0
        settings.bpjs_pension_employer_cap = 9077600
        settings.bpjs_pension_employee_rate = 1.0
        settings.bpjs_pension_employee_cap = 9077600
        settings.biaya_jabatan_rate = 5.0
        settings.biaya_jabatan_cap = 6000000
        settings.fallback_income_tax_slab = None
        settings.insert()
        frappe.logger().info("Created new Imogi Payroll Settings")
        return settings
    else:
        return frappe.get_doc("Imogi Payroll Settings", "Imogi Payroll Settings")

def setup_default_settings() -> None:
    """
    Setup default Imogi Payroll settings AND migrate master data to DocType Tables.
    This function is called from setup_module.py after_sync.
    """
    try:
        # Migrate master tables to DocType
        import_imogi_payroll_ptkp_table_to_doctype()
        import_ter_mapping_to_doctype()
        import_ter_brackets_to_doctype()

        # (optional) Also import to Settings for display/reference
        import_imogi_payroll_ptkp_table_to_settings()
        import_ter_mapping_to_settings()
        import_ter_brackets_to_settings()

        frappe.db.commit()
        frappe.logger().info("Completed Imogi Payroll settings and data migration")
    except Exception as e:
        frappe.db.rollback()
        frappe.logger().error(f"Error in Imogi Payroll settings/data migration: {str(e)}")
        raise

@frappe.whitelist()
def run_settings_migration() -> str:
    """
    Run settings + master table migration manually.
    Can be called from client side.
    """
    try:
        setup_default_settings()
        return "Imogi Payroll settings and data migration completed successfully"
    except Exception as e:
        return f"Error in Imogi Payroll settings/data migration: {str(e)}"