# Hospital Management System — User & Operations Manual

**Course:** BBAT104 — Fundamentals of Total Quality Management  
**Academic Session:** 2026–27  
**Student:** Ajay Bora (Roll No: 2410302008 — Branch: CSE — Section B)  
**Baseline System:** Hospital Management System (Digit 2)  
**Assigned Quality Goal:** Q07 — Improve Data Accuracy  
**Repository Identifier:** `BBAT104_TQM_2410302008` (GitHub: `TQM-Hospital-Management-System`)  

---

## 1. Executive Summary & Purpose

This User and Operations Manual provides comprehensive instructions for operating, configuring, verifying, and testing the **Hospital Management System (HMS)**. Developed in strict accordance with the **BBAT104 Course Project Guidelines**, the system integrates modern hospital administration workflows with rigorous **Total Quality Management (TQM)** error-prevention principles.

The central quality paradigm is **Poka-Yoke (Mistake-Proofing)** under **Quality Goal Q07 (Improve Data Accuracy)**: preventing flawed inputs at the user interface and data-access layers before they can corrupt clinical or administrative records.

---

## 2. System Architecture & Requirements

### 2.1 Technology Stack & Prerequisites
- **Operating System:** Windows, macOS, or Linux.
- **Runtime Environment:** Python 3.10 or higher.
- **Desktop UI Framework:** Standard `tkinter` / `ttk` (bundled with official Python).
- **Web Portal Framework:** Lightweight Flask-based web application with HTML5/CSS3/Vanilla JS.
- **Data Persistence:** Relational SQLite 3 (`src/database/hms.db`), zero external server configuration required.
- **Statistical Quality Control (SQC) Tools:** `matplotlib` for Pareto charts and Ishikawa (Fishbone) diagrams.
- **Risk Audit Engine:** `openpyxl` for formula-driven FMEA Risk Priority Number (RPN) calculations.

### 2.2 Dependencies Installation
From the project root directory, install all required packages:
```bash
pip install -r requirements.txt
```

---

## 3. Quick Start & Execution Modes

The HMS platform provides two distinct, fully synchronized user interfaces:

### Option A: Native Desktop GUI (Tkinter) — Primary Syllabus Deliverable
```bash
python run.py
```
- Automatically initializes the database schema and default records on first launch.
- Launches the **multi-tab native Tkinter desktop application** (10 module tabs).
- Implements all 5 Q07 widget-level controls: Input Masking, Dropdown Lists, Auto-Complete, Confirmation Modals, and Audit Logs.
- Prescribed by **BBAT104 Section 6.1**: *"Tkinter/CustomTkinter (GUI interfaces)"*

### Option B: Web Application Portal (Optional Demo)
```bash
python run.py --web
```
- Launches the local HTTP server at `http://127.0.0.1:5000`.
- Provides an interactive browser-based dashboard with REST API endpoints and the same 5 Q07 features implemented in JavaScript + Flask.

### Option C: Automated Quality Verification (Unit Test Suite)
```bash
python -m unittest discover tests
```
- Executes 28 automated tests covering CRUD operations, boundary validation, and TQM audit trails with zero failures.

---

## 4. Q07 Data Accuracy Feature Walkthrough (Poka-Yoke)

In compliance with **Q07: Improve Data Accuracy**, five reusable mistake-proofing controls have been implemented across all data-entry workflows:

| Feature # | Feature Name | Implementation File | Operational Impact |
|:---:|:---|:---|:---|
| **1** | **Input Masking** | `src/widgets/phone_mask_entry.py` | Automatically formats phone numbers to `+91-XXXXX-XXXXX`. Dynamically filters keystrokes with regex to strip non-digits, enforcing exact 10-digit telephone standards. |
| **2** | **Dropdown Lists** | `src/config.py` + `ttk.Combobox(state="readonly")` | Replaces vulnerable free-text inputs with standardized, immutable choice sets for Gender, Blood Group, Medical Department, Appointment Status, Room Type/Status, Staff Role/Shift, and Payment Status. |
| **3** | **Auto-Complete Search** | `src/widgets/autocomplete_entry.py` | Real-time substring query engine querying registered patient names as characters are entered. Surfaces matching records instantly, preventing duplicate chart creation. |
| **4** | **Confirmation Modals** | `src/widgets/confirm_dialog.py` | Wraps critical operations in explicit two-step confirmation prompts before allowing `UPDATE` or `DELETE` executions, preventing accidental record loss. |
| **5** | **Audit Trail Logging** | `src/database/db_manager.py` (`log_audit`) | Atomic transactional logger recording every `INSERT`, `UPDATE`, and `DELETE` with table name, record ID, modification summary, and exact timestamp. Viewable via the dedicated Audit Log tab. |

---

## 5. Module-by-Module Operational Guide

The system features 10 integrated modules:

