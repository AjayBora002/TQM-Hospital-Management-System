# 🏥 Comprehensive Modern HMS Platform Upgrade Plan
**Quality Goal: Q07 (Improve Data Accuracy) · NABH 6th Edition & ABDM Compliant Architecture**

---

## 1. Complete Module List (Grouped by Hospital Domain)

The modern HMS organizes hospital capabilities into 11 coherent domain groups in a fixed, collapsible sidebar:

| # | Domain Group | Modules Included | Primary User Roles |
|---|---|---|---|
| **1** | **Front Office** | Patient Master (UHID/ABHA/Photo), Appointments (Slot Engine), OPD Queue & Tokens, Visitor Management, Patient Portal | Receptionist, Patient, Admin |
| **2** | **Clinical Care** | Triage Station, EMR / Encounters (SOAP Notes & Timeline), e-Prescription (Allergy/Dose Poka-Yoke), Clinical Orders (STAT/Urgent/Routine), Emergency / Casualty Trauma Board, ICU Multi-parameter Monitoring Chart, Operation Theatre (OT Scheduling & Checklists), Radiology Orders & Reports, Dialysis / Daycare | Doctor, Nurse, OT Manager, Radiologist, Dietitian |
| **3** | **Diagnostics (LIS & Blood)** | Laboratory Information System (Order → Billing Gate → Sample Collection → Processing → Verification → Release with TAT), Blood Bank (Donors, Inventory, Cross-match, Expiry) | Lab Technician, Blood Bank Tech, Doctor |
| **4** | **Inpatient (IPD)** | Admissions & Stays, Ward Bed Board Matrix (Available/Occupied/Cleaning/Maintenance), Bed Transfers, Nursing Station & MAR (Medication Administration Record), Shift Handover Protocol, Clinical Discharge Summaries | Ward Manager, Nurse, Doctor, Housekeeping |
| **5** | **Pharmacy & Supply** | Prescription Dispensing Desk, Medicine Inventory (Batch & Expiry alerts), Purchase Orders, Vendor Directory, General Store & Central Consumables Issue to Wards | Pharmacist, Store Manager, Cashier |
| **6** | **Finance & Billing** | Itemized Invoicing (OPD/IPD/Lab/Pharmacy), Advance Deposits, Payments & Refund Approval, Insurance / TPA Desk (Pre-auth → Claim → Settlement), Package Pricing, GST Invoice & Print | Cashier, Insurance Desk, Hospital Manager |
| **7** | **Support Services** | Housekeeping (Auto-triggered Bed Cleaning on Discharge), Laundry Tracking, Diet & Kitchen Orders by Ward, Ambulance Fleet Dispatch & Trips, Biomedical Equipment (Asset Register, Maintenance & Calibration), Facility Maintenance Tickets | Housekeeping Sup, Dietitian, Ambulance Dispatcher, Biomedical Eng |
| **8** | **Human Resources** | Staff Directory & Credentials, Duty Roster & Shift Scheduling, Attendance Tracking, Staff Leave Requests, Licence Expiry Alerter | HR Manager, Hospital Manager |
| **9** | **Quality & Governance** | KPI Executive Dashboard (Wait Times, Lab TAT, Bed Occupancy, ALOS, Readmissions), Incident Reporting, RCA & CAPA Tracker, Quality Audits (NABH/ISO), Infection Control Log, SPC Control Charts | Quality Manager, Hospital Manager, Admin |
| **10** | **Administration** | User & Role Management, Visual RBAC Matrix Editor, Audit Trail Explorer with CSV Export, Automated Database Backup & Restore, System Config & Notification Templates | Admin |
| **11** | **Cross-Cutting Utilities** | Real-time Role Notification Centre, Global Omnisearch (`/` key, UHID/Name/Phone), Clinical Print Views, Simulated ABDM Gateway (ABHA Verification & Consent Stub) | All Authenticated Users |

---

## 2. Role × Module Permission Matrix Table (All 21 Roles)

Permissions: **V** (View/Read), **C** (Create), **E** (Edit/Update), **D** (Delete/Cancel), **A** (Approve/Verify/Release).

