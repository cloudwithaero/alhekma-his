# Al Hekma Hospital — override verification utility
# bench --site alhekma.local execute alhekma.setup.verify_override.check_hsu_override


def check_hsu_override():
    """
    Verify that Frappe's runtime resolves Healthcare Service Unit
    to AlHekmaHealthcareServiceUnit from apps/alhekma.
    """
    import frappe

    doc = frappe.get_doc("Healthcare Service Unit", "All Healthcare Service Units - hikma")
    actual_class = type(doc).__name__
    actual_module = type(doc).__module__

    expected_class = "AlHekmaHealthcareServiceUnit"
    expected_module = "alhekma.overrides.healthcare_service_unit"

    result = {
        "actual_class": actual_class,
        "actual_module": actual_module,
        "expected_class": expected_class,
        "expected_module": expected_module,
        "class_match": actual_class == expected_class,
        "module_match": actual_module == expected_module,
        "override_active": actual_class == expected_class and actual_module == expected_module,
    }

    print("=== HSU Override Verification ===")
    for k, v in result.items():
        print(f"  {k}: {v}")

    return result
