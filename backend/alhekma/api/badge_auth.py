import random
import requests

import frappe
from frappe import _
from frappe.utils.password import check_password, update_password

MAX_ATTEMPTS = 5
LOCKOUT_SECONDS = 900
CACHE_PREFIX = "alhekma_badge_login:"


@frappe.whitelist(allow_guest=True)
def badge_login(badge_code: str):
    """
    Authenticate a kiosk user using an Employee Badge code only.
    """

    if not badge_code:
        frappe.throw(_("Badge code is required."))

    badge_code = badge_code.strip()

    cache_key = f"{CACHE_PREFIX}{badge_code}"

    attempts = frappe.cache().get_value(cache_key) or 0
    attempts = int(attempts)

    if attempts >= MAX_ATTEMPTS:
        frappe.throw(
            _("Too many failed attempts. Please try again later.")
        )

    badge = frappe.db.get_value(
        "Employee Badge",
        {
            "badge_code": badge_code,
            "disabled": 0,
        },
        ["name", "user"],
        as_dict=True,
    )

    # Badge is invalid or disabled.
    # Count failed attempts because the badge itself is now
    # the only authentication factor.
    if not badge:
        attempts += 1

        frappe.cache().set_value(
            cache_key,
            attempts,
            expires_in_sec=LOCKOUT_SECONDS,
        )

        frappe.throw(_("Unknown or disabled badge."))

    if not badge.user:
        attempts += 1

        frappe.cache().set_value(
            cache_key,
            attempts,
            expires_in_sec=LOCKOUT_SECONDS,
        )

        frappe.throw(_("This badge is not linked to a user."))

    # Successful authentication.
    frappe.cache().delete_value(cache_key)

    frappe.local.login_manager = frappe.auth.LoginManager()
    frappe.local.login_manager.user = badge.user
    frappe.local.login_manager.post_login()

    return {
        "message": "ok",
        "redirect": "/app",
        "user": badge.user,
    }
    """
    Authenticate a kiosk user using:
    1. Employee Badge code
    2. 4-digit PIN
    """

    if not badge_code:
        frappe.throw(_("Badge code is required."))

    if not pin:
        frappe.throw(_("PIN is required."))

    badge_code = badge_code.strip()

    cache_key = f"{CACHE_PREFIX}{badge_code}"

    attempts = frappe.cache().get_value(cache_key) or 0
    attempts = int(attempts)

    if attempts >= MAX_ATTEMPTS:
        frappe.throw(
            _("Too many failed attempts. Please try again later.")
        )

    badge = frappe.db.get_value(
        "Employee Badge",
        {
            "badge_code": badge_code,
            "disabled": 0,
        },
        ["name", "user"],
        as_dict=True,
    )

    if not badge:
        frappe.throw(_("Unknown or disabled badge."))

    if not badge.user:
        frappe.throw(_("This badge is not linked to a user."))

    try:
        check_password(
            badge.name,
            pin,
            doctype="Employee Badge",
            fieldname="pin",
        )
    except frappe.AuthenticationError:
        attempts += 1

        frappe.cache().set_value(
            cache_key,
            attempts,
            expires_in_sec=LOCKOUT_SECONDS,
        )

        frappe.throw(_("Incorrect PIN."))

    frappe.cache().delete_value(cache_key)

    frappe.local.login_manager = frappe.auth.LoginManager()

    frappe.local.login_manager.user = badge.user
    frappe.local.login_manager.post_login()

    return {
        "message": "ok",
        "redirect": "/app",
        "user": badge.user,
    }


