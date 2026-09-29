# Al Hekma Hospital — Employee Badge DocType (card/QR + PIN kiosk login)
#
# PURPOSE: A lightweight standalone DocType that maps a physical badge
# code (printed as barcode/QR on the employee's card) to their real
# ERPNext User account, WITHOUT ever storing or exposing their actual
# account password. The badge's PIN is stored separately (hashed,
# via Frappe's own generic Auth mechanism — the same one that protects
# real user passwords), decoupled from the account password entirely.
# Losing/revoking a badge never touches the employee's real login.
#
# Run with:
#   bench --site alhekma.local execute alhekma.patches.create_employee_badge_doctype.run
#
# Safe to re-run: skips if the DocType already exists.

import frappe

DOCTYPE_NAME = "Employee Badge"


def run():
    if frappe.db.exists("DocType", DOCTYPE_NAME):
        print(f"DocType '{DOCTYPE_NAME}' already exists — skipping.")
        return

    doc = frappe.get_doc({
        "doctype": "DocType",
        "name": DOCTYPE_NAME,
        "module": "Al Hekma Hospital",
        "custom": 1,
        "naming_rule": "By fieldname",
        "autoname": "field:badge_code",
        "fields": [
            {
                "fieldname": "badge_code",
                "label": "Badge Code",
                "fieldtype": "Data",
                "reqd": 1,
                "unique": 1,
                "in_list_view": 1,
                "description": "The value encoded in the barcode/QR printed on the physical card.",
            },
            {
                "fieldname": "user",
                "label": "ERPNext User",
                "fieldtype": "Link",
                "options": "User",
                "reqd": 1,
                "in_list_view": 1,
            },
            {
                "fieldname": "employee",
                "label": "Employee",
                "fieldtype": "Link",
                "options": "Employee",
                "description": "Optional — for display/reporting only.",
            },
            {
                "fieldname": "disabled",
                "label": "Disabled",
                "fieldtype": "Check",
                "description": "Tick this immediately if the physical card is lost or stolen — "
                                "this blocks kiosk login without touching the employee's real account.",
            },
            {
                "fieldname": "failed_pin_attempts",
                "label": "Failed PIN Attempts (last window)",
                "fieldtype": "Int",
                "read_only": 1,
                "hidden": 1,
            },
        ],
        "permissions": [
            {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
            {"role": "HR Manager", "read": 1, "write": 1, "create": 1},
        ],
    })
    doc.insert(ignore_permissions=True)
    frappe.db.commit()
    print(f"Created DocType '{DOCTYPE_NAME}'.")
    print(
        "\nNext steps:\n"
        "  1. Drop alhekma/api.py's badge_login/set_employee_pin into the app.\n"
        "  2. Drop the www/kiosk.html + kiosk.py page into the app.\n"
        "  3. Run register_test_badges.py to create a couple of test badges.\n"
        "  4. Run 'bench --site alhekma.local migrate' if the new DocType "
        "doesn't show up immediately."
    )