| # | Role Identity | Front Office | Clinical Care | Diagnostics | Inpatient (IPD) | Pharmacy & Supply | Finance & Billing | Support Services | People (HR) | Quality & Governance | Admin Console |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **1** | **System Admin** | V, C, E | V *(non-clinical)* | V *(non-clinical)* | V, E | V, C, E | V | V, E | V, C, E, D | V | **V, C, E, D, A** |
| **2** | **Hospital Manager** | V | V | V | V | V | V, A | V | V, A | **V, C, E, A** | V |
| **3** | **Receptionist** | **V, C, E** | — *(Blocked)* | — *(Blocked)* | V, C | — | V, C | V | — | — | — |
| **4** | **Doctor** | V | **V, C, E, A** | V, C | V, C, E | V, C | — *(Blocked)* | V, C *(Diet)* | V | V | — |
| **5** | **Nurse** | V | V, C, E | V | **V, C, E, A** | V | — *(Blocked)* | V, C *(Housekeeping)* | V | V, C *(Incident)* | — |
| **6** | **Ward Manager** | V | V | V | **V, C, E, A** | V | — | V, C, E | V | V | — |
| **7** | **Lab Technician** | — | V *(Lab orders)* | **V, C, E, A** | — | — | — | — | — | V | — |
| **8** | **Pharmacist** | — | V *(Rx only)* | — | — | **V, C, E, A** | V | — | — | V | — |
| **9** | **Cashier** | V | — *(Blocked)* | — *(Blocked)* | V | V *(Billing)* | **V, C, E, A** | — | — | — | — |
| **10** | **Patient** | V, C *(Own)* | V *(Own reports)* | V *(Own reports)* | V *(Own stay)* | V *(Own Rx)* | V *(Own bills)* | — | — | V, C *(Feedback)* | — |
| **11** | **Quality Manager** | V | V | V | V | V | V | V | V | **V, C, E, A** | V *(Audit only)* |
| **12** | **Radiologist / Tech** | — | V *(Rad orders)* | **V, C, E, A** | — | — | — | — | — | V | — |
| **13** | **OT Manager** | — | **V, C, E, A** | V | V | V | — | V | V | V | — |
| **14** | **Blood Bank Tech** | — | V *(Requests)* | **V, C, E, A** | — | — | — | — | — | V | — |
| **15** | **Housekeeping Supervisor** | — | — | — | V | — | — | **V, C, E, A** | V | V | — |
| **16** | **Biomedical Engineer** | — | V *(Equip status)* | V | V | — | — | **V, C, E, A** | V | V | — |
| **17** | **HR Manager** | — | — | — | — | — | — | — | **V, C, E, D, A** | V | — |
| **18** | **Store / Inventory Manager**| — | — | — | — | **V, C, E, A** | V | V | V | V | — |
| **19** | **Insurance / TPA Desk** | V | — *(Blocked)* | — *(Blocked)* | V | — | **V, C, E, A** | — | — | V | — |
| **20** | **Ambulance Dispatcher** | V *(Emergency)* | V *(Casualty)* | — | — | — | — | **V, C, E, A** | V | V | — |
| **21** | **Dietitian** | — | V *(Nutrition)* | — | V | — | — | **V, C, E, A** | V | V | — |

---

## 3. New Database Tables (100% Backward-Compatible)

Existing tables (`patients`, `doctors`, `appointments`, `rooms`, `staff`, `medicines`, `bills`, `audit_log`, `defect_log`, `vitals_log`, `users`, `admissions`, `prescriptions`, `lab_tests`, `purchase_orders`, `quality_audits`, `departments`, `doctor_profiles`, `wards`, `nurse_profiles`, `opd_queue`, `clinical_orders`, `doctor_nurse_messages`, `shift_handovers`, `encounters`) are strictly preserved.

### New Tables:
1. `visitor_logs` — Visitor badge pass, visitor name, patient link, entry/exit timestamp.
2. `emergency_cases` — ER triage board, arrival mode, severity (Red/Yellow/Green), trauma vitals, attending doc.
3. `icu_monitoring_logs` — Ventilator mode, GCS score, arterial line BP, inotropes, urine output.
4. `ot_schedules` — Surgery booking, OT theater #, lead surgeon, anaesthetist, WHO surgical checklist stage.
5. `radiology_orders` — Modality (X-Ray/CT/MRI/USG), order status, DICOM accession #, findings, radiologist verification.
6. `blood_donors` & `blood_inventory` — Donor demographics, blood group, screening status, bag units, expiry date.
7. `blood_requests` — Patient cross-match requests, compatibility confirmation, issue log.
8. `nursing_mar` — Medication Administration Record (schedule time, given time, nurse digital signature, dosage check).
9. `bed_transfers` — Patient room/bed movement audit with reason, source room, target room, approval.
10. `inventory_items` & `inventory_transactions` — Consumables, surgical supplies, batch, reorder levels, ward issues.
11. `insurance_claims` — Provider, policy number, pre-authorization amount, claim status, settlement date.
12. `advance_deposits` — Inpatient admissions advance payment deposit, refund receipts, cashier approval.
13. `housekeeping_tasks` — Auto-created cleaning jobs on patient discharge, room status turnaround tracker.
14. `diet_orders` — Dietary plans (Diabetic, Renal, Soft, Normal, NPO), kitchen preparation and ward delivery.
15. `ambulance_trips` — Vehicle registration, driver, pickup location, caller phone, trip status, patient link.
16. `biomedical_equipment` — Equipment serial, department, calibration due date, breakdown alerts, preventive maintenance.
17. `facility_tickets` — Infrastructure maintenance issues (plumbing, electrical, AC, medical gas), status.
18. `staff_shifts` & `staff_leaves` — Duty roster scheduling by department/ward, leave approval workflow.
19. `quality_incidents` & `capa_actions` — Sentinel events, medication near-misses, 5-Why root cause analysis, corrective actions.
20. `notifications` — In-app alerts targeted by user/role (`unread`, `timestamp`, `link`).

