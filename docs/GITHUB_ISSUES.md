# GitHub Issues & Defect Tracking Log
**Project:** Hospital Management System &nbsp;|&nbsp; **Quality Goal:** Q07 — Improve Data Accuracy  
**Course:** BBAT104 Course Project &nbsp;|&nbsp; **Student:** Ajay Bora (CSE-B)  

This register contains the 11 defects logged in the Defect Checksheet, mapped to GitHub Issue tickets, root cause analyses, and their corresponding bugfix commits.

---

### Issue #1: Phone number field accepts arbitrary text and symbols
- **Category:** `Data Entry` | **Severity:** `High` | **Status:** `Closed`
- **Description:** During patient registration, entering alphabetical characters or partial digits (e.g. `phone="abc"`) was accepted and written to the database.
- **Root Cause:** Standard `tk.Entry` widget without keystroke filtering or regex validation.
- **Resolution:** Implemented `PhoneMaskEntry` widget enforcing `+91-XXXXX-XXXXX` format and restricting input to digits only.
- **Commit:** `Fixes #1: Enforce phone input masking and numerical keystroke filter`

---

### Issue #2: Inconsistent blood group capitalization causing search mismatch
- **Category:** `Data Entry` | **Severity:** `Medium` | **Status:** `Closed`
- **Description:** Users typed `b+`, `B positive`, or `B+`, creating fragmented records and breaking donor search queries.
- **Root Cause:** Free-text input field for blood group.
- **Resolution:** Replaced free-text input with a read-only `ttk.Combobox` linked to standard blood group constants in `config.py`.
- **Commit:** `Fixes #2: Standardize blood group field with read-only combobox`

---

### Issue #3: Duplicate patient records created during walk-in appointments
- **Category:** `Data Entry` | **Severity:** `High` | **Status:** `Closed`
- **Description:** Receptionists registered returning patients under slight spelling variations, duplicating patient history.
- **Root Cause:** Lack of real-time search during patient selection.
- **Resolution:** Built `AutocompleteEntry` widget displaying matching registered patients dynamically as characters are entered.
- **Commit:** `Fixes #3: Add autocomplete entry to prevent duplicate patient registration`

---

### Issue #4: Accidental record deletion without user confirmation
- **Category:** `UI` | **Severity:** `Critical` | **Status:** `Closed`
- **Description:** Clicking the "Delete" button immediately dropped patient/doctor records without prompting for confirmation.
- **Root Cause:** Missing confirmation guard before triggering model delete calls.
- **Resolution:** Integrated `widgets/confirm_dialog.py` modal prompt before every `Delete` and `Update` action.
- **Commit:** `Fixes #4: Add modal confirmation dialog on record deletion`

---

### Issue #5: Untracked data modifications in patient records
- **Category:** `Validation` | **Severity:** `High` | **Status:** `Closed`
- **Description:** Updates made to patient demographic and room records lacked audit trails, making it impossible to identify when or why changes occurred.
- **Root Cause:** Database operations did not capture transaction metadata.
- **Resolution:** Built central `log_audit()` helper and a dedicated **Audit Log** tab logging all `INSERT`, `UPDATE`, and `DELETE` events.
- **Commit:** `Fixes #5: Implement centralized audit logging for all database mutations`

---

### Issue #6: Date of birth field allows invalid calendar dates
- **Category:** `Validation` | **Severity:** `Medium` | **Status:** `Closed`
- **Description:** Users entered invalid dates like `1990-02-31` or `2099-01-01` without rejection.
- **Root Cause:** Lack of strict `datetime.strptime` validation on DOB entry.
- **Resolution:** Added `validate_dob()` helper verifying format, real calendar existence, and ensuring birth date is in the past.
- **Commit:** `Fixes #6: Add strict date parsing and range validation for patient DOB`

---

### Issue #7: Negative values allowed in billing charges
- **Category:** `Validation` | **Severity:** `High` | **Status:** `Closed`
- **Description:** Negative numbers could be inputted into Consultation Fee or Medicine Charges, lowering the total bill.
- **Root Cause:** Lack of boundary checks on numeric billing inputs.
- **Resolution:** Added non-negative float validation checks in `validators.py` and `bill.py`.
- **Commit:** `Fixes #7: Enforce non-negative numeric constraints on billing amounts`

---

### Issue #8: Appointment scheduling allows conflicting doctor timeslots
- **Category:** `Business Logic` | **Severity:** `Medium` | **Status:** `Closed`
- **Description:** Multiple appointments could be scheduled for the same doctor at the identical date and time.
- **Root Cause:** Missing uniqueness constraint on `(doctor_id, appt_date, appt_time)`.
- **Resolution:** Added conflict check prior to appointment creation.
- **Commit:** `Fixes #8: Add doctor schedule conflict prevention logic`

---

### Issue #9: Medicine stock depletion without reorder warning
- **Category:** `Database` | **Severity:** `High` | **Status:** `Closed`
- **Description:** Pharmacy inventory reached zero without alerting staff, causing emergency stockouts.
- **Root Cause:** No notification query checking current stock against minimum threshold.
- **Resolution:** Implemented `low_stock()` query flagging items where `stock_qty <= reorder_level` with visual tags.
- **Commit:** `Fixes #9: Implement automated low stock flagging in pharmacy module`

---

### Issue #10: Doctor department misspellings in roster
- **Category:** `Data Entry` | **Severity:** `Low` | **Status:** `Closed`
- **Description:** Manual entry of medical departments resulted in typos (`Cardiology` vs `Cardio`), fragmenting department lists.
- **Root Cause:** Unconstrained text entry on doctor onboarding form.
- **Resolution:** Enforced `DEPARTMENTS` constant list in `config.py` via read-only dropdown.
- **Commit:** `Fixes #10: Bind doctor department to fixed configuration list`

---

### Issue #11: Bill status displayed as paid without payment method selection
- **Category:** `Validation` | **Severity:** `Medium` | **Status:** `Closed`
- **Description:** Bills could be marked "Paid" while leaving payment method blank.
- **Root Cause:** Missing conditional validation on payment fields.
- **Resolution:** Enforced mandatory payment method selection whenever status is marked "Paid".
- **Commit:** `Fixes #11: Require valid payment method on paid invoice transitions`
