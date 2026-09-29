# Al Hekma Hospital — Warehouse creation script
# Source: AlHekma_ERPNext_Master_Tree_EN.xmind.md, Section 08
#
# SCOPE: Warehouse names/tree only, linked to departments already created
# in Section 02. Does NOT touch stock balances, opening quantities, or
# item valuation — those require real data and are out of scope here.
#
# Run with:
#   bench --site alhekma.local execute alhekma.patches.create_warehouses.run
#
# Safe to re-run: skips anything that already exists.

import frappe

COMPANY = "Al Hekma Hospital"
ABBR = "hikma"
ROOT_WAREHOUSE_NAME = "All Warehouses"

# (warehouse_name, parent_warehouse_name_or_None, is_group)
# None parent = reports directly to the company's default root warehouse
TREE = [
    ("General Stores", None, 0),
    ("Pharmacy Store", None, 0),
    ("CSSD Store", None, 0),
]


def _docname(name):
    return f"{name} - {ABBR}"


def _ensure_root_warehouse():
    """The Company doctype normally auto-creates a root 'All Warehouses'
    group warehouse. It's missing here (company was likely created outside
    the normal onboarding flow), so create it once, safely."""
    root_docname = _docname(ROOT_WAREHOUSE_NAME)

    if frappe.db.exists("Warehouse", root_docname):
        return root_docname

    existing_root = frappe.db.get_value(
        "Warehouse",
        {"company": COMPANY, "is_group": 1, "parent_warehouse": ["is", "not set"]},
        "name",
    )
    if existing_root:
        return existing_root

    doc = frappe.get_doc({
        "doctype": "Warehouse",
        "warehouse_name": ROOT_WAREHOUSE_NAME,
        "company": COMPANY,
        "is_group": 1,
    })
    doc.insert(ignore_permissions=True)
    frappe.db.commit()
    print(f"Created missing root warehouse: {doc.name}")
    return doc.name


def run():
    created, skipped, failed = [], [], []

    root_name = _ensure_root_warehouse()
    print(f"Root warehouse resolved as: {root_name}")

    for name, parent_name, is_group in TREE:
        docname = _docname(name)

        if frappe.db.exists("Warehouse", docname):
            skipped.append(docname)
            continue

        parent_docname = _docname(parent_name) if parent_name else root_name

        if not frappe.db.exists("Warehouse", parent_docname):
            failed.append((docname, f"parent '{parent_docname}' not found yet"))
            continue

        try:
            doc = frappe.get_doc({
                "doctype": "Warehouse",
                "warehouse_name": name,
                "company": COMPANY,
                "parent_warehouse": parent_docname,
                "is_group": is_group,
            })
            doc.insert(ignore_permissions=True)
            created.append(doc.name)
        except Exception as e:
            failed.append((docname, str(e)))

    frappe.db.commit()

    print("\n=== SUMMARY ===")
    print(f"Created: {len(created)}")
    print(f"Skipped (already existed): {len(skipped)}")
    print(f"Failed: {len(failed)}")

    if failed:
        print("\n--- FAILURES ---")
        for name, reason in failed:
            print(f"  {name}: {reason}")

    print(
        "\nNOTE: No stock balances, opening quantities, or item "
        "valuations were touched — only the Warehouse containers exist. "
        "Actual stock entries wait until items/procurement data arrive."
    )
