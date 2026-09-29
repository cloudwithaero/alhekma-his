import frappe
from healthcare.healthcare.utils import get_children as healthcare_get_children


@frappe.whitelist()
def get_root(
    doctype="Healthcare Service Unit",
    parent=None,
    company=None,
    is_root=False,
):
    if doctype != "Healthcare Service Unit":
        return []

    if not company:
        return []

    root = frappe.db.get_value(
        "Healthcare Service Unit",
        {
            "company": company,
            "parent_healthcare_service_unit": ["is", "not set"],
        },
        "name",
        order_by="lft asc",
    )

    if not root:
        return []

    # Initial tree request: return the real Healthcare root.
    if not parent:
        return [{"value": root, "expandable": 1}]

    # Frappe TreeView may use the selected Company as the visual root.
    # Bridge Company -> Healthcare Service Unit root.
    if parent == company:
        return [{"value": root, "expandable": 1}]

    # Normal Healthcare Service Unit children.
    return healthcare_get_children(
        doctype=doctype,
        parent=parent,
        company=company,
        is_root=False,
    )
