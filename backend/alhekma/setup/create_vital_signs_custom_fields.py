# Al Hekma Hospital — Vital Signs custom fields
# bench --site alhekma.local execute alhekma.setup.create_vital_signs_custom_fields.run


def run():
    """
    Create the hospital-specific SpO2 field on Vital Signs.

    Idempotent: no-op if the Custom Field already exists.
    Does not modify the Healthcare core DocType.
    """

    import frappe

    fieldname = "spo2"

    if frappe.db.exists(
        "Custom Field",
        {"dt": "Vital Signs", "fieldname": fieldname},
    ):
        print("Already exists: Vital Signs.spo2 — no action taken.")
        return {"status": "already_exists", "fieldname": fieldname}

    doc = frappe.get_doc(
        {
            "doctype": "Custom Field",
            "dt": "Vital Signs",
            "fieldname": fieldname,
            "label": "SpO₂ (%)",
            "fieldtype": "Float",
            "precision": 2,
            "insert_after": "bp_diastolic",
            "in_list_view": 1,
            "description": "Oxygen saturation recorded by the clinical staff.",
        }
    )
    doc.insert(ignore_permissions=True)
    frappe.db.commit()

    print("=== Vital Signs custom field created ===")
    print(f"  fieldname : {doc.fieldname}")
    print(f"  label     : {doc.label}")
    print(f"  fieldtype : {doc.fieldtype}")
    print(f"  insert_after: {doc.insert_after}")
    print("STATUS: OK")

    return {"status": "created", "fieldname": doc.fieldname}
