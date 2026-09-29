import frappe
from frappe import _


def _get_active_presence(user):
    return frappe.db.get_value(
        "Staff Shift Presence",
        {
            "user": user,
            "status": "Active",
        },
        [
            "name",
            "kiosk_device",
            "healthcare_service_unit",
            "started_at",
        ],
        as_dict=True,
        order_by="creation desc",
    )


def _get_unit_tree_names(service_unit):
    unit = frappe.db.get_value(
        "Healthcare Service Unit",
        service_unit,
        ["name", "lft", "rgt"],
        as_dict=True,
    )

    if not unit:
        return []

    if unit.lft is None or unit.rgt is None:
        return [unit.name]

    return frappe.get_all(
        "Healthcare Service Unit",
        filters={
            "lft": [">=", unit.lft],
            "rgt": ["<=", unit.rgt],
        },
        pluck="name",
    )


@frappe.whitelist()
def get_dashboard():
    """
    Return nursing dashboard data for the authenticated user.

    Access requires:
    - authenticated user
    - Nursing role
    - active Staff Shift Presence
    """

    user = frappe.session.user

    if not user or user == "Guest":
        frappe.throw(
            _("Authentication required."),
            frappe.PermissionError,
        )

    roles = frappe.get_roles(user)

    if "Nursing" not in roles:
        frappe.throw(
            _("Nursing access is required."),
            frappe.PermissionError,
        )

    presence = _get_active_presence(user)

    if not presence:
        frappe.throw(
            _(
                "No active staff shift presence was found. "
                "Please register at the fixed kiosk first."
            ),
            frappe.PermissionError,
        )

    service_unit = presence.healthcare_service_unit

    if not service_unit:
        frappe.throw(
            _("Your active presence has no Healthcare Service Unit.")
        )

    # The presence may point to a Ward/Unit group.
    # Include all descendants so beds underneath that unit
    # are included as patient locations.
    service_units = _get_unit_tree_names(service_unit)

    if not service_units:
        service_units = [service_unit]

    # ---------------------------------------------------------
    # Active inpatient occupancies in the current unit tree
    # ---------------------------------------------------------

    occupancies = frappe.get_all(
        "Inpatient Occupancy",
        filters={
            "service_unit": ["in", service_units],
            "left": 0,
            "parenttype": "Inpatient Record",
        },
        fields=[
            "parent",
            "service_unit",
            "check_in",
            "check_out",
        ],
        order_by="check_in desc",
    )

    if not occupancies:
        return {
            "location": service_unit,
            "presence": presence,
            "patients": [],
            "counts": {
                "patients": 0,
                "tasks": 0,
                "medications": 0,
                "alerts": 0,
            },
        }

    # Avoid duplicate inpatient records if data contains
    # more than one active occupancy row.
    inpatient_names = []
    seen = set()

    for occupancy in occupancies:
        parent = occupancy.parent

        if parent and parent not in seen:
            seen.add(parent)
            inpatient_names.append(parent)

    records = frappe.get_all(
        "Inpatient Record",
        filters={
            "name": ["in", inpatient_names],
            "status": "Admitted",
        },
        fields=[
            "name",
            "patient",
            "patient_name",
            "gender",
            "status",
            "admitted_datetime",
            "expected_discharge",
        ],
    )

    record_map = {record.name: record for record in records}

    patients = []
    added_records = set()

    for occupancy in occupancies:
        record = record_map.get(occupancy.parent)

        if not record:
            continue

        if record.name in added_records:
            continue

        added_records.add(record.name)

        patients.append(
            {
                "inpatient_record": record.name,
                "patient": record.patient,
                "patient_name": record.patient_name,
                "gender": record.gender,
                "status": record.status,
                "service_unit": occupancy.service_unit,
                "check_in": occupancy.check_in,
                "admitted_datetime": record.admitted_datetime,
                "expected_discharge": record.expected_discharge,
            }
        )

    return {
        "location": service_unit,
        "presence": presence,
        "patients": patients,
        "counts": {
            "patients": len(patients),
            "tasks": 0,
            "medications": 0,
            "alerts": 0,
        },
    }
