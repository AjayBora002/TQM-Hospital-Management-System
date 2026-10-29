# Hospital Management System (HMS) — Comprehensive User & Operations Manual

**Course:** BBAT104 — Fundamentals of Total Quality Management  
**Academic Session:** 2026–27  
**Student:** Ajay Bora (Roll No: 2410302008 — Branch: CSE — Section B)  
**Assigned Quality Goal:** Q07 — Improve Data Accuracy  
**Repository Identifier:** `BBAT104_TQM_2410302008` (GitHub: `TQM-Hospital-Management-System`)  
**Platform Version:** Modern Enterprise Clinical Edition (21 Roles, 11 Domains, Zero-Trust Server-Side RBAC)

---

## 1. System Overview & Architecture

The Hospital Management System is an enterprise-grade clinical and administrative software platform designed in compliance with **NABH Hospital Standards**, **ABDM (Ayushman Bharat Digital Mission)** digital health guidelines, and **Total Quality Management (TQM)** principles under **Quality Goal Q07 (Improve Data Accuracy)**.

### Architectural Highlights:
- **Zero-Trust Server-Side RBAC**: Every REST API route is protected by the `@require_permission(module, action)` decorator in `src/auth/permissions.py`. Unauthorized calls return `401 Unauthorized` or `403 Forbidden` and write to the immutable security audit trail.
- **Enterprise Authentication**: Werkzeug PBKDF2-HMAC password hashing, secure session management, **15-minute idle timeout** with 2-minute proactive warning, and **5-attempt account lockout** protection.
- **Modular Frontend Architecture**: Collapsible sidebar navigation with 11 domain groupings and SVG icons, sticky persistent patient context banner, topbar with breadcrumbs, branch selector, and instant global search (`/` keyboard shortcut).
- **Dedicated Print Views**: Clean `@media print` layouts for Prescriptions, Lab Reports, Discharge Summaries, and Invoices.
- **21 Stakeholder Roles**: Complete separation of duty across administrative, medical, nursing, diagnostic, allied healthcare, and patient roles.
- **Automated Verification**: Comprehensive test suite with 176 automated tests passing in under 5 seconds.

---

## 2. Launching the Application

### 2.1 Web Platform (Modern Clinical SaaS)
Launch the web interface locally:
```bash
python run.py --web
```
Access the application in any modern browser:
- **URL**: `http://127.0.0.1:5000` (or `http://127.0.0.1:5000/login`)
- When unauthenticated, the application automatically redirects to the clinical sign-in page.

### 2.2 Native Desktop GUI (Tkinter)
Launch the legacy Tkinter desktop interface:
```bash
python run.py
```

### 2.3 Executing the Automated Quality Test Suite
Execute all 176 unit and integration tests:
```bash
python -m unittest discover tests
```

---

## 3. Authentication & Account Security

### 3.1 Sign In Procedure
1. Navigate to `http://127.0.0.1:5000/login`.
2. Enter your authorized username and password.
3. In demonstration mode (`HMS_DEMO=1`), click any persona card in the **Demo Accounts Panel** on the right side of the screen to automatically prefill standard credentials.
4. Click **Sign In to System**. Upon successful verification, you are routed directly to the dashboard tailored to your role.

### 3.2 Demo Accounts (21 Personas)
All demo accounts are pre-seeded in SQLite with default credentials:
- **Admin**: `admin` / `admin123`
- **Hospital Manager**: `manager` / `mgr123`
- **Doctor (Lead Cardiologist)**: `doctor` / `doc123`
- **Nurse (Cardiac Ward)**: `nurse` / `nurse123`
- **Ward Manager**: `ward_mgr` / `ward123`
- **Receptionist**: `receptionist` / `rec123`
- **Lab Technician**: `labtech` / `lab123`
- **Pharmacist**: `pharmacist` / `pharm123`
- **Cashier**: `cashier` / `cash123`
- **Patient**: `patient` / `pat123`
- **Quality Manager**: `quality_mgr` / `qual123`
- **Radiologist**: `radiologist` / `rad123`
- **OT Manager**: `ot_mgr` / `ot123`
- **Blood Bank Tech**: `bloodbank_tech` / `bb123`
- **Housekeeping Supervisor**: `housekeeper` / `hk123`
- **Biomedical Engineer**: `biomed_eng` / `bio123`
- **HR Manager**: `hr_mgr` / `hr123`
- **Store Manager**: `store_mgr` / `store123`
- **Insurance / TPA Desk**: `insurance_desk` / `ins123`
- **Ambulance Dispatcher**: `ambulance_disp` / `amb123`
- **Dietitian**: `dietitian` / `diet123`

