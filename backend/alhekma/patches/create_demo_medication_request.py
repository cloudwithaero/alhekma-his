# Al Hekma Hospital — DEMO Medication Request end-to-end
#
# PURPOSE: Create the minimal chain of master data needed to save ONE
# real Medication Request, ordered by the TEST doctor (test-027,
# Physician role), so you can see it show up live in the pharmacy's
# Medication Request list (test-035, Pharmacy role).
#
# EVERYTHING created here is clearly labeled TEST/DEMO — not real
# hospital data, not a real patient, not a real practitioner. This is
# purely to exercise the workflow end-to-end. Safe to delete afterward.
#
# Run with:
#   bench --site alhekma.local execute alhekma.patches.create_demo_medication_request.run
#
# Safe to re-run: skips anything that already exists.

import frappe
from frappe.utils import nowdate, nowtime

DOCTOR_USER = "test-027@alhekma.local"


def _get_or_create(doctype, filters, values):
    name = frappe.db.exists(doctype, filters)
    if name:
        return name if isinstance(name, str) else frappe.db.get_value(doctype, filters, "name")
    doc = frappe.get_doc({"doctype": doctype, **values})
    doc.insert(ignore_permissions=True)
    return doc.name


def run():
    company = frappe.db.get_value("Company", {}, "name")
    if not company:
        frappe.throw("No Company found on this site — cannot proceed.")

    # 1. Code System + Code Value (for Medication Request's "Status" field)
    code_system = _get_or_create(
        "Code System",
        {"code_system": "AlHekma Local Codes (TEST)"},
        {
            "code_system": "AlHekma Local Codes (TEST)",
            "uri": "urn:alhekma:local-test-codes",
            "description": "TEST/DEMO code system — not a real terminology standard.",
        },
    )
    status_code = _get_or_create(
        "Code Value",
        {"code_value": "requested", "code_system": code_system},
        {
            "code_system": code_system,
            "code_value": "requested",
            "display": "Requested (TEST)",
        },
    )

    # 2. Dosage Form + Prescription Dosage
    dosage_form = _get_or_create(
        "Dosage Form", {"dosage_form": "Tablet (TEST)"}, {"dosage_form": "Tablet (TEST)"}
    )
    dosage = _get_or_create(
        "Prescription Dosage",
        {"dosage": "1 tablet twice daily (TEST)"},
        {"dosage": "1 tablet twice daily (TEST)"},
    )

    # 3. A plain Item to stand in for the medication (bypassing the full
    # Medication-doctype auto-item-creation flow, which needs its own
    # price list / item group setup — out of scope for this demo)
    item_code = "TEST-MED-PARACETAMOL-500"
    if not frappe.db.exists("Item", item_code):
        frappe.get_doc({
            "doctype": "Item",
            "item_code": item_code,
            "item_name": "Paracetamol 500mg (TEST item — not real catalogue data)",
            "item_group": frappe.db.get_value("Item Group", {}, "name") or "All Item Groups",
            "is_stock_item": 0,
            "stock_uom": "Nos",
        }).insert(ignore_permissions=True)

    # 4. TEST Patient
    patient_name = _get_or_create(
        "Patient",
        {"first_name": "TEST - Demo Patient"},
        {"first_name": "TEST - Demo Patient", "sex": "Male"},
    )

    # 5. TEST Healthcare Practitioner, linked to the test doctor's login
    practitioner_name = _get_or_create(
        "Healthcare Practitioner",
        {"first_name": "TEST - Demo Physician"},
        {
            "first_name": "TEST - Demo Physician",
            "status": "Active",
            "user_id": DOCTOR_USER,
        },
    )

    # 6. The actual Medication Request — ordered by the TEST doctor
    existing = frappe.db.exists(
        "Medication Request",
        {"patient": patient_name, "practitioner": practitioner_name, "medication_item": item_code},
    )
    if existing:
        print(f"Medication Request already exists: {existing}")
        return

    doc = frappe.get_doc({
        "doctype": "Medication Request",
        "order_date": nowdate(),
        "order_time": nowtime(),
        "status": status_code,
        "patient": patient_name,
        "company": company,
        "practitioner": practitioner_name,
        "dosage_form": dosage_form,
        "dosage": dosage,
        "medication_item": item_code,
        "quantity": 1,
    })
    doc.insert(ignore_permissions=True)
    frappe.db.commit()

    print("=== DONE ===")
    print(f"Company:            {company}")
    print(f"Patient:            {patient_name}")
    print(f"Practitioner:       {practitioner_name} (linked to {DOCTOR_USER})")
    print(f"Medication Request: {doc.name}")
    print(
        "\nNow log in as test-027 (Physician) and open Medication Request — "
        "you should see this record.\n"
        "Then log in as test-035 (Pharmacy) and refresh the Medication "
        "Request list — the same record should now appear there too."
    )