@frappe.whitelist()
def get_patient_profile(inpatient_record):
    """
    Return the authenticated nurse's allowed inpatient record
    with current occupancy, patient demographics and latest vital signs.
    """

    user = frappe.session.user

    if user == "Guest":
        frappe.throw("Authentication required")

    roles = frappe.get_roles(user)

    if "Nursing" not in roles:
        frappe.throw("Nursing access required")

    presence = _get_active_presence(user)

    if not presence:
        frappe.throw("No active staff shift presence")

    service_unit = presence.healthcare_service_unit

    if not service_unit:
        frappe.throw("Current presence has no Healthcare Service Unit")

    allowed_units = _get_unit_tree_names(service_unit)

    # Read only fields that actually exist in this Healthcare version.
    inpatient_meta = frappe.get_meta("Inpatient Record")

    wanted_inpatient_fields = [
        "patient",
        "patient_name",
        "status",
        "admitted_datetime",
        "discharged_datetime",
        "discharge_datetime",
        "expected_discharge",
        "expected_discharge_date",
        "admission_encounter",
    ]

    existing_inpatient_fields = {
        field.fieldname for field in inpatient_meta.fields
    }

    safe_inpatient_fields = [
        field
        for field in wanted_inpatient_fields
        if field in existing_inpatient_fields
    ]

    inpatient = frappe.db.get_value(
        "Inpatient Record",
        inpatient_record,
        safe_inpatient_fields,
        as_dict=True,
    )

    if not inpatient:
        frappe.throw("Inpatient Record not found")

    inpatient["name"] = inpatient_record

    if inpatient.status != "Admitted":
        frappe.throw("Patient is not currently admitted")

    # Find current occupancy for this inpatient record.
    occupancy_rows = frappe.get_all(
        "Inpatient Occupancy",
        filters={
            "parent": inpatient_record,
            "parenttype": "Inpatient Record",
            "left": 0,
        },
        fields=[
            "name",
            "service_unit",
            "check_in",
            "check_out",
            "left",
        ],
        order_by="check_in desc",
        limit_page_length=20,
    )

    current_occupancy = None

    for row in occupancy_rows:
        if row.service_unit in allowed_units:
            current_occupancy = row
            break

    if not current_occupancy:
        frappe.throw(
            "This patient is not currently assigned to your Healthcare Service Unit"
        )

    # Patient demographics.
    patient = None

    patient_fields = [
        "name",
        "patient_name",
        "sex",
        "dob",
        "blood_group",
        "mobile",
        "status",
    ]

    patient_meta = frappe.get_meta("Patient")
    existing_patient_fields = {
        field.fieldname for field in patient_meta.fields
    }

    safe_patient_fields = [
        field
        for field in patient_fields
        if field in existing_patient_fields
    ]

    if inpatient.patient and safe_patient_fields:
        patient = frappe.db.get_value(
            "Patient",
            inpatient.patient,
            safe_patient_fields,
            as_dict=True,
        )

    # Latest vital signs.
    vital_signs = []

    try:
        vital_meta = frappe.get_meta("Vital Signs")
        vital_fields = {
            field.fieldname for field in vital_meta.fields
        }

        candidates = [
            "name",
            "patient",
            "patient_name",
            "signs_date",
            "signs_time",
            "date",
            "time",
            "temperature",
            "pulse",
            "respiratory_rate",
            "systolic_bp",
            "diastolic_bp",
            "systolic_blood_pressure",
            "diastolic_blood_pressure",
            "weight",
            "height",
            "bmi",
            "oxygen_saturation",
            "spo2",
        ]

        safe_vital_fields = [
            field for field in candidates
            if field in vital_fields
        ]

        if "patient" in vital_fields and safe_vital_fields:
            order_field = (
                "signs_date"
                if "signs_date" in vital_fields
                else "creation"
            )

            vital_signs = frappe.get_all(
                "Vital Signs",
                filters={
                    "patient": inpatient.patient,
                },
                fields=safe_vital_fields,
                order_by=f"{order_field} desc, creation desc",
                limit_page_length=5,
            )

    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            "Nursing patient profile - vital signs lookup failed",
        )

    return {
        "patient": patient,
        "inpatient_record": {
            "name": inpatient.name,
            "patient": inpatient.patient,
            "patient_name": inpatient.patient_name,
            "status": inpatient.status,
            "admitted_datetime": inpatient.admitted_datetime,
            "discharged_datetime": inpatient.get("discharged_datetime") or inpatient.get("discharge_datetime"),
            "expected_discharge": inpatient.get("expected_discharge") or inpatient.get("expected_discharge_date"),
            "admission_encounter": inpatient.get("admission_encounter"),
        },
        "occupancy": current_occupancy,
        "location": {
            "current_service_unit": service_unit,
            "patient_service_unit": current_occupancy.service_unit,
            "kiosk_device": presence.kiosk_device,
        },
        "vital_signs": vital_signs,
    }
