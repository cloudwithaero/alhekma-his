# Al Hekma Hospital — Price List creation script
# Source: AlHekma_ERPNext_Master_Tree_EN.xmind.md, Section 07
#
# SCOPE: Creates ONLY the two Price Lists we are certain about right now.
# Does NOT create:
#   - Any Item Price / actual rate (waiting on real numbers from management)
#   - An "Insurance by Contract" or "Corporate Contracted" list — that split
#     is still an open question with hospital management (one shared
#     contracted-rate list vs. two separate lists). Per the Gate rule
#     ("do not invent decisions"), we are not guessing this one.
#
# Once management answers the Insurance/Corporate question, just add the
# resolved name(s) to the PENDING_NOTE section below and re-run — this
# script is safe and idempotent either way.
#
# Run with:
#   bench --site alhekma.local execute alhekma.patches.create_price_lists.run

import frappe

COMPANY = "alhikma_hospital"
CURRENCY = "EGP"

# (price_list_name, selling, buying)
PRICE_LISTS = [
    ("Individual Cash", 1, 0),
    ("Employee Discount", 1, 0),
]

# NOTE — decision pending with hospital management (as of 2026-09-15):
#   Insurance by Contract  vs.  Corporate Contracted
#   -> one shared "Contracted Rate" list, or two separate lists?
# Once resolved, add the name(s) above and re-run this script.
PENDING_NOTE = (
    "Insurance/Corporate contracted pricing structure: NOT created yet — "
    "awaiting management decision on shared vs. separate price lists."
)


def run():
    created, skipped, failed = [], [], []

    for name, selling, buying in PRICE_LISTS:
        if frappe.db.exists("Price List", name):
            skipped.append(name)
            continue

        try:
            doc = frappe.get_doc({
                "doctype": "Price List",
                "price_list_name": name,
                "currency": CURRENCY,
                "selling": selling,
                "buying": buying,
                "enabled": 1,
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

    print(f"\nPENDING: {PENDING_NOTE}")
    print(
        "\nNo Items or Item Prices created — only the Price List containers "
        "exist. Actual rates must be entered once management confirms the "
        "service catalogue and pricing (see the data-request document, "
        "Section 07)."
    )