### 3.3 Session Idle Timeout Policy
- The system enforces a strict **15-minute inactivity timeout**.
- If no mouse, keyboard, or touch events occur for **13 minutes**, a prominent toast alert notifies the user:
  `⚠️ Idle Session Warning: Inactivity timeout in 2 minutes. Any unsaved data will be secured.`
- At 15 minutes, the session is invalidated server-side, and the browser redirects to `/login`.

### 3.4 Brute-Force Lockout
- After 5 consecutive failed login attempts for any account, that account is automatically locked for **15 minutes**.
- All lockout events are recorded in `login_attempts` with client IP and timestamps.

### 3.5 Changing Password
1. Click the profile avatar in the top-right corner of the topbar.
2. Select **Change Password** from the dropdown menu.
3. Enter your current password and your new password (minimum 6 characters).
4. Click **Update Password**.

---

## 4. Navigation & Workspace Controls

### 4.1 Collapsible Sidebar
- Click the hamburger toggle button in the sidebar header to collapse the sidebar into icon-only mode.
- Hovering over any icon in collapsed mode surfaces an instant tooltip.
- Navigation items are organized into 11 distinct clinical and administrative domains:
  1. **Dashboard**
  2. **Front Office**
  3. **Clinical Care**
  4. **Diagnostics**
  5. **Inpatient (IPD)**
  6. **Pharmacy & Supply**
  7. **Finance & TPA**
  8. **Support Services**
  9. **People & HR**
  10. **Quality & TQM**
  11. **Administration**
  12. **Patient Portal**

### 4.2 Top Bar Features
- **Hospital Branch Selector**: Multi-facility selector for Apex Central Hospital (Main Campus) and City Care Clinic.
- **Global Search Button**: Clicking or pressing the `/` key anywhere in the application opens the global patient search dialog.
- **Notification Bell**: Live system alert counter for critical clinical orders and turnaround time warnings.
- **User Profile Menu**: Displays user initials avatar, full name, role badge, session status, password management, and one-click Sign Out.

### 4.3 Persistent Patient Context Banner
Whenever a patient is selected from a table, appointment queue, bed board, or search result, the **Patient Context Banner** docks immediately below the topbar:
- Displays: UHID (e.g., `UHID-2026-0001`), Full Name, Age / Gender, Blood Group, Location (e.g., `Bed 101` or `Outpatient`), and Allergies (red warning pill if documented).
- **Quick Action Buttons**:
  - `+ SOAP Note`: Instantly opens clinical consultation encounter.
  - `💊 Prescribe`: Navigates to e-Prescription with patient pre-selected.
  - `🧪 Order Lab`: Navigates to LIS orders with patient pre-selected.
  - `🛏️ Admit`: Navigates to Inpatient Admissions with patient pre-selected.
  - `💳 Bill`: Navigates to Invoices with patient pre-selected.
  - `360° EMR`: Opens the complete chronological clinical timeline.
  - `✕ Clear`: Dismisses active patient context.

### 4.4 Global Quick Search (`/`)
- Press `/` from anywhere in the application to summon the search modal.
- Type full or partial patient name, phone number, or UHID.
- Click any result row to immediately lock that patient into the persistent banner.

---

## 5. Domain-by-Domain Operational Workflows

