# Al Hekma Hospital — Register a few TEST badges to try the kiosk flow
#
# Creates 3 demo badges (clearly TEST codes, not real card data) linked
# to the existing test logins, so you can try /kiosk end-to-end before
# ordering real printed cards.
#
# Run with:
#   bench --site alhekma.local execute alhekma.patches.register_test_badges.run

import frappe

# (badge_code, user, pin)
BADGES = [
    ("TESTBADGE-DOCTOR-01", "test-027@alhekma.local", "1234"),
    ("TESTBADGE-NURSE-01", "test-029@alhekma.local", "1234"),
    ("TESTBADGE-PHARMACY-01", "test-035@alhekma.local", "1234"),
]


def run():
    if not frappe.db.exists("DocType", "Employee Badge"):
        frappe.throw("Run create_employee_badge_doctype.py first.")

    from alhekma.api import set_employee_pin

    for badge_code, user, pin in BADGES:
        set_employee_pin(badge_code=badge_code, user=user, pin=pin)
        print(f"Badge ready: {badge_code} -> {user} (PIN: {pin})")

    print(
        "\nOpen http://alhekma.local:8000/kiosk on the device.\n"
        "Since there's no physical scanner yet, just type one of the "
        "codes above into the page and press Enter manually (simulates "
        "a scan), then tap the PIN on screen."
    )
