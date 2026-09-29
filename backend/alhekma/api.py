# Al Hekma Hospital — Badge + PIN kiosk login API
#
# Place this file at: ~/frappe-bench/apps/alhekma/alhekma/api.py
# (If that file already exists with other content, paste these two
# functions + the imports into it instead of overwriting.)
#
# Exposes:
#   POST /api/method/alhekma.api.badge_login   (guest-allowed — this IS the login)
#   POST /api/method/alhekma.api.set_employee_pin  (logged-in System Manager only —
#       used once per employee to register/replace their badge + PIN)
#
# SECURITY NOTE: a 4-digit PIN only has 10,000 combinations, so
# badge_login is rate-limited per badge_code (not per IP, since many
# people share the same kiosk IP): 5 wrong PINs locks that badge for
# 15 minutes, independent of Frappe's own login lockouts on real
# accounts (which this endpoint never touches).

import frappe
from frappe import _
from frappe.utils.password import check_password, set_encrypted_password

MAX_ATTEMPTS = 5
LOCKOUT_SECONDS = 15 * 60
CACHE_PREFIX = "badge_pin_attempts:"


@frappe.whitelist(allow_guest=True)
def badge_login(badge_code: str, pin: str):
    if not badge_code or not pin:
        frappe.throw(_("Badge code and PIN are required."))

    cache_key = f"{CACHE_PREFIX}{badge_code}"
    attempts = frappe.cache.get_value(cache_key) or 0
    if int(attempts) >= MAX_ATTEMPTS:
        frappe.throw(_("This badge is temporarily locked. Try again in a few minutes, or ask an admin to reset it."))

    badge_name = frappe.db.get_value(
        "Employee Badge", {"badge_code": badge_code, "disabled": 0}, ["name", "user"], as_dict=True
    )
    if not badge_name:
        frappe.throw(_("Unknown or disabled badge."))

    try:
        check_password(badge_name.name, pin, doctype="Employee Badge", fieldname="pin")
    except frappe.AuthenticationError:
        frappe.cache.set_value(cache_key, int(attempts) + 1, expires_in_sec=LOCKOUT_SECONDS)
        frappe.throw(_("Incorrect PIN."))

    # Correct PIN — clear the attempt counter and open a real session
    frappe.cache.delete_value(cache_key)
    frappe.local.login_manager.login_as(badge_name.user)

    return {"message": "ok", "redirect": "/app"}


@frappe.whitelist()
def set_employee_pin(badge_code: str, user: str, pin: str, employee: str | None = None):
    """Register or replace a badge's PIN. Restricted to System Manager —
    call this from the Desk (or bench console) when issuing/reissuing a
    physical card, never from the public kiosk page."""
    if "System Manager" not in frappe.get_roles():
        frappe.throw(_("Not permitted."), frappe.PermissionError)

    if not (pin.isdigit() and len(pin) == 4):
        frappe.throw(_("PIN must be exactly 4 digits."))

    existing = frappe.db.exists("Employee Badge", badge_code)
    if existing:
        frappe.db.set_value("Employee Badge", existing, {"user": user, "employee": employee, "disabled": 0})
        badge_name = existing
    else:
        doc = frappe.get_doc({
            "doctype": "Employee Badge",
            "badge_code": badge_code,
            "user": user,
            "employee": employee,
        })
        doc.insert(ignore_permissions=True)
        badge_name = doc.name

    set_encrypted_password("Employee Badge", badge_name, pin, fieldname="pin")
    frappe.db.commit()
    return {"message": "ok", "badge": badge_name}
