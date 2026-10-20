# GitHub Issues & Defect Tracking Log

**Course:** BBAT104 — Fundamentals of Total Quality Management  
**Academic Session:** 2026–27  
**Student:** Ajay Bora (Roll No: 2410302008 — Branch: CSE — Section B)  
**Baseline System:** Hospital Management System (Digit 2)  
**Assigned Quality Goal:** Q07 — Improve Data Accuracy  
**Repository Identifier:** `BBAT104_TQM_2410302008` (GitHub: `TQM-Hospital-Management-System`)  

---

## 1. Defect Tracking Overview

In accordance with **CO2 & CO3** evaluation requirements and the **BBAT104 Marking Scheme (Documentation & GitHub Health)**, this register records all **15 empirical defect entries** logged in the system's Defect Checksheet (`TQM/data/checksheet.csv`), representing **33 total defect occurrences**.

Each issue is systematically tracked, categorized, analyzed for root causes using Ishikawa/FMEA principles, and mapped to its respective Poka-Yoke resolution commit.

---

### Issue #1: Phone number field accepts arbitrary text and symbols
- **Checksheet Date:** `2026-10-04` | **Module:** `Patient Registration` | **Defect Count:** 5
- **Category:** `Data Entry` | **Severity:** `High` | **Status:** `Closed`
- **Description:** Entering alphabetical characters or partial digits (e.g. `phone="abc"`) was accepted during patient intake, causing emergency contacts to be invalid.
- **Root Cause:** Standard text entry widget lacked keystroke filtering, regex validation, or length enforcement.
- **TQM Resolution:** Engineered `PhoneMaskEntry` (`src/widgets/phone_mask_entry.py`) enforcing `+91-XXXXX-XXXXX` format and restricting input exclusively to numerical digits.
- **Commit:** `feat(widgets): Implement PhoneMaskEntry for +91 phone formatting (Q07 Feature 1)`

---

### Issue #2: Inconsistent blood group capitalization and free text causing search mismatch
- **Checksheet Date:** `2026-10-04` | **Module:** `Patient Registration` | **Defect Count:** 3
- **Category:** `Data Entry` | **Severity:** `Medium` | **Status:** `Closed`
- **Description:** Users typed `b+`, `b positive`, or `B+`, creating fragmented records and breaking donor search queries.
- **Root Cause:** Unrestricted free-text input field for blood group.
- **TQM Resolution:** Replaced free-text entry with a read-only `ttk.Combobox` linked to standard blood group constants in `src/config.py`.
- **Commit:** `feat(patient): Build Patients registration tab with phone mask and dropdowns (Q07 Feature 2)`

---

### Issue #3: Duplicate patient records created during walk-in appointments
- **Checksheet Date:** `2026-10-04` | **Module:** `Appointments` | **Defect Count:** 2
- **Category:** `Data Entry` | **Severity:** `High` | **Status:** `Closed`
- **Description:** Receptionists registered returning patients under slight spelling variations, duplicating patient history charts.
- **Root Cause:** Lack of real-time search during patient selection.
- **TQM Resolution:** Engineered `AutocompleteEntry` (`src/widgets/autocomplete_entry.py`) displaying matching registered patients dynamically as characters are entered.
- **Commit:** `feat(widgets): Implement AutocompleteEntry for patient lookup (Q07 Feature 3)`

---

### Issue #4: Date of birth field allows future and invalid calendar dates
- **Checksheet Date:** `2026-10-05` | **Module:** `Patient Registration` | **Defect Count:** 4
- **Category:** `Validation` | **Severity:** `High` | **Status:** `Closed`
- **Description:** System permitted dates like `1990-02-31` or future dates (e.g. `2099-01-01`), corrupting demographic reporting.
- **Root Cause:** Absence of calendar and boundary checks on date of birth input.
- **TQM Resolution:** Added `validate_patient_payload()` in `src/utils/validators.py` verifying format, calendar reality, and ensuring DOB <= today.
- **Commit:** `feat(utils): Add input validation helpers for dates, times, and phone formats`

---