### 5.1 Front Office
- **Patient Registration & Duplicate Check**: Registers new patients with input masking (`+91-XXXXX-XXXXX`), mandatory blood group dropdown, and automated duplication check by phone number. Assigns standard institutional UHID (`UHID-YYYY-XXXX`).
- **Appointments & Doctor Schedules**: Books appointments against standard 15-minute slot intervals, validating against double-booking.
- **OPD Queue & Digital Tokens**: Generates OPD tokens for doctor consultations, tracks queue status (`Waiting`, `In Consultation`, `Completed`).
- **Visitor Passes**: Issues hospital visitor badges with relation to inpatient, contact phone, and room assignment. Tracks check-in and check-out times.

### 5.2 Clinical Care
- **Triage & Acuity Scoring**: Performs standardized Emergency Severity Index (ESI) Level 1 through 5 scoring, vital signs (BP, Pulse, SpO2, Temperature), and presenting complaints.
- **360° EMR & SOAP Consultations**: Records Subjective, Objective, Assessment, and Plan (SOAP) clinical encounter notes with attending physician attribution.
- **e-Prescriptions with Poka-Yoke Allergy Checks**: Selects medicine from active formulary, sets dosage, frequency, and duration. Warns immediately if the patient has a documented allergy matching the prescribed drug.
- **Doctor Clinical Orders**: Physicians dispatch STAT, Urgent, or Routine medication administration and vital monitoring orders directly to the nursing station.
- **Emergency / Trauma Board**: Real-time casualty board tracking incoming trauma cases, GCS scores, resuscitation bays, and attending trauma surgeons.
- **ICU Vital Flowsheet**: Hourly intensive care telemetry recording invasive arterial blood pressure, SpO2, ventilator mode, inotrope titrations, and hourly urine output.
- **Operation Theatre (OT) & WHO Checklist**: Schedules surgical procedures, assigns theatre rooms, lead surgeons, and anaesthetists. Enforces the WHO Surgical Safety Checklist (Sign In, Time Out, Sign Out).
- **Radiology & Medical Imaging**: Orders X-Ray, CT, MRI, and Ultrasound scans. Radiologists review imaging series and file digitally signed diagnostic findings.

### 5.3 Diagnostics
- **Laboratory Information System (LIS)**: Tracks diagnostic investigations through Sample Collection &rarr; Accessioning &rarr; Processing &rarr; Pathologist Verification &rarr; Report Release. Flags critical values outside biological reference intervals.
- **Blood Bank & Transfusion Safety**: Manages voluntary donor registration, serology screening, blood component inventory (Packed Red Blood Cells, Fresh Frozen Plasma, Platelets), and clinical cross-match requests.

### 5.4 Inpatient (IPD)
- **Admissions & Bed Board**: Bed matrix visualizing room availability, current occupancy, and sanitization status across wards (Cardiology, Orthopedics, General, ICU).
- **Bed Transfers**: Moves inpatients between beds or wards with clinical justification and nursing handover.
- **Nursing Station & MAR**: Medication Administration Record tracking dose schedules, vital recordings, and nursing shift handovers.
- **Shift Handover (SBAR)**: Standardized Situation-Background-Assessment-Recommendation transition of patient care between duty shifts.
- **Discharge Summaries**: Formulates clinical course summaries, discharge medications, follow-up advice, and bed turnover clearance.

### 5.5 Pharmacy & Supply
- **Prescription Dispensing**: Dispenses medications directly against active doctor prescriptions, auto-deducts inventory from the relevant batch, and posts charges to billing.
- **Stock, Batches & Expiry Alerts**: Tracks inventory batch numbers and expiration dates. Highlights low-stock medicines below reorder thresholds.
- **Purchase Orders**: Generates supplier procurement purchase orders with delivery date tracking and authorized approval workflows.
- **Central Stores & Consumables**: Manages non-drug hospital supplies (gloves, syringes, surgical drapes, catheters) and issues stock requisitions to hospital wards.

### 5.6 Finance & Accounts
- **Invoicing & Billing**: Consolidates consultation fees, room rent, pharmacy items, and lab investigations into itemized patient bills with GST breakdowns.
- **IPD Advance Deposits**: Collects advance payments for inpatient stays, updates the ledger, and prints advance receipts.
- **Insurance / TPA Claims**: Manages Third-Party Administrator insurance claims, pre-authorization submissions, approved coverage amounts, and cashless settlements.

