# Project Evaluation & Defense Dossier (Review-1 & Review-2)
**Course:** BBAT104 — Fundamentals of Total Quality Management  
**Project:** Hospital Management System (HMS) — TQM-Driven Healthcare Informatics  
**Student:** Ajay Bora | **Roll No:** 2410302008 | **Branch:** CSE — Section B  
**Academic Session:** 2026–27  
**Official Guideline Identifier:** `BBAT104_TQM_2410302008`  

---

## 1. Executive Purpose

This document serves as the master defense and evaluation dossier for **Review-1** (System Design & Requirements Engineering) and **Review-2** (Software Demonstration & Quality Evidence) in strict alignment with **Sections 20, 21, and 25 of the Base Project Guideline**.

The objective is to equip the student with an airtight presentation script, live demonstration steps, and verifiable evidence proving that this project is not a generic CRUD database, but a disciplined, TQM-engineered healthcare informatics system.

---

## 2. Review-1 Evaluation Dossier: System Design & Requirements

### 2.1 Review-1 Deliverables Checklist

| Guideline Requirement (Section 20) | Implementation Evidence in Repository | Document / Source Reference | Status |
|---|---|---|:---:|
| **Specific Hospital Process & Problem Statement** | Outpatient Department (OPD) & Emergency Triage Journey; Elimination of duplicate records, double-booking, and medication errors. | `docs/LITERATURE_REVIEW.md` (Sec 6) | **READY** |
| **Literature Review** | NABH 6th Edition (all 10 chapters analyzed) + ABDM national digital health framework + 3 system benchmarks. | `docs/LITERATURE_REVIEW.md` (Sec 2–5) | **READY** |
| **Stakeholder Map & Needs** | 10 hospital roles analyzed with explicit information needs, interaction touchpoints, and KPIs. | `docs/STAKEHOLDER_SRS_TRACEABILITY.md` (Sec 2) | **READY** |
| **Numbered, Testable SRS** | 24 atomic specifications (`SR-PAT-001` through `SR-SEC-003`) categorized by clinical domains. | `docs/STAKEHOLDER_SRS_TRACEABILITY.md` (Sec 3) | **READY** |
| **Traceability Matrix** | 6-way matrix linking Stakeholder $\leftrightarrow$ SRS $\leftrightarrow$ Process $\leftrightarrow$ Schema $\leftrightarrow$ UI $\leftrightarrow$ Test. | `docs/STAKEHOLDER_SRS_TRACEABILITY.md` (Sec 4) | **READY** |
| **Process Maps (As-Is / To-Be)** | Waste/delay analysis; multi-role swimlane sequence; finite state machines for Appointments, Lab, Beds. | `docs/PROCESS_WORKFLOW_MAPS.md` | **READY** |
| **Role-Permission Matrix** | Server-side enforced matrix for Admin, Doctor, Receptionist, Nurse, Lab Tech, Cashier. | `docs/architecture.md` (Sec 5) | **READY** |
| **Initial ERD & Data Dictionary** | 14 relational tables with primary keys, foreign keys, constraints, and audit entities. | `docs/ER_Diagram.md`, `src/database/db_manager.py` | **READY** |
| **Layered Architecture Rationale** | Strict multi-tier separation (Presentation $\rightarrow$ REST Blueprints $\rightarrow$ Business Rules $\rightarrow$ SQL Models $\rightarrow$ DB). | `docs/architecture.md` | **READY** |
| **FMEA Risk Prioritization** | 12 failure modes evaluated with Pre/Post RPN calculations demonstrating >90% risk reduction. | `TQM/FMEA.md`, `docs/FMEA_RiskAudit.xlsx` | **READY** |
| **P0 / P1 / P2 Prioritization** | Coherent scope boundaries: P0 Core Intake, P1 Connected Clinical Care, P2 TQM Analytics. | `docs/SRS.md`, `docs/STAKEHOLDER_SRS_TRACEABILITY.md` | **READY** |

---

## 3. Review-2 Evaluation Dossier: Software Demonstration & Quality Evidence

Review-2 evaluates whether the implemented software executes the designed requirements reliably and demonstrates measurable quality improvement.

### 3.1 Live Demonstration Script (Step-by-Step)

The demonstration follows a coherent, end-to-end patient journey:

