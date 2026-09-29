# Al Hekma Hospital — Give the DEMO Medication Request a readable drug name
#
# WHY: "Medication Item" on Medication Request is a Link to Item, and
# Item's Link control shows the raw item_code (e.g.
# "TEST-MED-PARACETAMOL-500"), not the friendly item_name — that's how
# Frappe Link fields render by default.
#
# FIX: create a proper "Medication" master record (the Healthcare app's
# actual drug catalogue doctype). Its autoname format is
# "{dosage_form} {generic_name} {strength}{strength_uom}" — meaning the
# record's own name IS a readable label by construction (e.g.
# "Tablet (TEST) Paracetamol (TEST) 500mg"). We then link the existing
# demo Medication Request's optional "medication" field to it.
#
# Everything created here is clearly labeled TEST — not a real drug
# catalogue entry.
#
# Run with:
#   bench --site alhekma.local execute alhekma.patches.link_demo_medication_name.run
#
# Safe to re-run: skips anything that already exists.

import frappe


def _get_or_create(doctype, filters, values):
    name = frappe.db.exists(doctype, filters)
    if name:
        return name if isinstance(name, str) else frappe.db.get_value(doctype, filters, "name")
    doc = frappe.get_doc({"doctype": doctype, **values})
    doc.insert(ignore_permissions=True)
    return doc.name


def run():
    # 1. Medication Class (tree doctype — this becomes its own root,
    # which is fine since no "All Medication Classes" root exists yet)
    medication_class = _get_or_create(
        "Medication Class",
        {"medication_class": "Analgesics (TEST)"},
        {"medication_class": "Analgesics (TEST)", "is_group": 0},
    )

    # 2. UOM for strength (mg is not guaranteed to exist by default)
    uom = _get_or_create("UOM", {"uom_name": "mg"}, {"uom_name": "mg"})

    # 3. Dosage Form — reuse the one from the earlier demo script
    dosage_form = frappe.db.exists("Dosage Form", {"dosage_form": "Tablet (TEST)"})
    if not dosage_form:
        frappe.throw(
            "Dosage Form 'Tablet (TEST)' not found — run "
            "create_demo_medication_request.py first."
        )

    # 4. The Medication master record itself.
    # linked_items is deliberately left empty — linking it to a real
    # stock Item requires a Price List + Item Group setup that's out
    # of scope for this naming-only fix.
    medication_name = _get_or_create(
        "Medication",
        {"generic_name": "Paracetamol (TEST)", "dosage_form": dosage_form, "strength": 500},
        {
            "generic_name": "Paracetamol (TEST)",
            "medication_class": medication_class,
            "strength": 500,
            "strength_uom": uom,
            "dosage_form": dosage_form,
        },
    )

    # 5. Find the demo Medication Request created earlier and link it
    med_request = frappe.db.get_value(
        "Medication Request",
        {"medication_item": "TEST-MED-PARACETAMOL-500"},
        "name",
    )
    if not med_request:
        frappe.throw(
            "No demo Medication Request found — run "
            "create_demo_medication_request.py first."
        )

    frappe.db.set_value("Medication Request", med_request, "medication", medication_name)
    frappe.db.commit()

    print("=== DONE ===")
    print(f"Medication master created: {medication_name}")
    print(f"Linked to Medication Request: {med_request}")
    print(
        "\nRefresh the Medication Request page (test-027 or test-035) — "
        "the new 'Medication' field should now show a readable name "
        f"instead of a raw item code: {medication_name}"
    )
