# Al Hekma Hospital — Designation Family + Designation creation script
# Source: AlHekma_ERPNext_Master_Tree_EN.xmind.md, Section 04
#
# Run with:
#   bench --site alhekma.local execute alhekma.patches.create_designations.run
#
# Safe to re-run: skips anything that already exists.
# Creates:
#   1. A new simple DocType "Designation Family" (no tree, no custom JS)
#   2. A new Link field "designation_family" on the standard Designation DocType
#   3. The 11 families from the document
#   4. The 40+ designations from the document, each linked to its family

import frappe

FAMILIES = [
    "Governance and Executive Leadership",
    "Management",
    "Medical Staff",
    "Nursing",
    "Allied Health",
    "Health Information and Patient Services",
    "Finance and Claims",
    "Human Resources and Administration",
    "Engineering and Information Technology",
    "Support Services",
]

# (designation_name, family)
DESIGNATIONS = [
    # Governance and Executive Leadership
    ("Chairman of the Board", "Governance and Executive Leadership"),
    ("Medical Director", "Governance and Executive Leadership"),
    ("Administrative Director", "Governance and Executive Leadership"),
    ("Financial Director", "Governance and Executive Leadership"),

    # Management
    ("Department Manager", "Management"),
    ("Section Head", "Management"),
    ("Supervisor", "Management"),
    ("Team Lead", "Management"),

    # Medical Staff
    ("Consultant", "Medical Staff"),
    ("Specialist", "Medical Staff"),
    ("Resident Physician", "Medical Staff"),
    ("General Practitioner", "Medical Staff"),
    ("Visiting Physician", "Medical Staff"),

    # Nursing
    ("Head of Nursing", "Nursing"),
    ("Head Nurse", "Nursing"),
    ("Nursing Supervisor", "Nursing"),
    ("Registered Nurse", "Nursing"),
    ("Nursing Technician", "Nursing"),

    # Allied Health
    ("Reporting Radiologist", "Allied Health"),
    ("Radiology Manager", "Allied Health"),
    ("Assistant Radiology Manager", "Allied Health"),
    ("Radiology Technician", "Allied Health"),
    ("Pharmacist", "Allied Health"),
    ("Assistant Pharmacist", "Allied Health"),
    ("CSSD Technician", "Allied Health"),
    ("Paramedic", "Allied Health"),

    # Health Information and Patient Services
    ("Medical Records Officer", "Health Information and Patient Services"),
    ("Medical Coding Officer", "Health Information and Patient Services"),
    ("Receptionist", "Health Information and Patient Services"),
    ("Registration and Admission Officer", "Health Information and Patient Services"),
    ("Patient Relations Officer", "Health Information and Patient Services"),

    # Finance and Claims
    ("Accountant", "Finance and Claims"),
    ("Treasurer / Cashier", "Finance and Claims"),
    ("Billing Officer", "Finance and Claims"),
    ("Insurance Reception and Data Entry Officer", "Finance and Claims"),
    ("Claims Manager", "Finance and Claims"),
    ("Financial and Cost Analyst", "Finance and Claims"),

    # Human Resources and Administration
    ("Human Resources Officer", "Human Resources and Administration"),
    ("Personnel Affairs Officer", "Human Resources and Administration"),
    ("Training Officer", "Human Resources and Administration"),
    ("Procurement Officer", "Human Resources and Administration"),
    ("Storekeeper", "Human Resources and Administration"),
    ("Quality Officer", "Human Resources and Administration"),
    ("Infection Control Officer", "Human Resources and Administration"),
    ("Legal Counsel / Legal Officer", "Human Resources and Administration"),
    ("Transformation Project Manager", "Human Resources and Administration"),

    # Engineering and Information Technology
    ("Maintenance Engineer", "Engineering and Information Technology"),
    ("Maintenance Technician", "Engineering and Information Technology"),
    ("Information Technology Officer", "Engineering and Information Technology"),
    ("Systems and Applications Officer", "Engineering and Information Technology"),
    ("ERPNext Programmer", "Engineering and Information Technology"),

    # Support Services
    ("Security Supervisor", "Support Services"),
    ("Security Officer", "Support Services"),
    ("Housekeeping Supervisor", "Support Services"),
    ("Housekeeper", "Support Services"),
    ("Laundry Worker", "Support Services"),
]


def create_doctype():
    if frappe.db.exists("DocType", "Designation Family"):
        print("DocType 'Designation Family' already exists — skipping creation.")
        return

    doc = frappe.get_doc({
        "doctype": "DocType",
        "name": "Designation Family",
        "module": "Al Hekma Hospital",
        "custom": 1,
        "naming_rule": "By fieldname",
        "autoname": "field:family_name",
        "fields": [
            {
                "fieldname": "family_name",
                "label": "Family Name",
                "fieldtype": "Data",
                "reqd": 1,
                "unique": 1,
                "in_list_view": 1,
            },
        ],
        "permissions": [
            {
                "role": "System Manager",
                "read": 1, "write": 1, "create": 1, "delete": 1,
            },
            {
                "role": "HR Manager",
                "read": 1, "write": 1, "create": 1,
            },
        ],
    })
    doc.insert(ignore_permissions=True)
    frappe.db.commit()
    print("Created DocType 'Designation Family'.")


def add_link_field_to_designation():
    if frappe.db.exists("Custom Field", "Designation-designation_family"):
        print("Field 'designation_family' already exists on Designation — skipping.")
        return

    field = frappe.get_doc({
        "doctype": "Custom Field",
        "dt": "Designation",
        "fieldname": "designation_family",
        "label": "Designation Family",
        "fieldtype": "Link",
        "options": "Designation Family",
        "insert_after": "designation_name",
        "in_list_view": 1,
    })
    field.insert(ignore_permissions=True)
    frappe.db.commit()
    print("Added Link field 'designation_family' to Designation.")


def create_families():
    created, skipped = [], []
    for family_name in FAMILIES:
        if frappe.db.exists("Designation Family", family_name):
            skipped.append(family_name)
            continue
        doc = frappe.get_doc({
            "doctype": "Designation Family",
            "family_name": family_name,
        })
        doc.insert(ignore_permissions=True)
        created.append(doc.name)
    frappe.db.commit()
    print(f"Families created: {len(created)}, skipped (existed): {len(skipped)}")


def create_designations():
    created, skipped, failed = [], [], []
    for designation_name, family in DESIGNATIONS:
        if frappe.db.exists("Designation", designation_name):
            # Already exists (maybe from ERPNext defaults) — just ensure family link is set
            current_family = frappe.db.get_value("Designation", designation_name, "designation_family")
            if not current_family:
                frappe.db.set_value("Designation", designation_name, "designation_family", family)
            skipped.append(designation_name)
            continue
        try:
            doc = frappe.get_doc({
                "doctype": "Designation",
                "designation_name": designation_name,
                "designation_family": family,
            })
            doc.insert(ignore_permissions=True)
            created.append(doc.name)
        except Exception as e:
            failed.append((designation_name, str(e)))
    frappe.db.commit()

    print(f"Designations created: {len(created)}, skipped (existed): {len(skipped)}, failed: {len(failed)}")
    if failed:
        print("\n--- FAILURES ---")
        for name, reason in failed:
            print(f"  {name}: {reason}")


def run():
    print("=== Step 1: Create Designation Family DocType ===")
    create_doctype()

    print("\n=== Step 2: Add Link field to Designation ===")
    add_link_field_to_designation()

    print("\n=== Step 3: Create 11 families ===")
    create_families()

    print("\n=== Step 4: Create 40+ designations, linked to families ===")
    create_designations()

    print("\n=== DONE ===")
