# Al Hekma Hospital — Roles + Role Profiles creation script
# Source: AlHekma_ERPNext_Master_Tree_EN.xmind.md, Section 05
#
# Run with:
#   bench --site alhekma.local execute alhekma.patches.create_roles.run
#
# IMPORTANT — SCOPE OF THIS SCRIPT:
# This creates the NAMES only (Roles + Role Profiles grouping them).
# It does NOT set any DocType permissions (read/write/create/delete).
# Actual permission rules are a separate, deliberate decision that must
# be reviewed with hospital management before being configured —
# per the master document's Gate rules ("do not invent access rules").
#
# Safe to re-run: skips anything that already exists.

import frappe

# (role_name, category)
ROLES = [
    # System Administration
    ("System Administrator", "System Administration"),
    ("ERPNext Application Administrator", "System Administration"),
    ("IT Support", "System Administration"),

    # Leadership
    ("Chairman Executive View", "Leadership"),
    ("Medical Director View", "Leadership"),
    ("Administrative Director View", "Leadership"),
    ("Financial Director View", "Leadership"),
    ("Department Manager View", "Leadership"),

    # Clinical
    ("Physician", "Clinical"),
    ("Nursing", "Clinical"),
    ("Emergency Registration", "Clinical"),
    ("Radiology", "Clinical"),
    ("Pharmacy", "Clinical"),
    ("CSSD", "Clinical"),
    ("Ambulance", "Clinical"),

    # Patient Services and Revenue Cycle
    ("Reception and Registration", "Patient Services and Revenue Cycle"),
    ("Admission and Discharge", "Patient Services and Revenue Cycle"),
    ("Medical Records", "Patient Services and Revenue Cycle"),
    ("Billing", "Patient Services and Revenue Cycle"),
    ("Claims Entry and Processing", "Patient Services and Revenue Cycle"),
    ("Claims Manager", "Patient Services and Revenue Cycle"),

    # Resources and Operations
    ("Human Resources", "Resources and Operations"),
    ("Procurement", "Resources and Operations"),
    ("Storekeeper", "Resources and Operations"),
    ("Engineering and Maintenance", "Resources and Operations"),
    ("Asset Custodian", "Resources and Operations"),

    # Oversight
    ("Quality and Risk Management", "Oversight"),
    ("Infection Control", "Oversight"),
    ("Legal", "Oversight"),
]

# Role Profile = one per category, bundling all roles in that category.
# This matches the document's grouping under "Permission profiles".
CATEGORIES = [
    "System Administration",
    "Leadership",
    "Clinical",
    "Patient Services and Revenue Cycle",
    "Resources and Operations",
    "Oversight",
]


def create_roles():
    created, skipped = [], []
    for role_name, _category in ROLES:
        if frappe.db.exists("Role", role_name):
            skipped.append(role_name)
            continue
        doc = frappe.get_doc({
            "doctype": "Role",
            "role_name": role_name,
            "desk_access": 1,
        })
        doc.insert(ignore_permissions=True)
        created.append(doc.name)
    frappe.db.commit()
    print(f"Roles created: {len(created)}, skipped (existed): {len(skipped)}")
    if skipped:
        print("  Already existed:", ", ".join(skipped))


def create_role_profiles():
    created, skipped, failed = [], [], []

    for category in CATEGORIES:
        profile_name = category  # Role Profile name = category name

        roles_in_category = [r for r, c in ROLES if c == category]

        if frappe.db.exists("Role Profile", profile_name):
            skipped.append(profile_name)
            continue

        try:
            doc = frappe.get_doc({
                "doctype": "Role Profile",
                "role_profile": profile_name,
                "roles": [
                    {"role": role_name} for role_name in roles_in_category
                ],
            })
            doc.insert(ignore_permissions=True)
            created.append(doc.name)
        except Exception as e:
            failed.append((profile_name, str(e)))

    frappe.db.commit()
    print(f"Role Profiles created: {len(created)}, skipped (existed): {len(skipped)}, failed: {len(failed)}")
    if failed:
        print("\n--- FAILURES ---")
        for name, reason in failed:
            print(f"  {name}: {reason}")


def run():
    print("=== Step 1: Create 28 Roles (names only, no permissions set) ===")
    create_roles()

    print("\n=== Step 2: Create 6 Role Profiles (grouping roles by category) ===")
    create_role_profiles()

    print("\n=== DONE ===")
    print(
        "\nNOTE: No DocType permissions have been configured on these roles yet.\n"
        "Each role currently grants NO special access beyond Frappe's defaults.\n"
        "Actual read/write/create/delete rules per role must be decided with\n"
        "hospital management before being configured — this was intentionally\n"
        "left out of this script per the master document's Gate rules."
    )
