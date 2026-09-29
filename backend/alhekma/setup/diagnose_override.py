# Diagnostic: trace what set_service_unit_properties does for a Room leaf
# bench --site alhekma.local execute alhekma.setup.diagnose_override.run


def run():
    import frappe
    from frappe.utils import cint

    # Simulate exactly what the creation script does for Triage (allow_appt=0)
    doc = frappe.new_doc("Healthcare Service Unit")
    doc.healthcare_service_unit_name   = "_DIAG_TEST_TRIAGE_"
    doc.parent_healthcare_service_unit = "Emergency Department - hikma"
    doc.service_unit_type              = "Room"
    doc.is_group                       = 0
    doc.allow_appointments             = 0
    doc.company                        = "alhikma_hospital"
    doc.flags.allow_appointments_override = True

    print("=== Before set_service_unit_properties ===")
    print(f"  doc.allow_appointments = {doc.allow_appointments}")
    print(f"  doc.flags.allow_appointments_override = {getattr(doc.flags, 'allow_appointments_override', 'NOT SET')}")
    print(f"  type(doc).__name__ = {type(doc).__name__}")
    print(f"  type(doc).__module__ = {type(doc).__module__}")

    # Call the method directly without insert
    doc.set_service_unit_properties()

    print("=== After set_service_unit_properties ===")
    print(f"  doc.allow_appointments = {doc.allow_appointments}")
    print(f"  doc.inpatient_occupancy = {doc.inpatient_occupancy}")

    # Now simulate GP Clinic (allow_appt=1)
    doc2 = frappe.new_doc("Healthcare Service Unit")
    doc2.healthcare_service_unit_name   = "_DIAG_TEST_GP_"
    doc2.parent_healthcare_service_unit = "Outpatient Clinics - hikma"
    doc2.service_unit_type              = "Room"
    doc2.is_group                       = 0
    doc2.allow_appointments             = 1
    doc2.company                        = "alhikma_hospital"
    doc2.flags.allow_appointments_override = True

    doc2.set_service_unit_properties()

    print("=== GP Clinic after set_service_unit_properties ===")
    print(f"  doc2.allow_appointments = {doc2.allow_appointments}")
    print(f"  doc2.inpatient_occupancy = {doc2.inpatient_occupancy}")

    return "done"
