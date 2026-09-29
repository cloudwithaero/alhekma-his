# Al Hekma HIS — Project State

## Paths

- Backend: `/home/ozyr/frappe-bench/apps/alhekma`
- Frontend: `/home/ozyr/alhekma-frontend`
- Bench: `/home/ozyr/frappe-bench`
- Site: `alhekma.local`
- Backend URL: `http://alhekma.local:8000`
- Frontend URL: `http://alhekma.local:5173`

## Versions

- Frappe: 15.120.1
- ERPNext: 15.121.2
- Healthcare: 15.2.3
- Al Hekma: 0.0.1

## Git Baselines

### Backend

- Branch: `develop`
- `c5796cb` — `chore: establish Al Hekma backend baseline`
- `ace575b` — `feat: Initialize App`

### Frontend

- Branch: `main`
- `b81dd1b` — `chore: establish Al Hekma frontend baseline`

## Backend Structure

```text
alhekma/
├── api/
├── overrides/
├── setup/
├── patches/
├── tests/
├── public/
├── templates/
├── www/
└── archive/
Important Backend APIs
alhekma.api.badge_auth
alhekma.api.nursing
alhekma.api.healthcare_service_unit
Healthcare Service Unit Override

alhekma.overrides.healthcare_service_unit.AlHekmaHealthcareServiceUnit

Frontend Structure
alhekma-frontend/
├── src/
│   ├── components/
│   │   ├── nursing/
│   │   ├── layout/
│   │   └── ui/
│   ├── App.tsx
│   └── main.tsx
├── public/
├── archive/
└── vite.config.ts
Nursing Authentication Flow
Hospital Login
    ↓
kiosk_badge_login
    ↓
Validate Kiosk Device
    ↓
Validate Employee Badge
    ↓
Resolve Employee/User
    ↓
Create Staff Shift Presence
    ↓
Create Frappe Session
    ↓
/nursing
    ↓
NursingDashboard
    ├── get_current_staff_context
    └── get_dashboard

Current kiosk:

F1-KIOSK-TEST

get_dashboard() requires:

authenticated user
Nursing role
active Staff Shift Presence
Healthcare Service Units

Section 03 of the approved project specification is authoritative.

Important rules:

Department != Cost Center
Department != Healthcare Service Unit
Healthcare Service Unit != Warehouse/Asset Location
Designation != ERP Permission Role
External Laboratory is an external provider/supplier
Ambulance Vehicles are ERPNext Assets
CSSD is operational, not a patient-care location

Phase 1D contains 25 target HSU records plus the system root.

[D] units were intentionally not created.

Current special behavior:

Bed type: appointments disabled, inpatient occupancy enabled
Groups: both disabled
General Practitioner Clinic: appointments enabled
PACU: inpatient occupancy enabled
Triage, VIP rooms, ORs, CT, Ultrasound and Patient Dispensing Point: appointments disabled

Do not modify Frappe, ERPNext, or Healthcare core for these customizations.

HSU Tree

Custom API:

alhekma.api.healthcare_service_unit.get_root

Custom tree JS:

alhekma/public/js/healthcare_service_unit_tree.js

Live HSU names use the company abbreviation, for example:

Emergency Department - hikma

Commands

Start backend:

cd ~/frappe-bench
bench start

Run backend function:

bench --site alhekma.local execute <python.path.function>

Build backend app:

bench build --app alhekma

Run frontend:

cd ~/alhekma-frontend
npm run dev
Project Rules
Backend customization belongs in apps/alhekma.
Frontend lives in /home/ozyr/alhekma-frontend.
Do not modify Frappe/ERPNext/Healthcare core.
Do not delete archived files without an explicit decision.
Do not create [D] HSU units before required data is approved.
External providers must not be modeled as internal departments/service units.
Section 03 is the authority for the HSU tree.
Create a Git commit before major changes.
Handoff

Use this file together with the code repositories as the current project state.

Backend and frontend both have clean Git baselines.
