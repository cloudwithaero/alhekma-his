import frappe


def create_doctype(name, fields, autoname="field:name", title_field=None):
    if frappe.db.exists("DocType", name):
        print(f"EXISTS: {name}")
        return

    doc = frappe.get_doc(
        {
            "doctype": "DocType",
            "name": name,
            "module": "Al Hekma Hospital",
            "custom": 1,
            "autoname": autoname,
            "fields": fields,
        }
    )

    if title_field:
        doc.title_field = title_field

    doc.insert(ignore_permissions=True)

    print(f"CREATED: {name}")


def run():
    # ---------------------------------------------------------
    # Kiosk Device
    # ---------------------------------------------------------
    create_doctype(
        "Kiosk Device",
        [
            {
                "fieldname": "device_id",
                "label": "Device ID",
                "fieldtype": "Data",
                "reqd": 1,
                "unique": 1,
                "in_list_view": 1,
            },
            {
                "fieldname": "device_name",
                "label": "Device Name",
                "fieldtype": "Data",
                "reqd": 1,
                "in_list_view": 1,
            },
            {
                "fieldname": "healthcare_service_unit",
                "label": "Healthcare Service Unit",
                "fieldtype": "Link",
                "options": "Healthcare Service Unit",
                "reqd": 1,
                "in_list_view": 1,
            },
            {
                "fieldname": "enabled",
                "label": "Enabled",
                "fieldtype": "Check",
                "default": 1,
                "in_list_view": 1,
            },
            {
                "fieldname": "description",
                "label": "Description",
                "fieldtype": "Small Text",
            },
        ],
        autoname="field:device_id",
        title_field="device_name",
    )

    # ---------------------------------------------------------
    # Staff Shift Presence
    # ---------------------------------------------------------
    create_doctype(
        "Staff Shift Presence",
        [
            {
                "fieldname": "employee",
                "label": "Employee",
                "fieldtype": "Link",
                "options": "Employee",
                "reqd": 1,
                "in_list_view": 1,
            },
            {
                "fieldname": "user",
                "label": "User",
                "fieldtype": "Link",
                "options": "User",
                "reqd": 1,
                "in_list_view": 1,
            },
            {
                "fieldname": "kiosk_device",
                "label": "Kiosk Device",
                "fieldtype": "Link",
                "options": "Kiosk Device",
                "reqd": 1,
                "in_list_view": 1,
            },
            {
                "fieldname": "healthcare_service_unit",
                "label": "Healthcare Service Unit",
                "fieldtype": "Link",
                "options": "Healthcare Service Unit",
                "reqd": 1,
                "in_list_view": 1,
            },
            {
                "fieldname": "started_at",
                "label": "Started At",
                "fieldtype": "Datetime",
                "reqd": 1,
                "in_list_view": 1,
            },
            {
                "fieldname": "ended_at",
                "label": "Ended At",
                "fieldtype": "Datetime",
                "in_list_view": 1,
            },
            {
                "fieldname": "status",
                "label": "Status",
                "fieldtype": "Select",
                "options": "Active\nEnded\nRevoked",
                "default": "Active",
                "reqd": 1,
                "in_list_view": 1,
            },
            {
                "fieldname": "notes",
                "label": "Notes",
                "fieldtype": "Small Text",
            },
        ],
        autoname="format:SSP-.#####",
    )

    frappe.db.commit()
    print("Kiosk/PRESENCE DocTypes created successfully.")

