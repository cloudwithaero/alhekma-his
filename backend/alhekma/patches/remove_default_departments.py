# Al Hekma Hospital — Remove ERPNext's auto-created default departments
#
# These 12 departments are NOT from AlHekma_ERPNext_Master_Tree_EN.xmind.md.
# ERPNext creates them automatically for any new Company (its standard
# demo/default HR structure). Removing them keeps the Department tree
# matching the approved master document exactly.
#
# Also removes the TEST employee (if any) that was seeded against each
# one, since an Employee cannot be orphaned from its Department safely.
#
# Run with:
#   bench --site alhekma.local execute alhekma.patches.remove_default_departments.run
#
# Safe to re-run: skips anything already gone.

import frappe

ABBR = "hikma"

DEFAULT_DEPARTMENTS_TO_REMOVE = [
    "Accounts",
    "Marketing",
    "Sales",
    "Purchase",
    "Operations",
    "Production",
    "Dispatch",
    "Customer Service",
    "Human Resources",
    "Management",
    "Quality Management",
    "Research & Development",
    "Legal",
]


def _docname(name):
    return f"{name} - {ABBR}"


def run():
    employees_deleted, departments_deleted, skipped, failed = [], [], [], []

    for name in DEFAULT_DEPARTMENTS_TO_REMOVE:
        docname = _docname(name)

        if not frappe.db.exists("Department", docname):
            skipped.append(docname)
            continue

        try:
            # Remove any employee(s) linked to this department first
            # (includes the TEST employee seeded earlier, if present).
            linked_employees = frappe.get_all("Employee", filters={"department": docname}, pluck="name")
            for emp in linked_employees:
                frappe.delete_doc("Employee", emp, ignore_permissions=True, force=True)
                employees_deleted.append(emp)

            frappe.delete_doc("Department", docname, ignore_permissions=True, force=True)
            departments_deleted.append(docname)
        except Exception as e:
            failed.append((docname, str(e)))

    frappe.db.commit()

    print("=== SUMMARY ===")
    print(f"Departments deleted: {len(departments_deleted)}")
    print(f"Employees deleted (linked TEST records): {len(employees_deleted)}")
    print(f"Skipped (already gone): {len(skipped)}")
    print(f"Failed: {len(failed)}")

    if failed:
        print("\n--- FAILURES ---")
        for name, reason in failed:
            print(f"  {name}: {reason}")
        print(
            "\nA failure usually means something else still links to this "
            "department (e.g. a real Employee, Cost Center, or Warehouse "
            "default). Check the linked doctype named in the error before "
            "re-running."
        )
