import frappe


def run():
    frappe.set_user("Administrator")

    log = []

    companies = frappe.get_all("Company", pluck="name")
    log.append(f"Companies found: {companies}")

    for company_name in companies:
        tdr = frappe.new_doc("Transaction Deletion Record")
        tdr.company = company_name
        tdr.process_in_single_transaction = 1
        # Non-empty placeholder so validate() does NOT auto-fill the default
        # master-data ignore list (Employee/Customer/Supplier/Account/etc) -
        # we want those gone too for a true reset, not just transactions.
        tdr.append("doctypes_to_be_ignored", {"doctype_name": "Transaction Deletion Record"})
        tdr.insert(ignore_permissions=True)
        log.append(f"Created {tdr.name} for company {company_name}")

        result = tdr.generate_to_delete_list()
        log.append(f"To-delete list generated: {result}")

        tdr.reload()
        tdr.submit()
        tdr.reload()
        log.append(f"TDR {tdr.name} status after submit: {tdr.status}")
        if tdr.status == "Failed":
            log.append(f"ERROR LOG: {tdr.error_log}")
        else:
            try:
                frappe.delete_doc("Company", company_name, force=True, ignore_permissions=True)
                log.append(f"Deleted Company {company_name}")
            except Exception as e:
                log.append(f"Failed to delete Company {company_name}: {e}")

    frappe.db.set_single_value("System Settings", "setup_complete", 0)
    frappe.db.set_default("Company", "")
    try:
        frappe.db.set_single_value("Global Defaults", "default_company", "")
    except Exception as e:
        log.append(f"Global Defaults reset skipped: {e}")

    frappe.clear_cache()
    frappe.db.commit()
    log.append("DONE: setup_complete reset to 0")

    with open("/tmp/reset_rcm_result.log", "w") as f:
        f.write("\n".join(log))

    for line in log:
        print(line)
