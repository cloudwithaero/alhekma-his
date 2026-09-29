# Al Hekma Hospital — Healthcare Service Unit controller override
# File: apps/alhekma/alhekma/overrides/healthcare_service_unit.py
#
# Registered in hooks.py via:
#   override_doctype_class = {
#       "Healthcare Service Unit": "alhekma.overrides.healthcare_service_unit.AlHekmaHealthcareServiceUnit"
#   }
#
# Design gap addressed
# --------------------
# The standard set_service_unit_properties() unconditionally copies
# allow_appointments from the linked Healthcare Service Unit Type onto every
# leaf node on every save.  This provides no per-unit override path.
#
# The Al Hekma blueprint requires allow_appointments=1 only for the
# General Practitioner Clinic.  All other leaf units (OR rooms, Radiology,
# VIP rooms, Dispensing Point, PACU) must have allow_appointments=0
# regardless of their Type's setting.
#
# Override scope
# --------------
# ONLY allow_appointments inheritance is overridden.
# inpatient_occupancy continues to be inherited exclusively from the Type.
# All group-node logic is identical to the standard implementation.
# All other methods (autoname, validate, on_update, on_trash, onload)
# are inherited unchanged from HealthcareServiceUnit.
#
# Usage in creation scripts
# -------------------------
# To preserve a per-unit allow_appointments value, set the flag before insert:
#
#   doc.allow_appointments = 1          # or 0
#   doc.flags.allow_appointments_override = True
#   doc.insert(ignore_permissions=True)
#
# Without the flag, behaviour is identical to the standard controller.

import frappe
from frappe import _
from frappe.utils import cint
from healthcare.healthcare.doctype.healthcare_service_unit.healthcare_service_unit import (
    HealthcareServiceUnit,
)


class AlHekmaHealthcareServiceUnit(HealthcareServiceUnit):
    """
    Al Hekma Hospital subclass of HealthcareServiceUnit.

    Only set_service_unit_properties() is overridden.  All other behaviour
    is inherited from the standard Healthcare app controller.
    """

    def set_service_unit_properties(self):
        if cint(self.is_group):
            # ── Group node: identical to standard behaviour ──────────────────
            # The standard implementation clears all leaf-only fields on group
            # nodes.  This block is reproduced verbatim and must stay in sync
            # with the upstream Healthcare app.
            self.allow_appointments = False
            self.overlap_appointments = False
            self.inpatient_occupancy = False
            self.service_unit_capacity = 0
            self.occupancy_status = ""
            self.service_unit_type = ""

        elif self.service_unit_type != "":
            # ── Leaf node ────────────────────────────────────────────────────
            service_unit_type = frappe.get_doc(
                "Healthcare Service Unit Type", self.service_unit_type
            )

            # Capture the intended per-unit allow_appointments value BEFORE
            # the Type value overwrites it.  The flag must be set on
            # doc.flags before insert/save for the override to take effect.
            intended_allow_appointments = cint(self.allow_appointments)
            override_active = bool(
                getattr(self.flags, "allow_appointments_override", False)
            )

            # ── inpatient_occupancy: always inherited from Type (no override) ─
            self.inpatient_occupancy = service_unit_type.inpatient_occupancy

            # ── allow_appointments: inherited from Type, then per-unit override
            self.allow_appointments = service_unit_type.allow_appointments
            if override_active:
                self.allow_appointments = intended_allow_appointments

            # ── Occupancy status (standard logic, unchanged) ─────────────────
            if self.inpatient_occupancy and self.occupancy_status != "":
                self.occupancy_status = "Vacant"

            # ── Overlap appointments (standard logic, unchanged) ─────────────
            if service_unit_type.overlap_appointments:
                self.overlap_appointments = True
            else:
                self.overlap_appointments = False
                self.service_unit_capacity = 0

        # ── Capacity guard (standard logic, unchanged) ───────────────────────
        if self.overlap_appointments:
            if not self.service_unit_capacity:
                frappe.throw(
                    _(
                        "Please set a valid Service Unit Capacity to enable"
                        " Overlapping Appointments"
                    ),
                    title=_("Mandatory"),
                )