### 5.7 Support Services
- **Housekeeping & Bed Turnaround**: Coordinates room sanitization tasks (Terminal Clean, Routine, Biohazard) to return discharged beds to `Available` status.
- **Dietetics & Patient Nutrition**: Prescribes customized clinical diets (Diabetic, Renal, High-Protein, Liquid, NPO) and tracks meal preparation and ward delivery.
- **Ambulance Fleet Dispatch**: Logs emergency ambulance dispatches, vehicle types (ALS/BLS), driver assignments, and destination GPS coordinates.
- **Biomedical Assets**: Maintains hospital medical equipment registers (ventilators, defibrillators, dialysis machines) with preventive maintenance and calibration tracking.
- **Facility Maintenance Tickets**: Logs engineering tickets for HVAC, medical gas pipelines, electrical systems, and plumbing.

### 5.8 People & Staff
- **Staff Directory**: Registry of healthcare workers, doctors, nurses, technicians, and administrative staff.
- **Shift Rosters**: Manages morning, evening, and night duty rosters across departments.
- **Leave Requests**: Staff leave submission and supervisor approval workflows.

### 5.9 Quality & Governance
- **Quality Incidents & CAPA**: Root Cause Analysis (RCA) and Corrective & Preventive Action cycles for clinical sentinel events, medication errors, and near misses.
- **Quality Audits**: Structured checklists evaluating hospital infection control, record completeness, and pharmacy expiry audits.
- **Defect Checksheet & Pareto Analysis**: Classifies data-entry defects (missing phone, wrong blood group, unmapped room) and plots defect distributions.
- **Statistical Process Control (SPC)**: 3-Sigma control charts tracking OPD waiting times, medication error rates, and laboratory turnaround times.

### 5.10 System Administration
- **User Management & RBAC**: Administers accounts for all 21 stakeholder roles, locks/unlocks users, and triggers administrative password resets.
- **Database Backup & Hot Recovery**: Creates atomic online SQLite database snapshots with sha256 checksums and automated verification.
- **Security Audit Trail**: Immutable query trail of every database mutation and unauthorized access attempt.

### 5.11 Patient Self-Service Portal
- When logged in with a `Patient` role, accesses personal health records:
  - Upcoming and past doctor appointments.
  - Active e-Prescriptions with dosage instructions.
  - Released diagnostic lab reports.
  - Billing invoices and payment receipts.

---

## 6. Dedicated Clinical Print Views

The system includes standardized print templates that automatically strip away application navigation, sidebars, and buttons during printing (`@media print`):

1. **e-Prescription Slip**:
   - Hospital letterhead with address, contact info, and NABH accreditation tag.
   - Patient demographics strip (UHID, Name, Age/Sex, Blood Group, Allergy alert).
   - Structured Rx medication table (Drug name, dosage, frequency, duration, special instructions).
   - Doctor's digital signature block and medical registration number.
   - ABDM QR code placeholder.
2. **Laboratory Diagnostic Report**:
   - Patient and ordering physician details.
   - Test parameter, observed value, unit, biological reference interval.
   - Highlighted flags for abnormal high/low values.
   - Dual sign-off: Medical Lab Technician and Consultant Pathologist.
3. **Discharge Summary**:
   - Admission and discharge dates with total length of stay.
   - Primary and secondary diagnoses.
   - Clinical course during hospitalization, procedures performed.
   - Discharge medications and dietary/wound care advice.
   - Emergency contact numbers and scheduled follow-up clinic date.
4. **Tax Invoice & Bill**:
   - Invoice number, date, and hospital GSTIN.
   - Itemized charge ledger categorized by department (Consultation, Pharmacy, Diagnostics, Bed charges).
   - Subtotal, GST, advance deposits applied, and net balance due.
   - Cashier signature and payment QR code.

To print any document, open its preview in the application and click the **Print Document** button or press `Ctrl + P`.
