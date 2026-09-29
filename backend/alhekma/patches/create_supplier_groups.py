# Al Hekma Hospital — Supplier Group creation script
# Source: AlHekma_ERPNext_Master_Tree_EN.xmind.md, Section 08
#
# SCOPE: Supplier Group names/tree only. Does NOT create any actual
# Supplier record — real approved suppliers must come from management
# per the Gate rule (do not invent vendor relationships).
#
# Run with:
#   bench --site alhekma.local execute alhekma.patches.create_supplier_groups.run
#
# Safe to re-run: skips anything that already exists.

import frappe

ROOT_GROUP = "All Supplier Groups"

# (group_name, parent_name_or_None)
TREE = [
    ("Pharmaceuticals and Medical Consumables", None),
    ("Medical Equipment and Devices", None),
    ("Maintenance and Engineering Services", None),
    ("IT Systems and Software", None),
    ("General Services and Utilities", None),
    ("Office and Administrative Supplies", None),
    ("Food and Catering Services", None),
]


def run():
    created, skipped, failed = [], [], []

    if not frappe.db.exists("Supplier Group", ROOT_GROUP):
        frappe.throw(f"Root Supplier Group '{ROOT_GROUP}' not found")

    for name, parent_name in TREE:
        if frappe.db.exists("Supplier Group", name):
            skipped.append(name)
            continue

        parent_resolved = parent_name if parent_name else ROOT_GROUP

        if not frappe.db.exists("Supplier Group", parent_resolved):
            failed.append((name, f"parent '{parent_resolved}' not found yet"))
            continue

        try:
            doc = frappe.get_doc({
                "doctype": "Supplier Group",
                "supplier_group_name": name,
                "parent_supplier_group": parent_resolved,
                "is_group": 0,
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
        "\nNOTE: No actual Supplier records were created — only the "
        "category names exist, ready for management's approved vendor "
        "list to be entered against the right category."
    )
