import frappe


TEST_WARD = "TEST Nursing Ward"
TEST_BED = "TEST Medication Workflow Bed - hikma"
TEST_NURSE = "test-029@alhekma.local"
ASSIGNMENT_DTYPE = "TEST Nursing Ward User"


def ensure_assignment_doctype():
    if frappe.db.exists("DocType", ASSIGNMENT_DTYPE):
        return

    doc = frappe.get_doc({
        "doctype": "DocType",
        "name": ASSIGNMENT_DTYPE,
        "module": "Al Hekma Hospital",
        "custom": 1,
        "autoname": "hash",
        "fields": [
            {
                "fieldname": "service_unit",
                "label": "Ward / Service Unit",
                "fieldtype": "Link",
                "options": "Healthcare Service Unit",
                "reqd": 1,
            },
            {
                "fieldname": "user",
                "label": "Nurse User",
                "fieldtype": "Link",
                "options": "User",
                "reqd": 1,
            },
        ],
    })

    doc.insert(ignore_permissions=True)


def ensure_test_ward():
    if not frappe.db.exists("Healthcare Service Unit", TEST_WARD + " - hikma"):
        ward = frappe.get_doc({
            "doctype": "Healthcare Service Unit",
            "healthcare_service_unit_name": TEST_WARD,
            "is_group": 1,
            "parent_healthcare_service_unit": "Inpatient Services - hikma",
            "company": "Al Hekma Hospital",
        })
        ward.insert(ignore_permissions=True)

    return TEST_WARD + " - hikma"


def move_test_bed(ward_name):
    bed = frappe.get_doc("Healthcare Service Unit", TEST_BED)

    if bed.parent_healthcare_service_unit != ward_name:
        bed.parent_healthcare_service_unit = ward_name
        bed.save(ignore_permissions=True)


def ensure_nurse_assignment(ward_name):
    existing = frappe.db.exists(
        ASSIGNMENT_DTYPE,
        {
            "service_unit": ward_name,
            "user": TEST_NURSE,
        },
    )

    if not existing:
        frappe.get_doc({
            "doctype": ASSIGNMENT_DTYPE,
            "service_unit": ward_name,
            "user": TEST_NURSE,
        }).insert(ignore_permissions=True)


def install_notification_hook():
    hook_file = frappe.get_app_path("alhekma", "hooks.py")

    with open(hook_file, "r", encoding="utf-8") as f:
        content = f.read()

    import_line = (
        "from alhekma.api.test_ward_notifications "
        "import notify_ward_nurses_on_medication_request"
    )

    if import_line not in content:
        content = import_line + "\n\n" + content

    if "doc_events = {" not in content:
        content += """
\n
doc_events = {
    "Medication Request": {
        "on_update": "alhekma.api.test_ward_notifications.notify_ward_nurses_on_medication_request"
    }
}
"""
    else:
        frappe.throw(
            "hooks.py already contains doc_events. "
            "Do not let this TEST patch overwrite existing hooks. "
            "Add the Medication Request on_update entry manually."
        )

    with open(hook_file, "w", encoding="utf-8") as f:
        f.write(content)


def run():
    frappe.flags.in_patch = True

    ensure_assignment_doctype()

    ward = ensure_test_ward()

    move_test_bed(ward)

    ensure_nurse_assignment(ward)

    frappe.db.commit()

    print("TEST Ward:", ward)
    print("TEST Bed:", TEST_BED)
    print("TEST Nurse:", TEST_NURSE)
    print("Assignment:", ASSIGNMENT_DTYPE)
    print("")
    print("TEST structure created successfully.")
    print("NOTE: Notification hook is NOT installed by this patch.")
