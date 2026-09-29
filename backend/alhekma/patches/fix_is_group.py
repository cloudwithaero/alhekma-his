# Al Hekma Hospital — Fix is_group flags per Section 02 of the master document
#
# Logic: a department is a GROUP if and only if it has at least one child
# department in the approved TREE list. Otherwise it is a LEAF (is_group=0).
#
# Run with:
#   bench --site alhekma.local execute alhekma.patches.fix_is_group.run

import frappe

ABBR = "hikma"

# Same TREE as create_departments.py
TREE = [
    ("Strategy and Transformation", None),
    ("Transformation and Project Management", "Strategy and Transformation"),
    ("Data Governance and Integrations", "Strategy and Transformation"),
    ("ERPNext Application Management", "Strategy and Transformation"),
    ("Legal Affairs", None),
    ("Medical Directorate", None),
    ("Medical Administration and Medical Staff Affairs", "Medical Directorate"),
    ("Physician Credentialing and Clinical Privileges", "Medical Administration and Medical Staff Affairs"),
    ("Physician Scheduling and Coverage", "Medical Administration and Medical Staff Affairs"),
    ("Medical Documentation and Performance", "Medical Administration and Medical Staff Affairs"),
    ("Emergency Department", "Medical Directorate"),
    ("Critical Care and Stroke Services", "Medical Directorate"),
    ("Intensive Care Unit", "Critical Care and Stroke Services"),
    ("Stroke Unit", "Critical Care and Stroke Services"),
    ("Surgery and Operating Rooms", "Medical Directorate"),
    ("Operating Theatre Complex", "Surgery and Operating Rooms"),
    ("Post-Anesthesia Care Unit", "Surgery and Operating Rooms"),
    ("Inpatient Services", "Medical Directorate"),
    ("Outpatient Clinics", "Medical Directorate"),
    ("General Practitioner Clinic", "Outpatient Clinics"),
    ("Specialty Clinics", "Outpatient Clinics"),
    ("Nursing Department", "Medical Directorate"),
    ("Emergency Nursing", "Nursing Department"),
    ("ICU and Stroke Nursing", "Nursing Department"),
    ("OR and Recovery Nursing", "Nursing Department"),
    ("Inpatient Nursing", "Nursing Department"),
    ("Outpatient Nursing", "Nursing Department"),
    ("Radiology Department", "Medical Directorate"),
    ("Pharmacy Department", "Medical Directorate"),
    ("Central Sterile Services Department - CSSD", "Medical Directorate"),
    ("Infection Prevention and Control", "Medical Directorate"),
    ("Ambulance Service", "Medical Directorate"),
    ("Internal Laboratory", "Medical Directorate"),
    ("Administrative Directorate", None),
    ("Quality and Risk Management", "Administrative Directorate"),
    ("Quality and Continuous Improvement", "Quality and Risk Management"),
    ("Patient Safety and Risk Management", "Quality and Risk Management"),
    ("Accreditation Coordination", "Quality and Risk Management"),
    ("Complaints and Patient Experience", "Quality and Risk Management"),
    ("Human Resources and Personnel Affairs", "Administrative Directorate"),
    ("Workforce Planning and Recruitment", "Human Resources and Personnel Affairs"),
    ("Personnel, Attendance, and Leave", "Human Resources and Personnel Affairs"),
    ("Training and Performance Evaluation", "Human Resources and Personnel Affairs"),
    ("Payroll and Benefits", "Human Resources and Personnel Affairs"),
    ("Patient Access and Services", "Administrative Directorate"),
    ("Reception and Information", "Patient Access and Services"),
    ("Registration and Admission", "Patient Access and Services"),
    ("Appointment Coordination", "Patient Access and Services"),
    ("Patient Relations", "Patient Access and Services"),
    ("Health Information Management and Medical Records", "Administrative Directorate"),
    ("Medical Records and Coding", "Health Information Management and Medical Records"),
    ("Record Completion and Review", "Health Information Management and Medical Records"),
    ("Disclosure, Copies, and Retention", "Health Information Management and Medical Records"),
    ("Engineering, Maintenance, and Information Technology", "Administrative Directorate"),
    ("Engineering and Maintenance", "Engineering, Maintenance, and Information Technology"),
    ("Preventive and Corrective Maintenance", "Engineering and Maintenance"),
    ("Utilities and Technical Safety", "Engineering and Maintenance"),
    ("Information Technology and Systems", "Engineering, Maintenance, and Information Technology"),
    ("Infrastructure and Support", "Information Technology and Systems"),
    ("Information Security and User Administration", "Information Technology and Systems"),
    ("ERPNext Implementer", "Information Technology and Systems"),
    ("Support Services", "Administrative Directorate"),
    ("Security", "Support Services"),
    ("Housekeeping and Waste Management", "Support Services"),
    ("Laundry", "Support Services"),
    ("Financial Directorate", None),
    ("Procurement", "Financial Directorate"),
    ("Requisitions, Quotations, and Purchase Orders", "Procurement"),
    ("Supplier Qualification and Evaluation", "Procurement"),
    ("General Stores", "Financial Directorate"),
    ("General Accounting", "Financial Directorate"),
    ("General Ledger and Journal Entries", "General Accounting"),
    ("Accounts Payable", "General Accounting"),
    ("Accounts Receivable and Collection", "General Accounting"),
    ("Asset and Depreciation Financial Control", "General Accounting"),
    ("Treasury", "Financial Directorate"),
    ("Treasury A", "Treasury"),
    ("Treasury B", "Treasury"),
    ("Treasury C", "Treasury"),
    ("Banks and Reconciliations", "Treasury"),
    ("Patient Accounts and Billing", "Financial Directorate"),
    ("Charge and Invoice Review", "Patient Accounts and Billing"),
    ("Discounts and Credit Limits", "Patient Accounts and Billing"),
    ("Collection and Refunds", "Patient Accounts and Billing"),
    ("Claims and Payers", "Financial Directorate"),
    ("Insurance Reception and Patient Data Entry", "Claims and Payers"),
    ("Claims Preparation and Review", "Claims and Payers"),
    ("Claims Approval and Submission", "Claims and Payers"),
    ("Denials, Reconciliation, and Collection Follow-up", "Claims and Payers"),
    ("Financial Planning and Control", "Financial Directorate"),
    ("Budgets and Forecasts", "Financial Planning and Control"),
    ("Cost and Profitability Accounting", "Financial Planning and Control"),
    ("Management Reporting", "Financial Planning and Control"),
]