@frappe.whitelist()
def set_employee_pin(
    badge_code: str,
    user: str,
    pin: str,
    employee: str | None = None,
):
    """
    Register or replace a badge's PIN.

    Restricted to System Manager.
    """

    if "System Manager" not in frappe.get_roles():
        frappe.throw(
            _("Not permitted."),
            frappe.PermissionError,
        )

    if not badge_code:
        frappe.throw(_("Badge code is required."))

    if not user:
        frappe.throw(_("User is required."))

    if not (pin.isdigit() and len(pin) == 4):
        frappe.throw(
            _("PIN must be exactly 4 digits.")
        )

    existing = frappe.db.exists(
        "Employee Badge",
        badge_code,
    )

    if existing:
        frappe.db.set_value(
            "Employee Badge",
            existing,
            {
                "user": user,
                "employee": employee,
                "disabled": 0,
            },
        )

        badge_name = existing

    else:
        doc = frappe.get_doc(
            {
                "doctype": "Employee Badge",
                "badge_code": badge_code,
                "user": user,
                "employee": employee,
                "disabled": 0,
            }
        )

        doc.insert(ignore_permissions=True)

        badge_name = doc.name

    update_password(
        badge_name,
        pin,
        doctype="Employee Badge",
        fieldname="pin",
    )

    frappe.db.commit()

    return {
        "message": "ok",
        "badge": badge_name,
    }


@frappe.whitelist(allow_guest=True)
def verify_badge(badge_code: str):
    """
    Check whether an active Employee Badge exists.
    Returns only whether it exists.
    """

    if not badge_code:
        return {
            "exists": False,
        }

    badge_code = badge_code.strip()

    exists = frappe.db.exists(
        "Employee Badge",
        {
            "badge_code": badge_code,
            "disabled": 0,
        },
    )

    return {
        "exists": bool(exists),
    }


@frappe.whitelist(allow_guest=True)
def get_csrf_token():
    return {
        "csrf_token": frappe.sessions.get_csrf_token()
    }


@frappe.whitelist(allow_guest=True)
def medical_quote():
    """
    Fetch a short healthcare-relevant quote from the public Quotable API.

    The external call is non-critical: the login page works even if the
    public quote service is unavailable. The endpoint returns only quote
    text, author, and a simple source label; no hospital or patient data
    is sent to the external service.
    """

    # These search terms keep the result set oriented toward healthcare.
    search_terms = [
        "doctor",
        "patient",
        "medicine",
        "health",
        "nurse",
        "care",
    ]

    # Rotate the query without relying on browser-side randomness.
    index = (frappe.utils.now_datetime().minute // 2) % len(search_terms)
    query = search_terms[index]

    try:
        response = requests.get(
            "https://api.quotable.io/search/quotes",
            params={
                "query": query,
                "limit": 10,
            },
            timeout=3,
        )

        response.raise_for_status()
        payload = response.json()

        results = payload.get("results") or []

        # Prefer results that contain healthcare-related terms in content/tags.
        keywords = {
            "doctor",
            "patient",
            "medicine",
            "medical",
            "health",
            "nurse",
            "care",
            "hospital",
            "healing",
            "wellness",
            "surgery",
            "clinical",
        }

        def score(item):
            content = str(item.get("content") or "").lower()
            tags = " ".join(
                str(tag) for tag in (item.get("tags") or [])
            ).lower()

            haystack = f"{content} {tags}"

            return sum(
                1
                for keyword in keywords
                if keyword in haystack
            )

        ranked = sorted(
            results,
            key=score,
            reverse=True,
        )

        candidates = [
            item
            for item in ranked
            if str(item.get("content") or "").strip()
        ]

        if candidates:
            # Pick from the strongest few so every page open can change it.
            top = candidates[: min(5, len(candidates))]
            chosen = random.choice(top)

            return {
                "quote": str(chosen.get("content")).strip(),
                "author": str(
                    chosen.get("author") or "Unknown"
                ).strip(),
                "source": "Quotable",
            }

    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            "Al Hekma medical quote API failed",
        )

    # Hospital-safe fallback if Internet/public API is unavailable.
    fallback = [
        {
            "quote": "Caring for patients starts with caring about the details.",
            "author": "Al Hekma Staff Reminder",
            "source": "Local fallback",
        },
        {
            "quote": "Good teamwork turns individual expertise into safer patient care.",
            "author": "Al Hekma Staff Reminder",
            "source": "Local fallback",
        },
        {
            "quote": "Every careful action at the bedside can make a meaningful difference.",
            "author": "Al Hekma Staff Reminder",
            "source": "Local fallback",
        },
        {
            "quote": "Clear communication is part of safe, compassionate care.",
            "author": "Al Hekma Staff Reminder",
            "source": "Local fallback",
        },
    ]

    return random.choice(fallback)
