import frappe
import json

log = frappe.logger("sales_invoice_updated", allow_site=True)


def log_changes(doc, method):
    try:
        doc_before_save = doc.get_doc_before_save()

        if not doc_before_save:
            log.info(f"New Sales Invoice created: {doc.name}")
            return

        changes = []
        for field in doc.meta.fields:
            old_value = doc_before_save.get(field.fieldname)
            new_value = doc.get(field.fieldname)
            if old_value != new_value:
                changes.append(
                    f"  - Field '{field.fieldname}': '{old_value}' -> '{new_value}'"
                )

        if changes:
            changes_str = "\n".join(changes)
            log.error(
                f"Sales Invoice {doc.name} was updated by {frappe.session.user}:\n{changes_str}"
            )
        else:
            log.info(
                f"Sales Invoice {doc.name} was saved, but no data fields were changed."
            )

    except Exception as e:
        log.error(
            f"Error logging changes for {doc.name}: {e}\n{frappe.get_traceback()}"
        )


# simple version
# def log_changes(doc, method):
#     if not doc.get("_doc_before_save"):
#         return

#     old_doc = doc._doc_before_save.as_dict()
#     new_doc = doc.as_dict()

#     changes = {}
#     for key, new_val in new_doc.items():
#         old_val = old_doc.get(key)
#         if old_val != new_val:
#             changes[key] = {"old": old_val, "new": new_val}

#     if changes:
#         log.error(
#             f"Sales Invoice Changes [{doc.name}]: {json.dumps(changes, indent=2, ensure_ascii=False, default=str)}"
#         )