### 5.1 Dashboard
- **Location:** Tab 1 / Web Home View.
- **Functionality:** Aggregates real-time metrics across all hospital departments: Total Patients, Active Doctors, Scheduled Appointments, Available Beds, Pending Invoices, Logged Quality Defects, and Historical Audit Events.
- **Operation:** Displays live counters and updates automatically whenever records are created, modified, or discharged.

### 5.2 Patients Registration & Records
- **Institutional UHID Generation:** Every newly registered patient is automatically assigned an immutable institutional Unique Hospital Identifier (e.g., `UHID-2026-00042`), adhering strictly to NABH and ABDM national guidelines.
- **Adding a Patient:**
  1. Navigate to the **Patients** tab.
  2. Enter Patient Full Name.
  3. Select **Gender** and **Blood Group** from the restricted dropdown menus.
  4. Input Date of Birth in standard format (`YYYY-MM-DD`).
  5. Enter a 10-digit mobile number in the **Phone** field — notice the automatic prefixing of `+91-` and hyphenation.
  6. Document known drug allergies (e.g., `Penicillin`, `Sulfa Drugs`) to activate downstream clinical Poka-Yoke prescribing safeguards.
  7. Optionally assign an available hospital room.
  8. Click **Add Patient**.
- **Updating / Deleting:** Select a patient from the record table. The form auto-populates. Edit fields and click **Update** or **Delete**. A confirmation modal will appear requiring explicit verification.
- **Search:** Enter search terms into the patient query box to locate records by name, telephone number, or UHID.

### 5.3 Doctors Roster
- Manage attending physicians and specialists.
- Register doctors by selecting their department from the pre-configured medical specialties list (`Cardiology`, `Neurology`, `Orthopedics`, `Pediatrics`, `General Medicine`, `Dermatology`, `ENT`, `Oncology`).
- Enforces phone number input masking for professional contact records.

### 5.4 Appointments Scheduling
- Schedule consultations between registered patients and available doctors.
- **Auto-Complete Integration:** Type the patient name — the system auto-completes from registered records, eliminating typos and scheduling conflicts.
- **Pre-Flight Conflict Prevention:** Real-time conflict engine (`has_conflict`) intercepts overlapping doctor slots with HTTP 409 conflict blocking.
- **Standardized Process States:** Supports the complete NABH outpatient lifecycle: `Scheduled`, `Confirmed`, `Checked-in`, `Waiting`, `In consultation`, `Completed`, `Cancelled`, `No-show`.

### 5.5 Ward & Bed Management
- Oversee room inventory across five categories: `General Ward`, `Semi-Private`, `Private`, `ICU`, and `Operation Theatre`.
- Monitor standardized bed states: `Available`, `Occupied`, `Under Maintenance`, `Cleaning / Sanitizing`, `Reserved`, `Blocked`.
- Pre-configured standard daily tariffs are maintained for automatic integration with patient billing.
- **Automated Bed Clearance:** Discharging a patient automatically transitions room status to `Cleaning / Sanitizing` or `Available`.

### 5.6 Staff Administration
- Manage hospital nursing, administrative, and paramedical staff.
- Restrict staff assignments to designated roles (`Nurse`, `Receptionist`, `Pharmacist`, `Lab Technician`, `Ward Boy`) and shifts (`Morning`, `Evening`, `Night`, `Rotational`).

### 5.7 Pharmacy & Inventory
- Maintain medicine inventories, unit prices, dosage forms, and stock quantities.
- **Automated Reorder Safeguard:** When inventory levels drop to or below the configured `reorder_level`, items are automatically tagged with a low-stock alert to prevent pharmaceutical stockouts.

### 5.8 Billing & Invoicing
- Generate patient invoices combining room tariffs, physician consultation fees, and prescribed medicine charges.
- **Poka-Yoke Automatic Calculation:** The system programmatically computes `total_amount = room_charges + consultation_fee + medicine_charges`, completely eliminating arithmetic errors.
- Track invoice payment statuses (`Unpaid`, `Partial`, `Paid`).

### 5.9 Audit Log Explorer (Read-Only)
- Accessible by administrators and compliance auditors.
- Displays an immutable log of all database transactions with timestamp, table name, affected primary key, action type, and descriptive details.

### 5.10 Defect Checksheet (SQC Data Capture)
- Standardized data-capture matrix for logging quality defects encountered during system audits.
- Records defect category (`Data Entry`, `Validation`, `UI`, `Database`, `Business Logic`), description, and severity (`Low`, `Medium`, `High`, `Critical`).
- Provides the empirical dataset feeding the Pareto analysis and Ishikawa diagrams.

### 5.11 Pharmacy Batch & Expiry Date Poka-Yoke Safeguard
- **Location:** Pharmacy tab & REST API `/api/medicines/expired`.
- **Functionality:** Every medicine tracks `batch_no` and `expiry_date`.
- **Clinical Poka-Yoke:** The system **automatically blocks** prescribing or dispensing any expired pharmaceutical batch with an immediate `CLINICAL SAFETY ALERT`.