def run():
    parent_names = {parent for _, parent in TREE if parent is not None}

    updated_to_group = []
    updated_to_leaf = []
    unchanged = []
    not_found = []

    for department_name, _ in TREE:
        docname = f"{department_name} - {ABBR}"

        if not frappe.db.exists("Department", docname):
            not_found.append(docname)
            continue

        should_be_group = 1 if department_name in parent_names else 0
        current_is_group = frappe.db.get_value("Department", docname, "is_group")

        if current_is_group == should_be_group:
            unchanged.append(docname)
            continue

        frappe.db.set_value("Department", docname, "is_group", should_be_group)

        if should_be_group:
            updated_to_group.append(docname)
        else:
            updated_to_leaf.append(docname)

    frappe.db.commit()

    print("\n=== SUMMARY ===")
    print(f"Set to GROUP (has children): {len(updated_to_group)}")
    print(f"Set to LEAF (no children):   {len(updated_to_leaf)}")
    print(f"Already correct:             {len(unchanged)}")
    print(f"Not found:                   {len(not_found)}")

    if updated_to_leaf:
        print("\n--- Set to LEAF ---")
        for name in updated_to_leaf:
            print(f"  {name}")

    if not_found:
        print("\n--- NOT FOUND (skipped) ---")
        for name in not_found:
            print(f"  {name}")