---

## 4. Route & File Architecture

### Backend:
```text
src/
├── auth/
│   ├── __init__.py
│   ├── permissions.py         # 21 Roles permission registry + @require_permission decorator
│   ├── session_guard.py       # Session idle timeout (15m), failed attempts lock
│   └── password_hasher.py     # Werkzeug generate/check_password_hash with SHA-256 fallback
├── services/                  # Business logic & state-machine guards
│   ├── appointment_service.py # Schedule conflict & slot derivation
│   ├── clinical_service.py    # EMR & allergy contraindication checks
│   ├── admission_service.py   # Inpatient bed allocation & discharge gate
│   ├── lab_service.py         # LIS state machine (Unpaid -> Collected -> Verified -> Released)
│   ├── billing_service.py     # Multi-line item bill calculation & financial lock
│   └── quality_service.py     # KPI calculation from operational timestamps
├── api/                       # Flask Blueprints (enforced with @require_permission)
│   ├── auth.py                # Login, Logout, /me, change-password, session status
│   ├── front_office.py        # Patients, Appointments, OPD Queue, Visitors
│   ├── clinical.py            # Encounters, Orders, ER, ICU, OT, Radiology
│   ├── diagnostics.py         # LIS, TAT tracking, Blood Bank
│   ├── inpatient.py           # Admissions, Bed Board, MAR, Handovers
│   ├── pharmacy_supply.py     # Dispensing, Inventory, POs
│   ├── finance.py             # Billing, Deposits, Insurance/TPA Claims
│   ├── support.py             # Housekeeping, Diet, Ambulance, Biomedical
│   ├── people.py              # Staff Roster, Leaves, Credentials
│   └── quality.py             # KPIs, Incidents, CAPA, SPC, NABH
```

### Frontend:
```text
src/
├── templates/
│   ├── index.html             # Clean modern app shell with sidebar & header
│   └── login.html             # Standalone modern clinical authentication screen
└── static/
    ├── css/
    │   ├── tokens.css         # Clinical SaaS design tokens (colors, elevation, 8px grid)
    │   ├── layout.css         # Collapsible sidebar, persistent patient banner, topbar
    │   ├── components.css     # Data tables, drawers, status badges, buttons, modals
    │   └── print.css          # Printable formats (Prescription, Discharge, Bill, Lab report)
    └── js/
        ├── core/
        │   ├── api.js         # Fetch wrapper with auto 401/403 handlers & CSRF/Session check
        │   ├── router.js      # Client-side hash router with permission gate
        │   ├── auth.js        # Current session state, timeout warnings, logout
        │   └── ui.js          # Drawers, modals, toasts, skeleton loaders, patient banner
        └── modules/
            ├── front_office.js
            ├── clinical.js
            ├── diagnostics.js
            ├── inpatient.js
            ├── pharmacy.js
            ├── finance.js
            ├── support.js
            ├── people.js
            ├── quality.js
            └── admin.js
```

---

## 5. Implementation Phases

1. **Phase A — Auth & Server-Side RBAC**:
   - `src/auth/permissions.py` (21 roles × module actions map).
   - `@require_permission(module, action)` decorator with audit logging of 403s.
   - User session guard with 15-minute idle timeout and failed attempt lockout.
   - Dedicated modern login page + `/api/auth/me` endpoint.
   - Remove admin fallback.

2. **Phase B — UI/UX Redesign & Role Homes**:
   - Modern healthcare SaaS design system: Collapsible sidebar, top header with global search & notification bell, persistent patient context banner.
   - Role-tailored landing screens upon login.
   - Modularized ES JS frontend with hash-routing (`#/clinical/emr`, `#/inpatient/bed-board`).

3. **Phase C — Depth-First OPD & IPD Journeys**:
   - **OPD Journey**: Appointment → Check-in → Token Queue → Doctor Consultation (SOAP) → Prescription & Lab Order → Billing → Discharge/Follow-up.
   - **IPD Journey**: Admission → Bed Allocation → MAR & Nursing Orders → Daily Rounds → Discharge Clearance → Bed Turnover (Housekeeping).
   - Strict state-machine gates (no unpaid lab processing, no double-booked beds).

4. **Phase D — Comprehensive Modules**:
   - Front Office (Visitors), Clinical (ER Trauma, ICU, OT, Radiology), Diagnostics (LIS + Blood Bank), Pharmacy (Store/Consumables), Support Services (Diet, Ambulance, Biomedical, Maintenance), People (Roster/Leave), Quality (KPIs, Incidents, CAPA).

5. **Phase E — Reports, Printing, Testing & Documentation**:
   - Print templates for Prescriptions, GST Bills, Discharge Summaries, and Lab Reports.
   - Automated RBAC unit tests (verifying 403 on unauthorized routes and 200 on authorized routes for every role).
   - All 172 existing tests continue to pass.
   - Update `README.md`, `docs/USER_MANUAL.md`, and generate `docs/RBAC_MATRIX.md`.

