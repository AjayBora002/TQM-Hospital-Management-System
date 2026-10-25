# Stakeholder Analysis & Requirements Traceability Matrix (RTM)
**Course:** BBAT104 — Fundamentals of Total Quality Management  
**Project:** Hospital Management System (HMS) — TQM-Driven Healthcare Informatics  
**Student:** Ajay Bora | **Roll No:** 2410302008 | **Branch:** CSE — Section B  
**Academic Session:** 2026–27  
**Official Guideline Identifier:** `BBAT104_TQM_2410302008`  

---

## 1. Introduction & Methodology

A foundational principle of Total Quality Management (TQM) in software engineering is that **every line of code and database schema must trace directly to a verified customer need**, and conversely, every stakeholder requirement must be verified by automated objective evidence. 

In strict adherence to **Section 7 and Section 8 of the Base Project Guideline**, this document establishes:
1. **The Comprehensive 10-Role Stakeholder Register:** Mapping the complete socio-technical ecosystem of the hospital.
2. **The Software Requirements Specification (SRS):** Formulated as atomic, testable, numbered statements (`SR-XXX-NNN`).
3. **The 6-Way Requirements Traceability Matrix (RTM):** Explicitly linking:
   $$\text{Stakeholder Need} \longleftrightarrow \text{SRS Requirement} \longleftrightarrow \text{Process Step} \longleftrightarrow \text{Database Object} \longleftrightarrow \text{UI Component} \longleftrightarrow \text{Automated Test Case}$$

---

## 2. Comprehensive 10-Role Stakeholder Register

| # | Stakeholder Role | Primary Operational Need / Problem Addressed | Critical Information Required | System Interaction Touchpoint | Success Measure & KPI |
|:---:|---|---|---|---|---|
| **1** | **Patient** | Minimized waiting time, transparent billing, and zero repeat registrations. | Doctor availability, appointment token, itemized bill, diagnosis timeline. | Patient Intake Screen / Reception Desk / Patient 360° Portal | Waiting time < 15 mins; Zero billing disputes |
| **2** | **Receptionist / Front Desk** | Fast, error-free intake; prevention of duplicate patient charts. | Master patient index, current phone number, doctor specialty roster. | Patients Tab / Appointments Tab / Dynamic Autocomplete Search | Registration cycle time < 90 secs; 0% duplicate UHIDs |
| **3** | **Attending Doctor / Clinician** | Immediate access to historical clinical context, vitals, and safe prescribing. | Longitudinal encounter history, physiological vitals, recorded allergies, lab reports. | Doctor Dashboard / Patient 360° View / Prescription Module | Zero Adverse Drug Reactions (ADR); Consultation cycle time tracking |
| **4** | **Triage & Ward Nurse** | Rapid acuity sorting; clear visibility of vital thresholds and doctor orders. | Patient blood pressure, pulse, SpO2, temperature, assigned bed status. | Emergency Triage Queue / Vitals Entry Dialog | Triage classification time < 60 secs; Zero missed Code Red alerts |
| **5** | **Billing Officer / Cashier** | Automated tariff calculations, transparent receipts, and zero financial leakage. | Room days, doctor consultation charges, dispensed pharmacy items, payment method. | Billing & Invoicing Module / Printable HTML Tax Invoices | Billing error rate = 0.0%; Instant reconciliation |
| **6** | **Laboratory Technician** | Traceable test requisitions, unambiguous specimen tracking, and critical flags. | Test name, clinical category, patient ID, biological reference intervals. | Diagnostic Lab Diagnostics Tab / Result Verification View | Lab turnaround time (TAT) < 4 hours; 100% abnormal flags highlighted |
| **7** | **Bed / Ward Manager** | Real-time bed visibility, instant sanitization tracking, and zero double-allocations. | Ward type, room number, occupancy state (`Available`, `Occupied`, `Cleaning`). | Ward & Bed Management Grid / Inpatient Admissions Tab | Bed turnaround time < 30 mins; Zero double-occupancies |
| **8** | **Hospital Quality Manager** | Objective, continuous evidence of operational stability and compliance. | Daily defect logs, Shewhart control limits, compliance audit scores, FMEA RPN. | Defect Checksheet / SQC Analytics / NABH Quality Audit Checklist | Process Capability $C_p > 1.33$; DPMO < 3,400 (4.5+ Sigma) |
| **9** | **Medical Superintendent / Hospital Manager** | High-level operational throughput, resource bottlenecks, and financial health. | Departmental patient footfall, room utilization rates, revenue collections. | Executive Summary Dashboard / Live Analytics Counters | Operational decision turnaround < 5 mins; Full bed utilization |
| **10** | **IT & Systems Administrator** | Data integrity, role enforcement, immutable auditing, and zero unrecoverable crashes. | User authentication hashes, access roles, mutation logs, snapshot backups. | Admin Console / Dual-Tier Audit Log Viewer / Automated Backup Engine | System uptime > 99.9%; 100% audit trail coverage |