### Issue #5: Total bill amount manually overridden by user without calculation integrity
- **Checksheet Date:** `2026-10-05` | **Module:** `Billing` | **Defect Count:** 3
- **Category:** `Validation` | **Severity:** `High` | **Status:** `Closed`
- **Description:** Operators could edit the calculated total field, resulting in invoices where total did not equal room + consultation + medicine charges.
- **Root Cause:** Total bill amount entry field was editable instead of calculated server-side.
- **TQM Resolution:** Total amount is now auto-computed in `src/models/bill.py` and displayed as a read-only field in both desktop and web interfaces.
- **Commit:** `fix(billing): Enforce explicit float coercion for financial calculations`

---

### Issue #6: Room number duplicated on re-entry causing ward management collision
- **Checksheet Date:** `2026-10-05` | **Module:** `Rooms/Wards` | **Defect Count:** 2
- **Category:** `Data Entry` | **Severity:** `Medium` | **Status:** `Closed`
- **Description:** Staff accidentally created multiple rooms with identical room numbers (e.g., duplicate '101').
- **Root Cause:** Absence of database-level UNIQUE constraint on `room_number`.
- **TQM Resolution:** Enforced `UNIQUE` constraint on `room_number` in SQLite schema and added pre-insert validation check.
- **Commit:** `feat(room): Enforce unique room number constraint and ward status management`

---

### Issue #7: Accidental appointment deletion without user confirmation modal
- **Checksheet Date:** `2026-10-06` | **Module:** `Appointments` | **Defect Count:** 2
- **Category:** `UI` | **Severity:** `Critical` | **Status:** `Closed`
- **Description:** Single click on delete button dropped appointment schedules immediately without warning.
- **Root Cause:** Missing confirmation guard before invoking delete controller.
- **TQM Resolution:** Integrated `ConfirmDialog` modal prompt (`src/widgets/confirm_dialog.py`) requiring explicit modal confirmation before every `Delete` and `Update` action.
- **Commit:** `feat(widgets): Implement ConfirmDialog modal for update/delete (Q07 Feature 4)`

---

### Issue #8: Patient record updated without confirmation prompt causing accidental overwrite
- **Checksheet Date:** `2026-10-06` | **Module:** `Patient Registration` | **Defect Count:** 1
- **Category:** `UI` | **Severity:** `High` | **Status:** `Closed`
- **Description:** Updating patient demographics occurred immediately upon button click, occasionally overwriting valid contact info.
- **Root Cause:** Direct dispatch of database update without review step.
- **TQM Resolution:** Wrapped all update triggers with `ConfirmDialog` confirmation modals.
- **Commit:** `feat(widgets): Implement ConfirmDialog modal for update/delete (Q07 Feature 4)`

---

### Issue #9: Negative medicine stock quantities accepted by inventory module
- **Checksheet Date:** `2026-10-06` | **Module:** `Pharmacy` | **Defect Count:** 3
- **Category:** `Validation` | **Severity:** `High` | **Status:** `Closed`
- **Description:** Stock updates accepted negative integers, producing phantom inventory deficits.
- **Root Cause:** Missing non-negative boundary constraint on `stock_qty` and `reorder_level`.
- **TQM Resolution:** Added non-negative validation in `src/models/medicine.py` enforcing `stock_qty >= 0`.
- **Commit:** `feat(pharmacy): Implement medicine inventory model with reorder thresholds`

---

### Issue #10: Bill total computed incorrectly when medicine or consultation charges are null
- **Checksheet Date:** `2026-10-07` | **Module:** `Billing` | **Defect Count:** 2
- **Category:** `Business Logic` | **Severity:** `Medium` | **Status:** `Closed`
- **Description:** If a patient had no pharmacy charges, `None` coerced arithmetic caused calculation errors.
- **Root Cause:** Lack of safe null-coalescing (`val or 0.0`) in invoice calculation pipeline.
- **TQM Resolution:** Enforced explicit zero-coalescing and float conversions in `src/models/bill.py`.
- **Commit:** `fix(billing): Enforce explicit float coercion for financial calculations`

---

### Issue #11: Medicine name saved with leading/trailing whitespace breaking inventory searches
- **Checksheet Date:** `2026-10-07` | **Module:** `Pharmacy` | **Defect Count:** 1
- **Category:** `Data Entry` | **Severity:** `Low` | **Status:** `Closed`
- **Description:** Entering `" Paracetamol "` caused exact string lookups to fail during billing dispatch.
- **Root Cause:** Omission of input string sanitization (`.strip()`).
- **TQM Resolution:** Added automated `.strip()` sanitization across all text entry models.
- **Commit:** `fix(models): Strip whitespace and normalize string attributes across models`

