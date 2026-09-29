# Al Hekma Hospital — Department Tree Creation Script
# Source: AlHekma_ERPNext_Master_Tree_EN.xmind.md, Section 02
#
# Run with:
#   bench --site alhekma.local execute alhekma.patches.create_departments.run
#
# Safe to re-run: skips any department that already exists.
# Does NOT touch, merge, or delete any existing department.

import frappe

COMPANY = "alhikma_hospital"
ABBR = "hikma"

# (department_name, parent_department_name_or_None)
# None parent = reports directly to the top-level "Al Hekma Hospital" root
TREE = [
    # Functions reporting directly to the Chairman
    ("Strategy and Transformation", None),
    ("Transformation and Project Management", "Strategy and Transformation"),
    ("Data Governance and Integrations", "Strategy and Transformation"),
    ("ERPNext Application Management", "Strategy and Transformation"),
    ("Legal Affairs", None),

    # Medical Directorate
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

    # Administrative Directorate
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

    # Financial Directorate
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


def _department_docname(department_name, parent_name):
    """Frappe autonames Department as '<name> - <abbr>' at the top level,
    but nested tree records still resolve via this same convention."""
    return f"{department_name} - {ABBR}"


def run():
    created = []
    skipped = []
    failed = []

    # Root department that ships by default with every Frappe site
    root_name = "All Departments"

    if not frappe.db.exists("Department", root_name):
        frappe.throw(f"Root department '{root_name}' not found")

    print(f"Root department resolved as: {root_name}")

    for department_name, parent_name in TREE:
        docname = _department_docname(department_name, parent_name)

        if frappe.db.exists("Department", docname):
            skipped.append(docname)
            continue

        parent_docname = (
            _department_docname(parent_name, None) if parent_name else root_name
        )

        if not frappe.db.exists("Department", parent_docname):
            failed.append((docname, f"parent '{parent_docname}' not found yet"))
            continue

        try:
            doc = frappe.get_doc({
                "doctype": "Department",
                "department_name": department_name,
                "company": COMPANY,
                "parent_department": parent_docname,
                "is_group": 1,  # safe default; can be corrected later per node
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

    if failed:
        print(
            "\nSome departments could not be created because their parent "
            "was not yet created. Re-run this script again — it is safe "
            "and idempotent, and will pick up where it left off."
        )