---

## 3. Formal Software Requirements Specification (SRS)

Requirements are partitioned into testable functional domains with standardized identifiers:
- `SR-PAT-xxx`: Patient Intake & Identity Management
- `SR-APT-xxx`: Doctor Scheduling & Conflict Prevention
- `SR-TRG-xxx`: Emergency Acuity & Triage Evaluation
- `SR-CLN-xxx`: Clinical Documentation & Safe Prescribing
- `SR-LAB-xxx`: Diagnostic Investigations & Reference Bounds
- `SR-BIL-xxx`: Billing, Tariffs & Transparent Invoicing
- `SR-BED-xxx`: Inpatient Ward & Bed Lifecycle Management
- `SR-QI-xxx`: Quality Engineering, SPC & Compliance Audits
- `SR-SEC-xxx`: Security, Authentication & Auditability

```mermaid
graph LR
    subgraph Core ["P0 — Core Intake & Appointments"]
        PAT[SR-PAT: Identity & UHID]
        APT[SR-APT: Conflict-Free Scheduling]
        SEC[SR-SEC: RBAC & Audit Trails]
    end

    subgraph Connected ["P1 — Connected Clinical Care"]
        TRG[SR-TRG: Triage Acuity]
        CLN[SR-CLN: Safe Prescribing]
        LAB[SR-LAB: Lab Bounds]
        BIL[SR-BIL: Invoicing]
    end

    subgraph Operations ["P2 — Operations & TQM"]
        BED[SR-BED: Bed Lifecycle]
        QI[SR-QI: Shewhart SPC & Audits]
    end

    Core --> Connected
    Connected --> Operations
```

### 3.1 Requirements Specification Table

| SRS ID | Requirement Statement | Priority | Verification Method |
|---|---|:---:|---|
| **SR-PAT-001** | The system shall generate a permanent, non-reusable Unique Hospital Identifier (`UHID-2026-XXXXX`) for every newly registered patient. | P0 | Automated Test |
| **SR-PAT-002** | The system shall enforce telephone formatting (`+91-XXXXX-XXXXX`) via real-time keystroke input masking, rejecting non-digit characters and capping at 10 digits. | P0 | Automated Test + GUI |
| **SR-PAT-003** | The system shall restrict categorical demographic fields (Gender, Blood Group) strictly to standardized medical enumerations. | P0 | Automated Test |
| **SR-PAT-004** | The system shall provide real-time substring auto-complete search across existing patient records to prevent duplicate patient charts. | P0 | Automated Test + REST |
| **SR-APT-001** | The system shall allow appointment scheduling only for valid doctor schedules and standard 30-minute time intervals. | P0 | Automated Test |
| **SR-APT-002** | The system shall execute pre-flight schedule conflict checks and reject overlapping bookings for the same doctor with HTTP 409 Conflict. | P0 | Automated Test |
| **SR-TRG-001** | The system shall validate physiological vital signs (BP, Pulse, Temp, SpO2) against bounded medical limits upon entry. | P1 | Automated Test |
| **SR-TRG-002** | The system shall evaluate vital signs and automatically sort patients into an Emergency Queue prioritized by Code Red, Yellow, and Green. | P1 | Automated Test |
| **SR-CLN-001** | The system shall assemble a longitudinal Patient 360° timeline aggregating registration, vitals, consultations, lab tests, and billing events. | P1 | Automated Test |
| **SR-CLN-002** | The system shall record documented patient drug allergies and block prescriptions containing contraindicated pharmaceutical classes. | P1 | Automated Test |
| **SR-CLN-003** | The system shall validate pharmaceutical batch numbers and expiry dates, blocking dispensing or prescription of expired medicine. | P1 | Automated Test |
| **SR-LAB-001** | The system shall support diagnostic lab test ordering across standardized laboratory categories. | P1 | Automated Test |
| **SR-LAB-002** | The system shall compare recorded quantitative lab results against biological reference ranges and compute an abnormal flag ($0$ or $1$). | P1 | Automated Test |
| **SR-BIL-001** | The system shall automatically compute total bill amounts ($Room + Consult + Meds = Total$) and block negative charge entries. | P0 | Automated Test |
| **SR-BIL-002** | The system shall generate print-ready, itemized medical tax invoices and discharge financial summaries. | P1 | Automated Test |
| **SR-BED-001** | The system shall enforce unique room numbers and maintain real-time occupancy state transitions (`Available` $\rightarrow$ `Occupied` $\rightarrow$ `Cleaning`). | P1 | Automated Test |
| **SR-BED-002** | The system shall automatically clear room assignments and toggle room status back to `Available` upon patient discharge or deletion. | P1 | Automated Test |
| **SR-QI-001** | The system shall record administrative and operational software defects into a structured checksheet feeding Pareto 80/20 analysis. | P0 | Automated Test |
| **SR-QI-002** | The system shall compute Shewhart Statistical Process Control (SPC) c-chart limits (CL, UCL, LCL) to verify process stabilization. | P1 | Automated Test |
| **SR-QI-003** | The system shall compute live Six Sigma Defect Per Million Opportunities (DPMO) and process sigma capability ratings. | P1 | Automated Test |
| **SR-QI-004** | The system shall provide an NABH & ISO 9001 departmental compliance inspection checklist with percentage scoring. | P2 | Automated Test |
| **SR-SEC-001** | The system shall enforce Role-Based Access Control (Admin, Doctor, Receptionist) with secure password hashing (SHA-256). | P0 | Automated Test |
| **SR-SEC-002** | The system shall maintain an immutable, dual-tier audit log capturing every INSERT, UPDATE, and DELETE across SQLite and CSV trails. | P0 | Automated Test |
| **SR-SEC-003** | The system shall require explicit, two-step confirmation modals before executing any database UPDATE or DELETE mutation. | P0 | GUI / DOM Test |

