# GitHub Issues & Defect Tracking Log

**Course:** BBAT104 — Fundamentals of Total Quality Management  
**Academic Session:** 2026–27  
**Student:** Ajay Bora (Branch: CSE — Section B)  
**Baseline System:** Hospital Management System (Digit 2)  
**Assigned Quality Goal:** Q07 — Improve Data Accuracy  
**Repository:** `TQM-Hospital-Management-System`  

---

## 1. Defect Tracking Overview

In accordance with **CO2 & CO3** evaluation requirements and the **BBAT104 Marking Scheme (Documentation & GitHub Health)**, this document registers the 11 defects logged in the system's Defect Checksheet. Each issue is categorized, analyzed for root causes using TQM methodologies, and mapped to its resolution commit.

---

### Issue #1: Phone number field accepts arbitrary text and symbols
- **Category:** `Data Entry` | **Severity:** `High` | **Status:** `Closed`
- **Description:** During patient registration, entering alphabetical characters or partial digits (e.g. `phone="abc"`) was accepted and written to the database.
- **Root Cause:** Standard text entry widget lacked keystroke filtering, regex validation, or length enforcement.
- **TQM Resolution:** Implemented `PhoneMaskEntry` (`src/widgets/phone_mask_entry.py`) enforcing `+91-XXXXX-XXXXX` format and restricting input exclusively to numerical digits.
- **Commit:** `feat(widgets): Implement PhoneMaskEntry for +91 phone formatting (Q07 Feature 1)`

---

### Issue #2: Inconsistent blood group capitalization causing search mismatch
- **Category:** `Data Entry` | **Severity:** `Medium` | **Status:** `Closed`
- **Description:** Users typed `b+`, `B positive`, or `B+`, creating fragmented records and breaking donor search queries.
- **Root Cause:** Unrestricted free-text input field for blood group.
- **TQM Resolution:** Replaced free-text entry with a read-only `ttk.Combobox` linked to standard blood group constants in `src/config.py`.
- **Commit:** `feat(patient): Build Patients registration tab with phone mask and dropdowns (Q07 Feature 2)`

---

### Issue #3: Duplicate patient records created during walk-in appointments
- **Category:** `Data Entry` | **Severity:** `High` | **Status:** `Closed`
- **Description:** Receptionists registered returning patients under slight spelling variations, duplicating patient history.
- **Root Cause:** Lack of real-time search during patient selection.
- **TQM Resolution:** Engineered `AutocompleteEntry` (`src/widgets/autocomplete_entry.py`) displaying matching registered patients dynamically as characters are entered.
- **Commit:** `feat(widgets): Implement AutocompleteEntry for patient lookup (Q07 Feature 3)`

---

### Issue #4: Accidental record deletion without user confirmation
- **Category:** `UI` | **Severity:** `Critical` | **Status:** `Closed`
- **Description:** Clicking the "Delete" button immediately dropped patient/doctor records without prompting for confirmation.
- **Root Cause:** Missing confirmation guard before triggering model delete calls.
- **TQM Resolution:** Integrated `ConfirmDialog` modal prompt (`src/widgets/confirm_dialog.py`) before every `Delete` and `Update` action.
- **Commit:** `feat(widgets): Implement ConfirmDialog modal for update/delete (Q07 Feature 4)`

---

### Issue #5: Untracked data modifications in patient records
- **Category:** `Validation` | **Severity:** `High` | **Status:** `Closed`
- **Description:** Updates made to patient demographic and room records lacked audit trails, making it impossible to identify when or why changes occurred.
- **Root Cause:** Database operations did not capture transaction metadata.
- **TQM Resolution:** Built central `log_audit()` helper and a dedicated **Audit Log** tab logging all `INSERT`, `UPDATE`, and `DELETE` events.
- **Commit:** `feat(audit): Implement audit logging and defect checksheet models`

---

### Issue #6: Date of birth field allows invalid calendar dates
- **Category:** `Validation` | **Severity:** `Medium` | **Status:** `Closed`
- **Description:** Users entered invalid dates like `1990-02-31` or `2099-01-01` without rejection.
- **Root Cause:** Lack of strict `datetime.strptime` validation on DOB entry.
- **TQM Resolution:** Added `validate_dob()` helper in `src/utils/validators.py` verifying format, calendar validity, and ensuring birth date is in the past.
- **Commit:** `feat(utils): Add input validation helpers for dates, times, and phone formats`

---

### Issue #7: Negative values allowed in billing charges
- **Category:** `Validation` | **Severity:** `High` | **Status:** `Closed`
- **Description:** Negative numbers could be inputted into Consultation Fee or Medicine Charges, lowering the total bill.
- **Root Cause:** Lack of boundary checks on numeric billing inputs.
- **TQM Resolution:** Added non-negative float validation checks in `src/utils/validators.py` and `src/models/bill.py`.
- **Commit:** `fix(billing): Enforce explicit float coercion for financial calculations`

---

### Issue #8: Appointment scheduling allows conflicting doctor timeslots
- **Category:** `Business Logic` | **Severity:** `Medium` | **Status:** `Closed`
- **Description:** Multiple appointments could be scheduled for the same doctor at the identical date and time.
- **Root Cause:** Missing uniqueness check on `(doctor_id, appt_date, appt_time)`.
- **TQM Resolution:** Added conflict check prior to appointment creation in `src/models/appointment.py`.
- **Commit:** `fix(appointment): Add mandatory guard checks for appointment date and time`

---

### Issue #9: Medicine stock depletion without reorder warning
- **Category:** `Database` | **Severity:** `High` | **Status:** `Closed`
- **Description:** Pharmacy inventory reached zero without alerting staff, causing emergency stockouts.
- **Root Cause:** No notification query checking current stock against minimum threshold.
- **TQM Resolution:** Implemented `low_stock()` query flagging items where `stock_qty <= reorder_level` with visual tags.
- **Commit:** `feat(pharmacy): Implement medicine inventory model with reorder thresholds`

---

### Issue #10: Doctor department misspellings in roster
- **Category:** `Data Entry` | **Severity:** `Low` | **Status:** `Closed`
- **Description:** Manual entry of medical departments resulted in typos (`Cardiology` vs `Cardio`), fragmenting department lists.
- **Root Cause:** Unconstrained text entry on doctor onboarding form.
- **TQM Resolution:** Enforced `DEPARTMENTS` constant list in `src/config.py` via read-only dropdown.
- **Commit:** `feat(doctor): Build Doctors roster tab UI with specialty department dropdowns`

---

### Issue #11: Bill status displayed as paid without payment method selection
- **Category:** `Validation` | **Severity:** `Medium` | **Status:** `Closed`
- **Description:** Bills could be marked "Paid" while leaving payment method blank.
- **Root Cause:** Missing conditional validation on payment fields.
- **TQM Resolution:** Enforced mandatory payment method selection whenever status is marked "Paid".
- **Commit:** `feat(billing): Build Billing tab UI with invoice generation and payment tracking`

---

## 2. Defect Distribution Summary (Pareto Input)

| Defect Category | Frequency | Percentage | Cumulative % | Vital Few Classification |
|---|:---:|:---:|:---:|:---|
| **Data Entry** | 5 | 45.45% | 45.45% | **Vital 80% Driver** |
| **Validation** | 4 | 36.36% | 81.82% | **Vital 80% Driver** |
| **UI** | 1 | 9.09% | 90.91% | Useful Many |
| **Database** | 1 | 9.09% | 100.00% | Useful Many |
| **Total** | **11** | **100.00%** | — | — |
