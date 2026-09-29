# Al Hekma Hospital — Service Group (Item Group) creation script
# Source: AlHekma_ERPNext_Master_Tree_EN.xmind.md, Section 07
#
# SCOPE: Item Groups only (the category names). This does NOT create:
#   - Any Item (actual billable service)
#   - Any price, service code, or revenue account
#   - Any Price List entries
# All of those require real data from hospital management and must
# not be invented, per the master document's explicit Gate rule:
#   "do not invent specialties, services, or prices"
#
# Future [F] and external [X] items are excluded — not operational yet
# or not an internal service (External Laboratory is a supplier).
#
# Run with:
#   bench --site alhekma.local execute alhekma.patches.create_service_groups.run
#
# Safe to re-run: skips anything that already exists.

import frappe

# (group_name, parent_name_or_None)
TREE = [
    ("Hospital Services", None),  # top-level parent for all clinical service groups

    ("Emergency", "Hospital Services"),
    ("Examination and Triage", "Emergency"),
    ("Observation and Procedures", "Emergency"),

    ("Inpatient", "Hospital Services"),
    ("Standard Inpatient Day", "Inpatient"),
    ("VIP Inpatient Day", "Inpatient"),

    ("Critical Care and Stroke", "Hospital Services"),
    ("ICU Day", "Critical Care and Stroke"),
    ("Stroke Services and Packages", "Critical Care and Stroke"),

    ("Surgery and Procedures", "Hospital Services"),
    ("Operating Room Use", "Surgery and Procedures"),
    ("Anesthesia", "Surgery and Procedures"),
    ("Surgery or Procedure", "Surgery and Procedures"),
    ("Recovery", "Surgery and Procedures"),

    ("Outpatient Clinics", "Hospital Services"),
    ("General Practitioner Consultation", "Outpatient Clinics"),
    # Specialty Consultation [F] and Follow-up Consultation [F] excluded — future

    ("Radiology", "Hospital Services"),
    ("CT", "Radiology"),
    ("Ultrasound", "Radiology"),
    # MRI [F] excluded — future, not currently available

    ("Pharmacy", "Hospital Services"),
    ("Medicines", "Pharmacy"),
    ("Patient-Billable Consumables", "Pharmacy"),

    ("Ambulance", "Hospital Services"),
    ("Local Transport", "Ambulance"),
    # Distance- or Acuity-Based Transport [D] excluded — pending pricing policy

    # External Laboratory [X] excluded — this is a supplier relationship,
    # not an internal service group, per the document's own classification.
]


def run():
    created, skipped, failed = [], [], []

    for name, parent_name in TREE:
        if frappe.db.exists("Item Group", name):
            skipped.append(name)
            continue

        parent_name_resolved = parent_name if parent_name else "All Item Groups"

        if not frappe.db.exists("Item Group", parent_name_resolved):
            failed.append((name, f"parent '{parent_name_resolved}' not found yet"))
            continue

        try:
            doc = frappe.get_doc({
                "doctype": "Item Group",
                "item_group_name": name,
                "parent_item_group": parent_name_resolved,
                "is_group": 1,  # corrected in a follow-up pass if needed
            })
            doc.insert(ignore_permissions=True)
            created.append(doc.name)
        except Exception as e:
            failed.append((name, str(e)))

    frappe.db.commit()

    print("=== SUMMARY ===")
    print(f"Created: {len(created)}")
    print(f"Skipped (already existed): {len(skipped)}")
    print(f"Failed: {len(failed)}")

    if failed:
        print("\n--- FAILURES ---")
        for name, reason in failed:
            print(f"  {name}: {reason}")
        print(
            "\nSome groups could not be created because their parent was "
            "not yet created. Re-run this script — it is safe and "
            "idempotent, and will pick up where it left off."
        )

    print(
        "\nNOTE: No Items, prices, service codes, or revenue accounts "
        "have been created. Only the category structure (Item Groups) "
        "exists. Actual billable services must be added once management "
        "confirms the service catalogue and pricing."
    )
