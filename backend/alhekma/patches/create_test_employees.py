# Al Hekma Hospital — TEST/DUMMY Employee seeding script
#
# PURPOSE: One clearly-labeled fake employee per LEAF department, so you
# can click around Employee list/tree views, department-linked reports,
# and permission testing with something in front of you.
#
# THIS IS NOT REAL DATA. Every record is named starting with
# "TEST - " and given employee_number starting with "TEST-" so it is
# impossible to mistake for a real hire, and trivial to bulk-select and
# delete before go-live.
#
# Only fields that are safe to fabricate for UI testing are set
# (name, gender placeholder, department, date of joining = today,
# status). No designation is guessed per department — that mapping is
# real HR data and out of scope here.
#
# Run with:
#   bench --site alhekma.local execute alhekma.patches.create_test_employees.run
#
# Safe to re-run: skips departments that already have a TEST employee.
#
# TO DELETE ALL TEST EMPLOYEES LATER, run in `bench console`:
#   frappe.db.delete("Employee", {"employee_number": ["like", "TEST-%"]})
#   frappe.db.commit()

# NOTE (seen on first run): 12 extra leaf departments not from the master
# tree will also get a test employee — Accounts, Marketing, Sales,
# Purchase, Operations, Production, Dispatch, Customer Service, Human
# Resources, Management, Quality Management, Research & Development,
# Legal. These are ERPNext's standard auto-created departments for any
# new Company and are NOT part of AlHekma_ERPNext_Master_Tree_EN.xmind.md.
# Left in scope here on purpose — deciding whether to delete/merge them
# is a separate decision, not something to silently skip.

import frappe

COMPANY = "Al Hekma Hospital"
TEST_PREFIX = "TEST - "
TEST_NUMBER_PREFIX = "TEST-"


def run():
    leaf_departments = frappe.get_all(
        "Department",
        filters={"company": COMPANY, "is_group": 0},
        fields=["name", "department_name"],
    )

    if not leaf_departments:
        frappe.throw("No leaf departments found — run create_departments.py and fix_is_group.py first")

    created, skipped, failed = [], [], []

    for i, dept in enumerate(leaf_departments, start=1):
        employee_name = f"{TEST_PREFIX}{dept.department_name}"
        employee_number = f"{TEST_NUMBER_PREFIX}{i:03d}"

        already_exists = frappe.db.exists(
            "Employee", {"department": dept.name, "employee_number": ["like", "TEST-%"]}
        )
        if already_exists:
            skipped.append(dept.department_name)
            continue

        try:
            doc = frappe.get_doc({
                "doctype": "Employee",
                "employee_name": employee_name,
                "first_name": employee_name,
                "employee_number": employee_number,
                "company": COMPANY,
                "department": dept.name,
                "gender": "Male",
                "date_of_birth": "1990-01-01",
                "date_of_joining": frappe.utils.today(),
                "status": "Active",
            })
            doc.insert(ignore_permissions=True)
            created.append(doc.name)
        except Exception as e:
            failed.append((dept.department_name, str(e)))

    frappe.db.commit()

    print("=== SUMMARY ===")
    print(f"Created: {len(created)}")
    print(f"Skipped (already had a test employee): {len(skipped)}")
    print(f"Failed: {len(failed)}")

    if failed:
        print("\n--- FAILURES ---")
        for name, reason in failed:
            print(f"  {name}: {reason}")

    print(
        "\nAll created employees are named 'TEST - <department>' with an "
        "employee_number starting 'TEST-'. To remove all of them later, "
        "run in `bench --site alhekma.local console`:\n"
        '  frappe.db.delete("Employee", {"employee_number": ["like", "TEST-%"]})\n'
        "  frappe.db.commit()"
    )
