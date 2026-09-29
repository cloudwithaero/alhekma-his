# Al Hekma Hospital — TEST logins for every TEST employee
#
# PURPOSE: One login per TEST employee so you can log in as ANY
# department's test person and see the Desk from their side.
#
# THE REAL "Throttled" CAUSE (confirmed from frappe source,
# frappe/core/doctype/user/user.py -> throttle_user_creation()):
#   Frappe blocks creating a new User once more than
#   `throttle_user_limit` (site_config.json key, default 60) Users
#   have been created in the last 60 MINUTES — not 60 seconds.
#   That's why exponential backoff up to 40s never helped: the
#   window is an hour wide, so short retries can't outrun it.
#   The same function explicitly skips the check when
#   `frappe.flags.in_import` is set — that's the safe, targeted
#   bypass used below (no site_config.json change needed).
#
# CAVEAT (same as the single nurse login): most Roles have no permission
# rules configured yet (Section 05 gate). Expect most of these logins to
# show a bare Desk beyond what Frappe/ERPNext grants automatically to any
# linked Employee. That's expected, not a bug — it's exactly what's still
# pending from hospital management.
#
# Skips any TEST employee that already has a linked User (e.g. the
# Emergency Nursing test login created earlier keeps its "Nursing" role
# untouched).
#
# All accounts share ONE password for convenience during testing.
# DELETE ALL OF THESE before go-live.
#
# Run with:
#   bench --site alhekma.local execute alhekma.patches.create_test_logins_all.run
#
# Safe to re-run: skips employees that already have a linked user.

import os

import frappe

TEST_PASSWORD = os.environ.get("ALHEKMA_TEST_PASSWORD")
EMAIL_DOMAIN = "alhekma.local"


def run():
    if not TEST_PASSWORD:
        frappe.throw("ALHEKMA_TEST_PASSWORD environment variable is required.")

    # Bypass Frappe's rolling 60-minute User-creation throttle for this
    # batch of clearly-labeled TEST accounts. frappe.flags is a per-process
    # flag, so it's reset automatically once this bench command exits —
    # nothing persists, no site-wide setting is touched.
    frappe.flags.in_import = True

    test_employees = frappe.get_all(
        "Employee",
        filters={"employee_number": ["like", "TEST-%"]},
        fields=["name", "employee_name", "employee_number", "department", "user_id"],
    )

    if not test_employees:
        frappe.throw("No TEST employees found. Run create_test_employees.py first.")

    created, skipped, failed = [], [], []
    mapping = []  # (department, email) for the summary table

    for emp in test_employees:
        if emp.user_id:
            skipped.append((emp.department, emp.user_id))
            continue

        email_local = emp.employee_number.lower()  # e.g. "test-014"
        email = f"{email_local}@{EMAIL_DOMAIN}"

        try:
            if frappe.db.exists("User", email):
                user_name = email
            else:
                user = frappe.get_doc({
                    "doctype": "User",
                    "email": email,
                    "first_name": emp.employee_name,
                    "send_welcome_email": 0,
                    "new_password": TEST_PASSWORD,
                })
                user.insert(ignore_permissions=True)
                user_name = user.name

            frappe.db.set_value("Employee", emp.name, "user_id", user_name)
            created.append((emp.department, email))
            mapping.append((emp.department, email))
        except Exception as e:
            failed.append((emp.department, str(e)))

    frappe.db.commit()

    print("=== SUMMARY ===")
    print(f"Logins created: {len(created)}")
    print(f"Skipped (already linked): {len(skipped)}")
    print(f"Failed: {len(failed)}")
    print(f"Shared password for all new logins: {TEST_PASSWORD}")

    if failed:
        print("\n--- FAILURES ---")
        for dept, reason in failed:
            print(f"  {dept}: {reason}")

    print("\n--- DEPARTMENT -> LOGIN EMAIL ---")
    for dept, email in sorted(mapping):
        print(f"  {dept:55s} {email}")

    if skipped:
        print("\n--- ALREADY LINKED (unchanged) ---")
        for dept, existing_user in sorted(skipped):
            print(f"  {dept:55s} {existing_user}")

    print(
        "\nAll new accounts share the password above. Delete all TEST "
        "users before go-live, e.g. in `bench console`:\n"
        '  users = frappe.get_all("User", filters={"name": ["like", "test-%@alhekma.local"]}, pluck="name")\n'
        '  [frappe.delete_doc("User", u, ignore_permissions=True, force=True) for u in users]\n'
        "  frappe.db.commit()"
    )