### 5.12 Diagnostic Laboratory Testing & Reference Intervals
- **Location:** Lab Diagnostics module & REST API `/api/lab-tests`.
- **Functionality:** Orders pathology and radiology tests. Pre-populated biological reference ranges (e.g., Hemoglobin $12.0 - 17.5$ g/dL, Fasting Sugar $70 - 99$ mg/dL).
- **Poka-Yoke Flagging:** Results outside standard reference boundaries automatically flag `abnormal_flag = 1` in bold red for immediate physician attention.

### 5.13 Printable Medical Invoices & Discharge Summaries
- **Location:** Billing & Admissions routes (`/api/bills/<id>/receipt`, `/api/admissions/<id>/discharge-summary`).
- **Functionality:** Instant print-ready HTML documents with `@media print` styling, itemized financial breakdowns, and NABH-compliant discharge summaries.

### 5.14 Emergency Priority Triage Queue
- **Location:** Dashboard & `/api/triage/queue`.
- **Functionality:** Automated Manchester/ESI triage engine ranking emergency arrivals into **Code Red (Resuscitation)**, **Code Yellow (Urgent)**, and **Code Green (Stable)** based on real-time vitals ($SpO_2$, BP, pulse, temperature).

### 5.15 Patient 360° Comprehensive Medical Journey
- **Location:** Patient Chart & `/api/patients/<id>/timeline`.
- **Functionality:** Aggregates a complete, single-screen chronological timeline of all patient interactions: registration, vitals history, consultations, admissions, lab orders, prescriptions, and payments.

### 5.16 Automated Pharmacy Purchase Orders (PO)
- **Location:** Pharmacy & `/api/purchase-orders`.
- **Functionality:** Automatically scans for inventory at or below reorder levels and generates standardized supplier orders. Receiving an order automatically restocks inventory.

### 5.17 NABH & ISO 9001 Hospital Quality Inspection Checklist
- **Location:** Quality Audit & `/api/quality-audits`.
- **Functionality:** Formal compliance inspection tool across departments (Patient Safety, Pharmacy, Infection Control, Invoicing) computing compliance percentages.

### 5.18 Desktop Startup Login Dialog & Role Switcher
- **Location:** Desktop Tkinter startup window (`src/views/login_dialog.py`).
- **Functionality:** Secure credentials entry with 1-click Quick Login buttons for Admin (`admin123`), Doctor (`doctor123`), and Receptionist (`recep123`), or Guest Demo Bypass.

---

## 6. Statistical Quality Control (SQC) Tools Execution

### 6.1 Pareto Analysis (80/20 Rule)
Execute the Pareto chart script to isolate the vital few root causes of data errors:
```bash
python sqc/pareto_chart.py
```
- **Output:** Saves high-resolution chart to `sqc/pareto_chart.png`.
- **Finding:** Confirms that `Data Entry` (45.5%) and `Validation` (36.4%) constitute **81.8%** of total defects, mathematically justifying the implementation of Q07 controls.

### 6.2 Ishikawa (Fishbone) Diagram
Generate the root cause diagram categorized across People, Process, Software Code, and Infrastructure:
```bash
python sqc/fishbone_diagram.py
```
- **Output:** Saves root-cause visualization to `sqc/fishbone_diagram.png`.

### 6.3 Shewhart Statistical Process Control (SPC c-Chart)
Generate the analytical Shewhart control chart to verify process stabilization:
```bash
python sqc/spc_chart.py
```
- **Output:** Saves control chart to `sqc/spc_control_chart.png` and CSV parameters to `TQM/data/spc_metrics.csv`.
- **Finding:** Demonstrates process capability shift from initial high error rates (pre-intervention) to zero 3-sigma violations under active Poka-Yoke controls.

### 6.4 FMEA Risk Matrix Generation
Regenerate the automated Excel workbook containing formula-driven RPN risk scores:
```bash
python docs/build_fmea.py
```
- **Output:** Updates `docs/FMEA_RiskAudit.xlsx` with dynamic Excel formulas for Risk Priority Numbers (`RPN = Severity * Occurrence * Detection`).

---

## 7. Troubleshooting & FAQ

| Problem | Likely Cause | Solution |
|---|---|---|
| `ModuleNotFoundError: No module named 'matplotlib'` | Dependencies not yet installed | Run `pip install -r requirements.txt` |
| Tkinter window fails to open in headless server | Headless Linux environment without X11 | Run the web portal using `python run.py` instead |
| Need clean demo dataset | Pre-existing local test data | Delete `src/database/hms.db` and launch `python run.py` or `python src/main.py` to auto-seed fresh records |
| How to verify test coverage? | Automated test execution | Run `python -m unittest discover tests` |