---

### Issue #12: Untracked data modifications and missing record_id in audit trail
- **Checksheet Date:** `2026-10-08` | **Module:** `Audit Log` | **Defect Count:** 1
- **Category:** `Validation` | **Severity:** `High` | **Status:** `Closed`
- **Description:** A DELETE transaction was recorded without referencing the target `record_id`, hindering post-mortem investigation.
- **Root Cause:** Inconsistent audit call signature during model refactoring.
- **TQM Resolution:** Unified `log_audit()` signature across all 8 models; dual-logged to SQLite `audit_log` and `TQM/data/audit_logs.csv`.
- **Commit:** `feat(audit): Implement audit logging and defect checksheet models`

---

### Issue #13: Staff shift entered as free text causing inconsistent duty roster
- **Checksheet Date:** `2026-10-08` | **Module:** `Staff` | **Defect Count:** 1
- **Category:** `Data Entry` | **Severity:** `Low` | **Status:** `Closed`
- **Description:** Shift values like `'morning'`, `'AM'`, and `'Day'` coexisted in staff table.
- **Root Cause:** Free-text input on staff onboarding interface.
- **TQM Resolution:** Bound shift field to read-only `Combobox` constrained to `SHIFTS = ["Morning", "Evening", "Night"]` in `src/config.py`.
- **Commit:** `feat(staff): Build Staff directory tab with role and shift scheduling`

---

### Issue #14: Doctor double-booking and schedule slot conflict not prevented
- **Checksheet Date:** `2026-10-09` | **Module:** `Appointments` | **Defect Count:** 2
- **Category:** `Validation` | **Severity:** `High` | **Status:** `Closed`
- **Description:** Multiple appointments could be booked for the same doctor at the same date and time.
- **Root Cause:** Absence of conflict check on `(doctor_id, appt_date, appt_time)`.
- **TQM Resolution:** Added `has_conflict()` check in `src/models/appointment.py` and HTTP 409 conflict responses in web API.
- **Commit:** `fix(appointment): Add mandatory guard checks for appointment date and time`

---

### Issue #15: Allergy field accepted free text without standardized contraindication checks
- **Checksheet Date:** `2026-10-10` | **Module:** `Patient Registration` | **Defect Count:** 1
- **Category:** `Validation` | **Severity:** `Critical` | **Status:** `Closed`
- **Description:** Unstandardized allergy entries prevented the system from cross-referencing prescribed drugs for adverse drug reactions (ADR).
- **Root Cause:** Absence of controlled allergy vocabulary and clinical contraindication checks.
- **TQM Resolution:** Bound allergies to `ALLERGIES` constants and implemented `check_drug_allergy_contraindication()` in `src/utils/validators.py`.
- **Commit:** `feat(clinical): Implement clinical poka-yoke with allergy cross-checking and vitals triage`

---

## 2. Defect Distribution Summary (Pareto Input)

| Rank | Defect Category | Checksheet Issues | Defect Count | Percentage | Cumulative % | Pareto Classification |
|:---:|---|:---:|:---:|:---:|:---:|---|
| 1 | **Data Entry** | 6 issues (#1, #2, #3, #6, #11, #13) | **14** | **42.42%** | **42.42%** | **Vital Few** (Primary Root Cause) |
| 2 | **Validation** | 6 issues (#4, #5, #9, #12, #14, #15) | **14** | **42.42%** | **84.85%** | **Vital Few** (**Crosses 80% Threshold**) |
| 3 | **UI** | 2 issues (#7, #8) | **3** | **9.09%** | **93.94%** | Useful Many |
| 4 | **Business Logic** | 1 issue (#10) | **2** | **6.06%** | **100.00%** | Useful Many |
| — | **Total** | **15 Issues** | **33 Defects** | **100.00%** | — | — |

> **Key 80/20 Finding:** The top 2 categories (Data Entry + Validation) account for **28 out of 33 defects (84.85%)**, crossing the 80% threshold at just 2 of 4 categories (50% of causes driving ~85% of defects).
