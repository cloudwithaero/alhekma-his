# Al Hekma Hospital — one-time HSU Type correction
# Callable via: bench --site alhekma.local execute alhekma.setup.fix_hsu_types.fix_bed_type


def fix_bed_type():
    """
    Fix the Bed Healthcare Service Unit Type to the approved state:
      allow_appointments  = 0
      inpatient_occupancy = 1

    Uses doc.save() so the standard HealthcareServiceUnitType validator runs
    and confirms the mutual-exclusion rule is satisfied.
    Only these two fields are changed; all other Bed fields are untouched.
    """
    import frappe

    doc = frappe.get_doc("Healthcare Service Unit Type", "Bed")

    pre_allow = int(doc.allow_appointments)
    pre_inpatient = int(doc.inpatient_occupancy)

    doc.allow_appointments = 0
    doc.inpatient_occupancy = 1

    doc.save(ignore_permissions=True)
    frappe.db.commit()

    # Re-fetch from DB to confirm persisted values
    doc2 = frappe.get_doc("Healthcare Service Unit Type", "Bed")

    result = {
        "allow_appointments_before": pre_allow,
        "allow_appointments_after": int(doc2.allow_appointments),
        "inpatient_occupancy_before": pre_inpatient,
        "inpatient_occupancy_after": int(doc2.inpatient_occupancy),
        "overlap_appointments": int(doc2.overlap_appointments),
        "disabled": int(doc2.disabled),
        "is_billable": int(doc2.is_billable),
        "status": (
            "OK"
            if int(doc2.allow_appointments) == 0 and int(doc2.inpatient_occupancy) == 1
            else "FAILED"
        ),
    }

    print("=== Bed HSU Type fix ===")
    for k, v in result.items():
        print(f"  {k}: {v}")

    return result