```text
[Step 1: Poka-Yoke Intake] ──> [Step 2: Emergency Triage] ──> [Step 3: Conflict-Free Slot]
                                                                        │
[Step 6: Real-Time SPC]   <── [Step 5: Itemized Bill]    <── [Step 4: Safe Prescribing]
```

#### Step 1: Patient Intake & Poka-Yoke Registration
- **Action:** Open Desktop GUI (`python run.py`) or Web Portal (`python run.py --web` at `http://127.0.0.1:5000`).
- **Demonstrate:**
  1. Begin typing an existing patient name ("Rohan") in the Auto-Complete field; show existing chart suggestions to prevent duplicate creation.
  2. Type a phone number into the registration field; demonstrate that non-digit characters are stripped and formatted as `+91-XXXXX-XXXXX`.
  3. Attempt to save without mandatory fields; show validation banner.
  4. Submit valid patient ("Aarav Sharma", Blood Group "O+", Allergy "Penicillin").
  5. Show institutional permanent UHID generated: `UHID-2026-XXXXX`.

#### Step 2: Emergency Triage & Physiological Acuity
- **Action:** Navigate to Emergency Triage module.
- **Demonstrate:**
  1. Enter abnormal vital signs for the patient (BP: 190/110 mmHg, Pulse: 125 bpm, SpO2: 88%).
  2. System automatically categorizes patient as **Code Red (Immediate Emergency)**.
  3. Show patient instantly prioritized to the top of the Emergency Queue.

#### Step 3: Conflict-Free Doctor Consultation Booking
- **Action:** Navigate to Appointments tab.
- **Demonstrate:**
  1. Select Dr. Shalini Kapoor (Cardiology) for tomorrow at `10:30`.
  2. Book successfully.
  3. **Negative Test (Double-Booking Error Prevention):** Attempt to book another patient with Dr. Shalini Kapoor for the exact same date and time slot (`10:30`).
  4. **System Response:** Operation blocked! Shows error modal: *"Doctor already has an active appointment at 2026-11-20 10:30. Double-booking prevented."* (HTTP 409 Conflict).

#### Step 4: Clinical Consultation & Pre-Flight ADR Allergy Poka-Yoke
- **Action:** Open Patient 360° Timeline for Aarav Sharma.
- **Demonstrate:**
  1. Patient allergy badge clearly highlights **Penicillin**.
  2. **Negative Test (Adverse Drug Reaction Prevention):** Doctor attempts to prescribe *"Amoxicillin 500mg"* (a Penicillin class antibiotic).
  3. **System Response:** Poka-Yoke contraindication check intercepts the order! Pop-up warning: *"CONTRAINDICATION WARNING: Patient has documented allergy to 'Penicillin'. Cannot prescribe 'Amoxicillin'!"*
  4. Prescribe a safe alternative (*"Azithromycin 500mg"*); system verifies batch number and expiry date before signing.

#### Step 5: Diagnostic Investigation & Reference Range Abnormal Flag
- **Action:** Order a Laboratory Test (*"Fasting Blood Sugar"*).
- **Demonstrate:**
  1. Input result: `185 mg/dL` (Biological Reference: 70–99 mg/dL).
  2. System compares result against boundaries and automatically sets `abnormal_flag = 1`.
  3. Result badge appears highlighted in red in the Patient 360° record.

#### Step 6: Transparent Itemized Invoicing & Discharge
- **Action:** Generate Bill.
- **Demonstrate:**
  1. Enter charges; total auto-calculates ($0.00 + 500.00 + 320.00 = 820.00$). Total field is read-only to prevent manual calculation discrepancy.
  2. Click **Print Tax Receipt**; show formatted, print-ready HTML receipt with institutional header.
  3. Complete discharge; show bed state automatically toggled from `Occupied` to `Cleaning / Sanitizing`.

#### Step 7: Dual-Tier Audit Trail & TQM Statistical Process Control
- **Action:** Open Audit Log and Quality Dashboard.
- **Demonstrate:**
  1. Show that every single action performed above generated an immutable log entry in SQLite `audit_log` with user identity and timestamp.
  2. Show defect checksheet logging.
  3. Display the **Shewhart SPC Control Chart (c-Chart)** showing Central Line ($CL = \bar{c}$), Upper Control Limit ($UCL = \bar{c} + 3\sqrt{\bar{c}}$), and Lower Control Limit ($LCL$).
  4. Display live **Six Sigma DPMO** calculation (e.g., $DPMO = 2,450 \implies 4.31\sigma$).

---

