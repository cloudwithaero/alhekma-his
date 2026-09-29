# Al Hekma Hospital — DEMO: multi-drug encounter + pharmacy status
# workflow + nurse notifications
#
# Builds on create_demo_medication_request.py and
# link_demo_medication_name.py (run those first).
#
# WHAT THIS ADDS:
#   1. A real Patient Encounter (the "visit") linking the existing
#      demo Medication Request to it, plus a SECOND demo Medication
#      Request (a different drug) linked to the same encounter — this
#      is how ERPNext represents "more than one drug in one visit":
#      multiple Medication Request records sharing one
#      order_group (Patient Encounter), not multiple lines in one record.
#   2. Two more status values for the pharmacy workflow: "Preparing"
#      and "Dispensed" (in addition to "Requested" from the earlier
#      script).
#   3. WRITE permission for the Pharmacy role on Medication Request
#      (they only had read before) so pharmacy staff can actually
#      change the status field.
#   4. Two System Notifications that fire automatically whenever a
#      Medication Request's status changes to "Preparing" or
#      "Dispensed" — sent to everyone holding the Nursing role.
#
# CAVEAT (explicit, not hidden): Medication Request has no field for
# "which specific nurse is responsible for this patient". Real hospital
# routing (notify only the assigned nurse, not every nurse in the
# building) needs that link to exist first — a policy/data-model
# decision for hospital management, same Gate-rule pattern as
# everything else in this project. This demo broadcasts to the whole
# Nursing role as a stand-in.
#
# Run with:
#   bench --site alhekma.local execute alhekma.patches.build_medication_workflow_demo.run
#
# Safe to re-run: skips anything that already exists.

import frappe
import frappe.permissions as perms
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
    # --- 0. Pull in what the earlier demo scripts already created ---
    patient = frappe.db.get_value("Patient", {"first_name": "TEST - Demo Patient"}, "name")
    practitioner = frappe.db.get_value(
        "Healthcare Practitioner", {"first_name": "TEST - Demo Physician"}, "name"
    )
    company = frappe.db.get_value("Company", {}, "name")
    dosage_form = frappe.db.get_value("Dosage Form", {"dosage_form": "Tablet (TEST)"}, "name")
    dosage = frappe.db.get_value(
        "Prescription Dosage", {"dosage": "1 tablet twice daily (TEST)"}, "name"
    )
    code_system = frappe.db.get_value(
        "Code System", {"code_system": "AlHekma Local Codes (TEST)"}, "name"
    )
    first_med_request = frappe.db.get_value(
        "Medication Request", {"medication_item": "TEST-MED-PARACETAMOL-500"}, "name"
    )

    if not all([patient, practitioner, company, dosage_form, dosage, code_system, first_med_request]):
        frappe.throw(
            "Missing demo data — run create_demo_medication_request.py and "
            "link_demo_medication_name.py first."
        )

    # --- 1. Real Patient Encounter (the "visit") ---
    appointment_type = _get_or_create(
        "Appointment Type", {"appointment_type": "Consultation (TEST)"}, {"appointment_type": "Consultation (TEST)"}
    )
    encounter = frappe.db.exists(
        "Patient Encounter", {"patient": patient, "practitioner": practitioner}
    )
    if not encounter:
        enc = frappe.get_doc({
            "doctype": "Patient Encounter",
            "patient": patient,
            "practitioner": practitioner,
            "company": company,
            "encounter_date": nowdate(),
            "encounter_time": nowtime(),
            "appointment_type": appointment_type,
        })
        enc.insert(ignore_permissions=True)
        encounter = enc.name
    print(f"Patient Encounter: {encounter}")

    # Link the existing Medication Request to this encounter
    frappe.db.set_value("Medication Request", first_med_request, "order_group", encounter)

    # --- 2. A second drug, same encounter (proves "more than one item") ---
    second_item_code = "TEST-MED-IBUPROFEN-400"
    if not frappe.db.exists("Item", second_item_code):
        frappe.get_doc({
            "doctype": "Item",
            "item_code": second_item_code,
            "item_name": "Ibuprofen 400mg (TEST item — not real catalogue data)",
            "item_group": frappe.db.get_value("Item Group", {}, "name") or "All Item Groups",
            "is_stock_item": 0,
            "stock_uom": "Nos",
        }).insert(ignore_permissions=True)

    requested_status = frappe.db.get_value(
        "Code Value", {"code_value": "requested", "code_system": code_system}, "name"
    )

    second_med_request = frappe.db.exists(
        "Medication Request", {"medication_item": second_item_code, "patient": patient}
    )
    if not second_med_request:
        doc2 = frappe.get_doc({
            "doctype": "Medication Request",
            "order_date": nowdate(),
            "order_time": nowtime(),
            "status": requested_status,
            "patient": patient,
            "company": company,
            "practitioner": practitioner,
            "dosage_form": dosage_form,
            "dosage": dosage,
            "medication_item": second_item_code,
            "quantity": 1,
            "order_group": encounter,
        })
        doc2.insert(ignore_permissions=True)
        second_med_request = doc2.name
    print(f"Second Medication Request (same encounter): {second_med_request}")

    # --- 3. Pharmacy workflow statuses ---
    preparing_status = _get_or_create(
        "Code Value",
        {"code_value": "preparing", "code_system": code_system},
        {"code_system": code_system, "code_value": "preparing", "display": "Preparing (TEST)"},
    )
    dispensed_status = _get_or_create(
        "Code Value",
        {"code_value": "dispensed", "code_system": code_system},
        {"code_system": code_system, "code_value": "dispensed", "display": "Dispensed (TEST)"},
    )

    # --- 4. Let Pharmacy actually change the status (write, not just read) ---
    perms.update_permission_property("Medication Request", "Pharmacy", 0, "write", 1)
    frappe.clear_cache()

    # --- 5. Notifications to the Nursing role on status change ---
    def _ensure_notification(name, condition_status, subject):
        if frappe.db.exists("Notification", name):
            return
        frappe.get_doc({
            "doctype": "Notification",
            "name": name,
            "subject": subject,
            "document_type": "Medication Request",
            "event": "Value Change",
            "value_changed": "status",
            "channel": "System Notification",
            "condition": f'doc.status == "{condition_status}"',
            "message": (
                "<p>طلب دواء للمريض {{ doc.patient_name }} "
                f"({subject}).</p>"
                "<p>Medication Request: {{ doc.name }}</p>"
            ),
            "recipients": [{"receiver_by_role": "Nursing"}],
        }).insert(ignore_permissions=True)

    _ensure_notification(
        "Medication Request Preparing (TEST)", preparing_status, "الصيدلية بدأت تجهيز الدواء"
    )
    _ensure_notification(
        "Medication Request Dispensed (TEST)", dispensed_status, "الدواء جاهز/تم صرفه"
    )

    frappe.db.commit()

    print("\n=== DONE ===")
    print(f"Encounter linking both Medication Requests: {encounter}")
    print(f"Medication Request 1 (Paracetamol): {first_med_request}")
    print(f"Medication Request 2 (Ibuprofen):    {second_med_request}")
    print(f"Status codes ready: requested / {preparing_status} / {dispensed_status}")
    print(
        "\nNow, logged in as test-035 (Pharmacy), open either Medication "
        "Request and change its Status field to 'Preparing (TEST)', save, "
        "then to 'Dispensed (TEST)', save. Each save should create a "
        "System Notification (bell icon) for every user holding the "
        "Nursing role — including test-029."
    )
