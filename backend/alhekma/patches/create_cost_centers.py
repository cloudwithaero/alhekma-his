# Al Hekma Hospital — Cost Center Tree creation script
# Source: AlHekma_ERPNext_Master_Tree_EN.xmind.md, Section 06
#
# Run with:
#   bench --site alhekma.local execute alhekma.patches.create_cost_centers.run
#
# SCOPE: Only the Cost Center tree. Chart of Accounts is NOT touched —
# it contains a [D: accounts] item (Banks) requiring real bank account
# data from hospital management, which must not be invented.
#
# Future [F] items (Internal Laboratory, MRI) are excluded per the
# document's own coding — they do not exist yet operationally.
#
# Safe to re-run: skips anything that already exists.

import frappe

COMPANY = "Al Hekma Hospital"
ABBR = "hikma"

# (cost_center_name, parent_name_or_None)
# None parent = reports directly to the top-level root cost center
TREE = [
    ("Final / Revenue-Generating Centers", None),
    ("Emergency Department", "Final / Revenue-Generating Centers"),
    ("ICU and Stroke Services", "Final / Revenue-Generating Centers"),
    ("Inpatient Services", "Final / Revenue-Generating Centers"),
    ("Outpatient Clinics", "Final / Revenue-Generating Centers"),
    ("Surgery and Procedures", "Final / Revenue-Generating Centers"),
    ("Ambulance Service", "Final / Revenue-Generating Centers"),

    ("Intermediate / Mixed Medical Centers", None),
    ("Radiology", "Intermediate / Mixed Medical Centers"),
    ("Pharmacy", "Intermediate / Mixed Medical Centers"),
    ("CSSD", "Intermediate / Mixed Medical Centers"),

    ("Administrative and Logistics Centers", None),
    ("General Administration and Chairman-Reporting Functions", "Administrative and Logistics Centers"),
    ("Medical Directorate and Medical Administration", "Administrative and Logistics Centers"),
    ("Nursing Management and Supervision", "Administrative and Logistics Centers"),
    ("Administrative Directorate", "Administrative and Logistics Centers"),
    ("Quality and Risk Management", "Administrative and Logistics Centers"),
    ("Human Resources", "Administrative and Logistics Centers"),
    ("Reception, Registration, and Admission", "Administrative and Logistics Centers"),
    ("Medical Records", "Administrative and Logistics Centers"),
    ("Finance and Accounting", "Administrative and Logistics Centers"),
    ("Claims and Payers", "Administrative and Logistics Centers"),
    ("Engineering, Maintenance, and IT", "Administrative and Logistics Centers"),
    ("Procurement", "Administrative and Logistics Centers"),
    ("General Stores", "Administrative and Logistics Centers"),
    ("Security", "Administrative and Logistics Centers"),
    ("Housekeeping and Waste Management", "Administrative and Logistics Centers"),
    ("Laundry", "Administrative and Logistics Centers"),
    ("Infection Prevention and Control", "Administrative and Logistics Centers"),
    ("Strategy and Transformation", "Administrative and Logistics Centers"),
    ("Legal Affairs", "Administrative and Logistics Centers"),

    # NOTE: "Future Centers" group (Internal Laboratory [F], MRI [F])
    # intentionally excluded — not operational yet per the document.
]


def _docname(name):
    return f"{name} - {ABBR}"


def run():
    created, skipped, failed = [], [], []

    # The root cost center that ships automatically with every Company
    root_name = frappe.db.get_value(
        "Cost Center",
        {"company": COMPANY, "is_group": 1, "parent_cost_center": ["is", "not set"]},
        "name",
    )

    if not root_name:
        frappe.throw(f"Could not find a root Cost Center for company {COMPANY}")

    print(f"Root cost center resolved as: {root_name}")

    for name, parent_name in TREE:
        docname = _docname(name)

        if frappe.db.exists("Cost Center", docname):
            skipped.append(docname)
            continue

        parent_docname = _docname(parent_name) if parent_name else root_name

        if not frappe.db.exists("Cost Center", parent_docname):
            failed.append((docname, f"parent '{parent_docname}' not found yet"))
            continue

        try:
            doc = frappe.get_doc({
                "doctype": "Cost Center",
                "cost_center_name": name,
                "company": COMPANY,
                "parent_cost_center": parent_docname,
                "is_group": 1,  # corrected in a follow-up pass, same as Departments
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
            "\nSome cost centers could not be created because their parent "
            "was not yet created. Re-run this script — it is safe and "
            "idempotent, and will pick up where it left off."
        )
