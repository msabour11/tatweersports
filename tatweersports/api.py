import frappe
import json



def log_changes(doc, method):
    # Take previous version from DB (excluding unsaved transient state)
    old_doc = frappe.get_doc(doc.doctype, doc.name).as_dict()

    changes = {}
    for key, new_val in doc.as_dict().items():
        old_val = old_doc.get(key)
        if old_val != new_val:
            changes[key] = {"old": old_val, "new": new_val}

    if changes:
        frappe.logger("sales_invoice_update").info(
            f"Changes in {doc.name}: {json.dumps(changes, indent=2, ensure_ascii=False, default=str)}"
        )
