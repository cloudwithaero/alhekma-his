# Al Hekma Hospital — Placeholder Rooms/Beds for undetermined counts
# Source: AlHekma_ERPNext_Master_Tree_EN.xmind.md, Section 03
#
# SCOPE: Only the units marked [D: count and identifiers] — where the
# document does not yet specify a real number. Each placeholder unit
# is named ending in "(PENDING - confirm count/number with management)"
# so nobody mistakes it for verified data.
#
# VIP-01..05 and OR-01..03 are NOT touched here — they already have
# confirmed [R] identifiers from the document and were created earlier.
#
# Run with:
#   bench --site alhekma.local execute alhekma.patches.create_placeholder_units.run
#
# Safe to re-run: skips anything that already exists.
# EASY TO UNDO: once real counts arrive, just rename/delete these
# specific placeholder records — nothing else depends on them.

import frappe

COMPANY = "Al Hekma Hospital"
ABBR = "hikma"
PENDING_SUFFIX = " (PENDING - confirm count/number with management)"

# (unit_name, parent_hsu_name, placeholder_count)
# parent_hsu_name must be an EXISTING Healthcare Service Unit (already created)
PLACEHOLDER_GROUPS = [
    ("Examination and Treatment Room", "Emergency Department", 3),
    ("Observation Bed", "Emergency Department", 4),
    ("ICU Bed", "Intensive Care Unit", 4),
    ("Stroke Bed", "Stroke Unit", 4),
    ("Standard Room", "Inpatient Services", 5),
]


def _docname(name):
    return f"{name} - {ABBR}"


def run():
    created, skipped, failed = [], [], []

    for unit_label, parent_hsu, count in PLACEHOLDER_GROUPS:
        parent_docname = _docname(parent_hsu)

        if not frappe.db.exists("Healthcare Service Unit", parent_docname):
            failed.append((unit_label, f"parent HSU '{parent_docname}' not found"))
            continue

        for i in range(1, count + 1):
            unit_name = f"{unit_label} {i}{PENDING_SUFFIX}"
            docname = _docname(unit_name)

            if frappe.db.exists("Healthcare Service Unit", docname):
                skipped.append(docname)
                continue

            try:
                doc = frappe.get_doc({
                    "doctype": "Healthcare Service Unit",
                    "healthcare_service_unit_name": unit_name,
                    "company": COMPANY,
                    "parent_healthcare_service_unit": parent_docname,
                    "is_group": 1,  # placeholder group — no service type assigned yet
                })
                doc.insert(ignore_permissions=True)
                created.append(doc.name)
            except Exception as e:
                failed.append((docname, str(e)))

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
        "\nNOTE: All created units are placeholders with counts guessed by "
        "the implementer, NOT confirmed hospital data. Each is named with "
        "'(PENDING - confirm count/number with management)' so they are "
        "impossible to mistake for real data. Once management confirms "
        "real numbers and identifiers, these placeholder records should "
        "be renamed (or deleted and replaced) accordingly."
    )