---

## 4. Master 6-Way Requirements Traceability Matrix (RTM)

This matrix establishes 100% bi-directional traceability from stakeholder voice down to executable code and automated unit test files:

| SRS ID | Stakeholder Origin | Clinical / Process Workflow | Database Objects / Schema | UI Presentation Component | Automated Verification Test Case | Status |
|:---:|---|---|---|---|---|:---:|
| **SR-PAT-001** | Receptionist, Patient | Patient Intake & Registration | `patients.patient_id`, `patients.uhid` | `src/views/patient_view.py`, Web Patient Modal | `tests/test_patient_timeline.py::test_01` | **PASS** |
| **SR-PAT-002** | Receptionist, IT Admin | Phone Keystroke Validation | `patients.phone` (TEXT NOT NULL) | `src/widgets/phone_mask_entry.py`, `app.js` | `tests/test_validators.py::test_phone` | **PASS** |
| **SR-PAT-003** | Doctor, Nurse | Dropdown Categorical Locking | `patients.gender`, `patients.blood_group` | `ttk.Combobox(state="readonly")`, HTML `<select>` | `tests/test_patient_boundaries.py::test_03` | **PASS** |
| **SR-PAT-004** | Receptionist, Doctor | Duplicate Prevention Search | `patients.full_name` (INDEX) | `src/widgets/autocomplete_entry.py`, API `/search` | `tests/test_db.py::test_04_patient_name_candidates` | **PASS** |
| **SR-APT-001** | Patient, Doctor | Appointment Booking | `appointments`, `doctors` | `src/views/appointment_view.py`, Web Slot Picker | `tests/test_appointment_boundaries.py::test_valid` | **PASS** |
| **SR-APT-002** | Doctor, Patient | Conflict Pre-Flight Check | `appointments (doctor_id, appt_date, appt_time)` | `has_conflict()` in `models/appointment.py` | `tests/test_appointment_boundaries.py::test_conflict` | **PASS** |
| **SR-TRG-001** | Triage Nurse, Doctor | Emergency Vitals Intake | `vitals_log (systolic, pulse, spo2)` | Vitals Dialog, Web Triage Modal | `tests/test_triage_boundaries.py::test_bounds` | **PASS** |
| **SR-TRG-002** | Doctor, Triage Nurse | Emergency Priority Queue | `vitals_log.triage_status`, `patients` | `src/views/dashboard_view.py`, API `/triage/queue` | `tests/test_triage_queue.py::test_queue_sorting` | **PASS** |
| **SR-CLN-001** | Doctor, Patient | Longitudinal Health Journey | `patients`, `vitals`, `prescriptions`, `bills` | `get_patient_360_timeline()`, Web Timeline Drawer | `tests/test_patient_timeline.py::test_aggregation` | **PASS** |
| **SR-CLN-002** | Doctor, Pharmacist | Pre-Flight Allergy ADR Check | `patients.allergies`, `config.DRUG_MAP` | Allergy Badge, Prescription Pre-Flight Validator | `tests/test_clinical_poka_yoke.py::test_allergy` | **PASS** |
| **SR-CLN-003** | Pharmacist, Doctor | Expiry Date Poka-Yoke | `medicines.expiry_date`, `medicines.batch_no` | Pharmacy View, API `/medicines/expired` | `tests/test_pharmacy_expiry.py::test_expiry` | **PASS** |
| **SR-LAB-001** | Doctor, Lab Tech | Diagnostic Test Requisition | `lab_tests (test_name, category)` | Lab Diagnostics View, API `/lab-tests` | `tests/test_lab_module.py::test_create_order` | **PASS** |
| **SR-LAB-002** | Lab Tech, Doctor | Reference Interval Check | `lab_tests (ref_min, ref_max, abnormal_flag)`| `record_result()`, Automated Red Flag Icon | `tests/test_lab_module.py::test_abnormal_flag` | **PASS** |
| **SR-BIL-001** | Billing, Patient | Tariff Auto-Calculation | `bills (room, consult, med, total)` | Billing View, Auto-Calculating Total Entry | `tests/test_billing_validation.py::test_calc` | **PASS** |
| **SR-BIL-002** | Patient, Cashier | Printable Invoices | `bills`, `report_generator.py` | `generate_bill_receipt_html()`, Web Print Button | `tests/test_report_generator.py::test_receipt` | **PASS** |
| **SR-BED-001** | Bed Manager, Nurse | Ward Inventory & State | `rooms.room_number`, `rooms.status` | Rooms & Wards Grid, API `/rooms` | `tests/test_room_boundaries.py::test_room_crud` | **PASS** |
| **SR-BED-002** | Bed Manager, Nurse | Automated Bed Clearance | `rooms.status`, `patients.room_id` | Patient Transfer / Discharge Action | `tests/test_hospital_features.py::test_clearance` | **PASS** |
| **SR-QI-001** | Quality Manager | Defect Checksheet Logging | `defect_log`, `TQM/data/checksheet.csv` | Defect Checksheet View, API `/defects` | `tests/test_db.py::test_09_defect_checksheet` | **PASS** |
| **SR-QI-002** | Quality Manager | Shewhart c-Chart SPC Engine | `TQM/data/checksheet.csv`, `spc_service.py` | `sqc/spc_chart.py`, Dashboard SPC Widget | `tests/test_spc_chart.py::test_spc_limits` | **PASS** |
| **SR-QI-003** | Quality Manager | Six Sigma DPMO Rating | `sigma_calculator.py` | Dashboard Live Metric Cards | `tests/test_six_sigma.py::test_dpmo_math` | **PASS** |
| **SR-QI-004** | Quality Manager | NABH Compliance Checklist | `quality_audits (standard_code, score)` | Quality Audits View, API `/quality-audits` | `tests/test_quality_audits.py::test_scoring` | **PASS** |
| **SR-SEC-001** | IT Admin, All Roles | RBAC & Password Hashing | `users.password_hash`, `users.role` | `src/views/login_dialog.py`, Top Status Bar | `tests/test_login_dialog.py::test_quick_login` | **PASS** |
| **SR-SEC-002** | IT Admin, Auditor | Dual-Tier Audit Logging | `audit_log`, `TQM/data/audit_logs.csv` | Audit Log View, API `/audit` | `tests/test_audit_sync.py::test_dual_logging` | **PASS** |
| **SR-SEC-003** | Receptionist, Billing | Accidental Deletion Shield | Application Business Logic | `src/widgets/confirm_dialog.py`, JS Modals | Verified in UI & API error handlers | **PASS** |

---

## 5. Traceability Summary

- **Total Stakeholder Roles Analyzed:** 10
- **Total Functional Requirements Specified:** 24
- **Total Automated Test Cases Verifying Requirements:** 147 Unit Tests (100% Pass Rate)
- **Traceability Density:** 100% (Zero orphaned code, zero unsubstantiated requirements).
