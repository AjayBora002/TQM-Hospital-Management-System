# SIPOC Diagram — Hospital Management System
## Quality Goal: Q07 — Improve Data Accuracy

A SIPOC (Suppliers → Inputs → Process → Outputs → Customers) map shows the end-to-end process flow and identifies where Q07 quality controls intercept each step.

---

## Top-Level SIPOC Table

| **S — Suppliers** | **I — Inputs** | **P — Process Steps** | **O — Outputs** | **C — Customers** |
|---|---|---|---|---|
| Walk-in Patients | Patient demographics (Name, DOB, Phone, Blood Group, Allergies) | 1. Patient Registration | Verified patient record (validated, no duplicates) | Attending Doctors |
| Doctors / Clinical Staff | Doctor specialty, schedule, availability | 2. Doctor & Appointment Management | Confirmed appointment with conflict check | Hospital Scheduling Team |
| Hospital Administration | Room type, capacity, daily rate | 3. Room / Ward Allocation | Room status updated (Available/Occupied) | Nursing & Ward Staff |
| Pharmacists | Medicine name, category, stock level, expiry | 4. Pharmacy & Medicine Management | Accurate stock ledger, low-stock alerts | Billing Officers, Doctors |
| Billing Officers | Room charges, consultation fee, medicine costs | 5. Billing & Invoice Generation | Itemized, auto-verified invoice | Patients, Finance Dept. |
| Quality Auditors | Defect observations, test results | 6. Defect Logging & SQC Analysis | Checksheet entries → Pareto chart → PDCA loop | Hospital Management |
| System (all modules) | Every INSERT, UPDATE, DELETE event | 7. Audit Trail Recording | Immutable audit log entry (timestamp + actor) | Compliance / Accreditation |

---

## Detailed Per-Step Process Map with Q07 Controls

### Step 1: Patient Registration
```
Receptionist Opens Patients Tab
    ↓
Begins Typing Patient Name
    ↓
[Q07-F3] AutocompleteEntry: Existing Match Found?
    ├── YES → Select existing patient → Update via ConfirmDialog
    └── NO  → Proceed to new registration
                ↓
            [Q07-F1] PhoneMaskEntry enforces +91-XXXXX-XXXXX
                ↓
            [Q07-F2] Read-only Combobox: Gender / Blood Group / Allergies
                ↓
            Enter DOB, Address (validator rejects future dates)
                ↓
            Click "Add Patient"
                ↓
            [Q07-F5] log_audit() → SQLite audit_log + audit_logs.csv
```

### Step 2: Appointment Scheduling
```
Open Appointments Tab
    ↓
[Q07-F3] Select Patient via AutocompleteEntry
    ↓
Select Doctor from Department Dropdown [Q07-F2]
    ↓
Enter Date + Time Slot
    ↓
[Clinical] has_conflict() checks doctor & patient calendars
    ├── CONFLICT → Error dialog, user must pick another slot
    └── FREE    → Proceed
                ↓
            Select Status (Scheduled / Completed / Cancelled) [Q07-F2]
                ↓
            Book Appointment → [Q07-F5] Audit recorded
```

### Step 3: Room / Ward Allocation
```
Open Rooms Tab
    ↓
Select Room Type [Q07-F2]
    ↓
Assign Patient via AutocompleteEntry
    ↓
Status updates to Occupied → [Q07-F5] Audit recorded
    ↓
On Discharge: Room Status → Available → [Q07-F5] Audit recorded
```

### Step 4: Medicine / Pharmacy
```
Open Pharmacy Tab
    ↓
Enter Medicine Name (strip() applied, no leading spaces)
    ↓
[Q07-F2] Category Dropdown (read-only)
    ↓
Enter Quantity (validator: qty >= 1)
    ↓
Set Reorder Level → Low-stock flag auto-raised if stock < reorder
    ↓
[Q07-F5] Audit recorded on every change
```

### Step 5: Billing
```
Open Billing Tab
    ↓
[Q07-F3] Select Patient via AutocompleteEntry
    ↓
Enter Room Charges, Consultation Fee, Medicine Charges
    ↓
System auto-computes: Total = Room + Consultation + Medicine (read-only field)
    ↓
[Q07-F2] Payment Method + Status Dropdowns
    ↓
Generate Bill → [Q07-F5] Audit recorded
```

### Step 6: Defect Logging & SQC
```
Staff / Tester Opens Defect Checksheet Tab
    ↓
Select Module, Error Category, Severity [Q07-F2]
    ↓
Enter Count + Remarks
    ↓
Log Defect → Written to defect_log (SQLite) + TQM/data/checksheet.csv
    ↓
Run: python sqc/pareto_chart.py → Pareto PNG (80/20 analysis)
    ↓
Run: python sqc/fishbone_diagram.py → Ishikawa PNG (root causes)
    ↓
PDCA cycle updated in TQM/PDCA.md
```

### Step 7: Audit Trail (Automatic — All Steps)
```
Any database write (INSERT / UPDATE / DELETE)
    ↓
log_audit(table, record_id, action, description) called inside model
    ↓
Atomic write to audit_log table (SQLite)
    ↓
Concurrent write to TQM/data/audit_logs.csv (via logging_service.py)
    ↓
Visible in Audit Log tab of the HMS application
```

---

## Q07 Control Points Summary

| Q07 Feature | Intercepts At Step |
|---|---|
| F1: Input Masking | Step 1 (Patient Registration) |
| F2: Dropdown Lists | Steps 1, 2, 3, 4, 5, 6 (universal) |
| F3: Auto-Complete | Steps 1, 2, 5 (patient/doctor lookup) |
| F4: Confirmation Modals | Any UPDATE or DELETE in all steps |
| F5: Audit Logs | Steps 1, 2, 3, 4, 5, 6, 7 (all write operations) |