@frappe.whitelist(allow_guest=True)
def arabic_quote():
    """
    Return a short Arabic quote for the staff kiosk.

    The external service receives no hospital, employee, badge,
    PIN, patient, or other application data.
    """

    fallback_quotes = [
        {
            "text": "سلامة المريض تبدأ من دقة كل خطوة يقوم بها الفريق.",
            "source": "تذكير للطاقم الطبي",
        },
        {
            "text": "الاهتمام بالتفاصيل الصغيرة يصنع فرقًا كبيرًا في جودة الرعاية.",
            "source": "تذكير للطاقم الطبي",
        },
        {
            "text": "التواصل الواضح بين أفراد الفريق جزء أساسي من الرعاية الآمنة.",
            "source": "تذكير للطاقم الطبي",
        },
        {
            "text": "كل مريض يحتاج إلى علمٍ دقيق، وقلبٍ حاضر، واحترامٍ كامل.",
            "source": "تذكير للطاقم الطبي",
        },
    ]

    try:
        response = requests.get(
            "https://quotes.assayyaad.pro/api",
            params={
                "lang": "ar",
                "cat": "quotes",
            },
            timeout=4,
        )

        response.raise_for_status()

        payload = response.json()

        if not isinstance(payload, list):
            raise ValueError("Unexpected quote API response")

        quotes = []

        medical_keywords = (
            "طب",
            "طبي",
            "طبيب",
            "مريض",
            "مرضى",
            "صحة",
            "علاج",
            "شفاء",
            "رعاية",
            "تمريض",
            "مستشفى",
            "دواء",
            "جراحة",
            "ألم",
        )

        for item in payload:
            if not isinstance(item, dict):
                continue

            text = str(item.get("text") or "").strip()
            source = str(item.get("source") or "").strip()

            if not text:
                continue

            score = sum(
                1
                for keyword in medical_keywords
                if keyword in text
            )

            quotes.append(
                {
                    "text": text,
                    "source": source or "اقتباس عربي",
                    "score": score,
                }
            )

        if quotes:
            medical_quotes = [
                quote
                for quote in quotes
                if quote["score"] > 0
            ]

            candidates = medical_quotes or quotes

            # Prefer a random quote from the healthcare-relevant subset.
            chosen = random.choice(candidates)

            return {
                "text": chosen["text"],
                "source": chosen["source"],
            }

    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            "Al Hekma Arabic quote API failed",
        )

    return random.choice(fallback_quotes)
