# Hospital Management System (HMS) — User & Operations Manual
**Course:** BBAT104 Total Quality Management & Software Quality Audit  
**Student:** Ajay Bora | Branch: CSE | Section: B  
**Baseline System:** Hospital Management System (Digit 2)  
**Assigned Quality Goal:** Q07 — Improve Data Accuracy  

---

## 1. System Overview & Objectives
The **Hospital Management System (HMS)** is a modular desktop application designed under Total Quality Management (TQM) principles to eliminate data entry defects, prevent patient record duplication, and streamline hospital administrative operations.

### Key Operational Capabilities
- **Patient Registration & Records:** Captures patient demographics, blood groups, contact details, and optional room assignments.
- **Doctor Roster & Specialties:** Manages medical staff by specialized department with direct contact linking.
- **Appointment Scheduling:** Links registered patients with consulting doctors, tracking scheduling timestamps and statuses.
- **Ward & Bed Management:** Monitors room inventory (General, Semi-Private, Deluxe, ICU) and occupancy status in real time.
- **Staff Administration:** Tracks nursing and support staff across roles and shift rotations.
- **Pharmacy & Inventory:** Manages medicine stocks, unit costs, and provides automatic visual flags for low stock.
- **Billing & Invoicing:** Automatically calculates total hospital charges (room + consultation + medicines) and tracks payment status.
- **Q07 Quality Control Suite:** Integrated **Audit Log** (every change timestamped) and **Defect Checksheet** (empirical defect tracking feeding Pareto & Fishbone analysis).

---

## 2. Installation & Quick Start

### 2.1 Prerequisites
- **Python:** Version 3.10 or higher.
- **Dependencies:** `matplotlib` (for SQC charts) and `openpyxl` (for FMEA Excel generation).
- **GUI:** Standard Tkinter (bundled with official Python installers).

### 2.2 Setup Instructions
```bash
# 1. Clone or navigate to the project directory
cd HMS_Project_AjayBora

# 2. Install required SQC & Excel libraries
pip install -r requirements.txt

# 3. Run the application
python src/main.py

# 4. Run automated unit test suite
python tests/test_db.py
```

> **Note:** The SQLite database `src/database/hms.db` is initialized automatically on first startup with pre-seeded sample records for immediate evaluation.

---

## 3. Q07 Data Accuracy Features Walkthrough (Poka-Yoke)

In accordance with Quality Goal **Q07: Improve Data Accuracy**, five reusable error-prevention mechanisms have been engineered across all data entry forms:

| Feature # | Feature Name | Component | Practical User Experience |
|:---:|:---|:---|:---|
| **1** | **Input Masking** | `widgets/phone_mask_entry.py` | Automatically formats telephone numbers as `+91-XXXXX-XXXXX`. Prevents non-numeric input and ensures standard Indian phone formats without manual spacing. |
| **2** | **Dropdown Lists** | `config.py` + `ttk.Combobox` | Replaces open text fields with fixed, validated option lists for: Gender, Blood Group, Department, Appointment Status, Room Type/Status, Staff Role/Shift, and Payment Method/Status. Eliminates spelling mistakes and formatting inconsistencies. |
| **3** | **Auto-Complete** | `widgets/autocomplete_entry.py` | Provides real-time matching suggestions while typing patient names during search, appointment booking, and billing. Prevents duplicate patient creation. |
| **4** | **Confirmation Modals** | `widgets/confirm_dialog.py` | Displays an explicit modal dialog (`askyesno`) before performing any **Update** or **Delete** operation, protecting against accidental record destruction. |
| **5** | **Audit Trail Logging** | `database/db_manager.log_audit()` + `views/audit_view.py` | Automatically logs an immutable, timestamped record for every `INSERT`, `UPDATE`, and `DELETE` across every database table, accessible in the **Audit Log** tab. |

---

## 4. Module-by-Module Operation Guide

### 4.1 Dashboard
- **Access:** First tab upon launch.
- **Function:** Displays real-time operational metrics across all 8 modules (Total Patients, Active Doctors, Scheduled Appointments, Available Beds, Pending Bills, Logged Defects, and Audit Events).
- **Usage:** Click **Refresh Dashboard** to recalculate live totals instantly.

### 4.2 Patients Module
- **Adding a Patient:**
  1. Fill in Patient Full Name.
  2. Select Gender and Blood Group from the standard dropdowns.
  3. Enter Date of Birth in `YYYY-MM-DD` format.
  4. Type a 10-digit mobile number in the Phone field (the `+91-` prefix and hyphens format automatically).
  5. Select an available room from the Room dropdown (optional).
  6. Click **Add Patient**.
