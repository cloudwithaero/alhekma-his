# Al Hekma Hospital — Property Setter application
# bench --site alhekma.local execute alhekma.setup.apply_property_setters.allow_appointments_fetch_from


def allow_appointments_fetch_from():
    """
    Create a Property Setter that clears fetch_from on
    Healthcare Service Unit.allow_appointments.

    This allows allow_appointments to be set per leaf HSU by the
    AlHekmaHealthcareServiceUnit override instead of being forcibly
    inherited from the linked Healthcare Service Unit Type on every save.

    Scope: exactly one Property Setter record.
    No HSU records, no HSU Type records, no core files are touched.
    Idempotent: no-op if the record already exists.
    """
    import frappe

    ps_name = "Healthcare Service Unit-allow_appointments-fetch_from"

    if frappe.db.exists("Property Setter", ps_name):
        print(f"Already exists: {ps_name} — no action taken.")
        return {"status": "already_exists", "name": ps_name}

    doc = frappe.new_doc("Property Setter")
    doc.doctype_or_field   = "DocField"
    doc.doc_type           = "Healthcare Service Unit"
    doc.field_name         = "allow_appointments"
    doc.property           = "fetch_from"
    doc.property_type      = "Data"
    doc.value              = ""
    doc.is_system_generated = 0
    doc.insert(ignore_permissions=True)
    frappe.db.commit()

    print("=== Property Setter created ===")
    print(f"  name             : {doc.name}")
    print(f"  doctype_or_field : {doc.doctype_or_field}")
    print(f"  doc_type         : {doc.doc_type}")
    print(f"  field_name       : {doc.field_name}")
    print(f"  property         : {doc.property}")
    print(f"  property_type    : {doc.property_type}")
    print(f"  value            : '{doc.value}'")
    print(f"  is_system_generated: {doc.is_system_generated}")
    print("STATUS: OK")

    return {"status": "created", "name": doc.name}