@frappe.whitelist(allow_guest=True)
def kiosk_badge_login(badge_code: str, kiosk_device: str):
    """
    TEST/Development:
    Authenticate a badge from a fixed kiosk and create an active
    Staff Shift Presence tied to the kiosk location.
    """

    if not badge_code:
        frappe.throw(_("Badge code is required."))

    if not kiosk_device:
        frappe.throw(_("Kiosk device is required."))

    badge_code = badge_code.strip()
    kiosk_device = kiosk_device.strip()

    # ---------------------------------------------------------
    # Validate kiosk
    # ---------------------------------------------------------

    kiosk = frappe.db.get_value(
        "Kiosk Device",
        {
            "device_id": kiosk_device,
            "enabled": 1,
        },
        [
            "name",
            "device_id",
            "healthcare_service_unit",
        ],
        as_dict=True,
    )

    if not kiosk:
        frappe.throw(_("Unknown or disabled kiosk device."))

    if not kiosk.healthcare_service_unit:
        frappe.throw(_("This kiosk has no Healthcare Service Unit assigned."))

    # ---------------------------------------------------------
    # Validate badge
    # ---------------------------------------------------------

    badge = frappe.db.get_value(
        "Employee Badge",
        {
            "badge_code": badge_code,
            "disabled": 0,
        },
        [
            "name",
            "user",
            "employee",
        ],
        as_dict=True,
    )

    if not badge:
        frappe.throw(_("Unknown or disabled badge."))

    if not badge.user:
        frappe.throw(_("This badge is not linked to a user."))

    # ---------------------------------------------------------
    # Get employee
    # ---------------------------------------------------------

    employee = badge.employee

    if not employee:
        employee = frappe.db.get_value(
            "Employee",
            {
                "user_id": badge.user,
                "status": "Active",
            },
            "name",
        )

    if not employee:
        frappe.throw(_("No active employee is linked to this user."))

    # ---------------------------------------------------------
    # Check for existing active presence
    # ---------------------------------------------------------

    active_presence = frappe.db.get_value(
        "Staff Shift Presence",
        {
            "user": badge.user,
            "status": "Active",
        },
        [
            "name",
            "kiosk_device",
            "healthcare_service_unit",
            "started_at",
        ],
        as_dict=True,
    )

    if active_presence:
        if active_presence.kiosk_device == kiosk.name:
            # Already active on this same kiosk.
            presence_name = active_presence.name
        else:
            frappe.throw(
                _(
                    "This employee already has an active shift presence "
                    "on another kiosk."
                )
            )
    else:
        # -----------------------------------------------------
        # Create new presence
        # -----------------------------------------------------

        presence = frappe.get_doc(
            {
                "doctype": "Staff Shift Presence",
                "employee": employee,
                "user": badge.user,
                "kiosk_device": kiosk.name,
                "healthcare_service_unit": kiosk.healthcare_service_unit,
                "started_at": frappe.utils.now_datetime(),
                "status": "Active",
            }
        )

        presence.insert(ignore_permissions=True)
        frappe.db.commit()

        presence_name = presence.name

    # ---------------------------------------------------------
    # Create Frappe login session
    # ---------------------------------------------------------

    frappe.local.login_manager = frappe.auth.LoginManager()
    frappe.local.login_manager.user = badge.user
    frappe.local.login_manager.post_login()

    return {
        "message": "ok",
        "user": badge.user,
        "employee": employee,
        "kiosk_device": kiosk.name,
        "healthcare_service_unit": kiosk.healthcare_service_unit,
        "presence": presence_name,
        "home_page": "/app/home",
    }
@frappe.whitelist()
def get_current_staff_context():
    """
    Return the currently authenticated staff user's
    role, employee, active kiosk and current healthcare unit.
    """

    user = frappe.session.user

    if not user or user == "Guest":
        frappe.throw(_("Authentication required."), frappe.PermissionError)

    roles = frappe.get_roles(user)

    employee = frappe.db.get_value(
        "Employee",
        {"user_id": user},
        [
            "name",
            "employee_name",
            "designation",
            "department",
        ],
        as_dict=True,
    )

    active_presence = frappe.db.get_value(
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

    if not employee:
        frappe.throw(
            _("No active Employee record is linked to this user.")
        )

    if not active_presence:
        frappe.throw(
            _("No active staff shift presence was found.")
        )

    kiosk = frappe.db.get_value(
        "Kiosk Device",
        active_presence.kiosk_device,
        [
            "device_id",
            "device_name",
            "healthcare_service_unit",
        ],
        as_dict=True,
    )

    return {
        "user": user,
        "full_name": employee.employee_name,
        "employee": employee.name,
        "designation": employee.designation,
        "department": employee.department,
        "roles": roles,
        "presence": {
            "name": active_presence.name,
            "kiosk_device": kiosk.device_id if kiosk else None,
            "kiosk_name": kiosk.device_name if kiosk else None,
            "healthcare_service_unit": active_presence.healthcare_service_unit,
            "started_at": active_presence.started_at,
            "status": "Active",
        },
    }
