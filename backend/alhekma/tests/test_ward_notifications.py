import frappe
import requests


ASSIGNMENT_DTYPE = "TEST Nursing Ward User"

NTFY_URL = "https://ntfy.sh/"


STATUS_LABELS = {
    "draft-Medication Request Status": "مسودة",
    "active-Medication Request Status": "نشط",
    "on-hold-Medication Request Status": "معلّق",
    "completed-Medication Request Status": "مكتمل",
    "cancelled-Medication Request Status": "ملغي",
    "ended-Medication Request Status": "منتهي",
    "stopped-Medication Request Status": "متوقف",
    "unknown-Medication Request Status": "غير معروف",
    "entered-in-error-Medication Request Status": "تم إدخاله بالخطأ",
}


def get_status_label(status):
    if not status:
        return "غير محددة"

    return STATUS_LABELS.get(status, status)


def get_current_ward(patient):
    inpatient_records = frappe.get_all(
        "Inpatient Record",
        filters={
            "patient": patient,
            "status": "Admitted",
        },
        fields=["name"],
        order_by="modified desc",
        limit=1,
    )

    if not inpatient_records:
        return None

    inpatient_record = frappe.get_doc(
        "Inpatient Record",
        inpatient_records[0].name,
    )

    current_occupancy = None

    for row in inpatient_record.inpatient_occupancies:
        if not row.check_out:
            current_occupancy = row
            break

    if not current_occupancy:
        return None

    bed = frappe.get_doc(
        "Healthcare Service Unit",
        current_occupancy.service_unit,
    )

    parent = bed.parent_healthcare_service_unit

    while parent:
        unit = frappe.get_doc(
            "Healthcare Service Unit",
            parent,
        )

        if unit.is_group:
            return unit.name

        parent = unit.parent_healthcare_service_unit

    return None


def get_ward_nurses(ward):
    if not ward:
        return []

    return frappe.get_all(
        ASSIGNMENT_DTYPE,
        filters={
            "service_unit": ward,
        },
        pluck="user",
    )


def send_ntfy_notification(subject, message):
    try:
        response = requests.post(
            NTFY_URL,
            json={
                "topic": "alhekma-test-847293",
                "message": message,
                "title": subject,
                "priority": 4,
                "tags": [
                    "hospital",
                    "medication",
                ],
            },
            timeout=5,
        )

        response.raise_for_status()

        frappe.logger("alhekma").info(
            f"ntfy notification sent successfully: {response.status_code}"
        )

        return True

    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            "Al Hekma ntfy notification failed",
        )

        return False


def notify_ward_nurses_on_medication_request(doc, method=None):
    if frappe.flags.in_import or frappe.flags.in_patch:
        return

    if doc.doctype != "Medication Request":
        return

    if method != "on_update":
        return

    old_doc = doc.get_doc_before_save()

    if not old_doc:
        return

    old_status = old_doc.get("status")
    new_status = doc.get("status")

    # Only notify when the status actually changes
    if old_status == new_status:
        return

    # Find the current ward of the patient
    ward = get_current_ward(doc.patient)

    if not ward:
        return

    # Find nurses assigned to that ward
    users = get_ward_nurses(ward)

    if not users:
        return

    patient_name = doc.get("patient_name") or doc.patient

    old_status_label = get_status_label(old_status)
    new_status_label = get_status_label(new_status)

    subject = f"💊 تحديث حالة دواء - {patient_name}"

    # ERPNext Notification Log HTML message
    message = f"""
<div dir="rtl" style="font-family: Arial, sans-serif; line-height: 1.8; direction: rtl; text-align: right;">

    <h3>💊 تحديث حالة دواء</h3>

    <p>
        <b>المريض:</b>
        {patient_name}
    </p>

    <p>
        <b>الحالة السابقة:</b>
        {old_status_label}
    </p>

    <p>
        <b>الحالة الحالية:</b>
        {new_status_label}
    </p>

    <hr>

    <p>
        يرجى مراجعة طلب الدواء واتخاذ الإجراء المناسب.
    </p>

</div>
"""

    # Create ERPNext notifications
    for user in users:
        frappe.get_doc(
            {
                "doctype": "Notification Log",
                "for_user": user,
                "type": "Alert",
                "document_type": doc.doctype,
                "document_name": doc.name,
                "subject": subject,
                "email_content": message,
            }
        ).insert(ignore_permissions=True)

    # Plain-text message for ntfy
    ntfy_message = f"""💊 تحديث حالة دواء

المريض: {patient_name}

الحالة السابقة: {old_status_label}

الحالة الحالية: {new_status_label}

يرجى مراجعة طلب الدواء واتخاذ الإجراء المناسب."""

    # Send mobile push notification
    send_ntfy_notification(
        subject,
        ntfy_message,
    )

    frappe.db.commit()