- **Updating/Deleting:** Select a patient from the table list. The fields auto-populate. Modify details and click **Update** (or **Delete**). Confirm the action on the popup modal.
- **Search:** Enter part of a name or phone in the Search box and click **Search**.

### 4.3 Doctors Module
- Enter Doctor Name, select Department from the dropdown list, and enter phone number using the input mask.
- Click **Add Doctor** to enroll the physician into the hospital roster.

### 4.4 Appointments Module
- **Booking an Appointment:**
  1. Start typing the patient name in the Patient field — the Auto-Complete dropdown reveals matching existing patients.
  2. Select Consulting Doctor from the dropdown roster.
  3. Enter Appointment Date (`YYYY-MM-DD`) and Time (`HH:MM`).
  4. Select Status (`Scheduled`, `Completed`, `Cancelled`).
  5. Click **Book Appointment**.

### 4.5 Rooms / Wards Module
- Manage hospital bed availability across `General`, `Semi-Private`, `Deluxe`, and `ICU`.
- Mark rooms as `Available`, `Occupied`, or `Maintenance`. Daily rate is stored and utilized during patient discharge billing.

### 4.6 Staff Module
- Manage non-physician medical staff (Nurses, Receptionists, Pharmacists, Lab Technicians, Ward Boys).
- Assign shift schedules: `Morning`, `Evening`, `Night`, or `Rotational`.

### 4.7 Pharmacy (Medicines & Inventory)
- Track medicines, dosage forms (Tablet, Capsule, Syrup, Injection, Ointment), unit price, current stock, and reorder levels.
- **Safety Alert:** When medicine stock reaches or falls below the designated `reorder_level`, it is flagged for replenishment to prevent drug stockouts.

### 4.8 Billing & Invoicing Module
- Select patient using the Auto-Complete search box.
- Enter Room Charges, Consultation Fee, and Medicine Charges.
- Click **Generate Bill**: The system auto-calculates `total_amount = room + consultation + medicine` and logs the transaction.
- Update payment status between `Unpaid`, `Partial`, and `Paid`.

### 4.9 Audit Log Tab
- Read-only real-time security log showing:
  - Timestamp of modification
  - Table name affected
  - Record ID
  - Action performed (`INSERT`, `UPDATE`, `DELETE`)
  - Description of change

### 4.10 Defect Checksheet Tab (SQC Tool)
- Standardized data entry tool for capturing software and process defects.
- Allows quality auditors to log:
  - **Category:** `Data Entry`, `Validation`, `UI`, `Database`, `Business Logic`, etc.
  - **Description:** Specific anomaly detected.
  - **Severity:** `Low`, `Medium`, `High`, `Critical`.
- Feeds live data into the Statistical Quality Control (SQC) Pareto analysis scripts.

---

## 5. Statistical Quality Control (SQC) Scripts

### 5.1 Pareto Chart (80/20 Rule Analysis)
Run the automated Pareto analysis script:
```bash
python sqc/pareto_chart.py
```
- **Output:** Generates `sqc/pareto_chart.png`.
- **Purpose:** Identifies the "vital few" defect categories that generate 80% of system errors. Demonstrates that targeted Q07 features (Input Masking & Dropdowns) resolve ~80% of data errors.

### 5.2 Ishikawa (Fishbone) Diagram
Run the root-cause generation script:
```bash
python sqc/fishbone_diagram.py
```
- **Output:** Generates `sqc/fishbone_diagram.png`.
- **Purpose:** Categorizes root causes of hospital data inaccuracies across four branches: **People**, **Process**, **Software Code**, and **Infrastructure**.

### 5.3 FMEA Risk Audit Generation
Regenerate the automated Excel workbook containing the FMEA risk assessment and Defect Checksheet:
```bash
python docs/build_fmea.py
```
- **Output:** Generates `docs/FMEA_RiskAudit.xlsx` with dynamic Excel formulas for Risk Priority Numbers (`RPN = Severity * Occurrence * Detection`).

---

## 6. Troubleshooting & FAQs
<!-- Verified for Academic Session 2026-27 Evaluation -->

**Q: Running `python src/main.py` gives an import error or cannot find modules.**  
A: Ensure you are executing the command from the root project folder (`HMS_Project_AjayBora`).

**Q: How do I reset the database to clean demo data?**  
A: Simply delete `src/database/hms.db` and re-run `python src/main.py`. The database will automatically recreate with fresh initial data.

**Q: Can I run unit tests without opening the GUI?**  
A: Yes! Run `python tests/test_db.py`. It uses an isolated temporary database and tests all 8 core models headlessly in <0.2 seconds.
