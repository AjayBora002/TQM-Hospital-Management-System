# PDCA (Plan-Do-Check-Act) Continuous Improvement Log

**Course:** BBAT104 — Fundamentals of Total Quality Management  
**Academic Session:** 2026–27  
**Student:** Ajay Bora (Branch: CSE — Section B)  
**Baseline System:** Hospital Management System (Digit 2)  
**Assigned Quality Goal:** Q07 — Improve Data Accuracy  
**Repository:** `TQM-Hospital-Management-System`  

This document logs the continuous-improvement cycles driven by empirical defect logging and Statistical Quality Control (SQC) analysis, fulfilling **Review 4 (CO2 & CO3)** evaluation requirements.

---

## Cycle 1 — Data Entry & Validation Accuracy

### 1. PLAN
- **Defect Analysis:** Pareto analysis demonstrated that **Data Entry** defects (5 of 11 logged, ~45.5%) and **Validation** defects (4 of 11, ~36.4%) comprised **81.8%** of total defects—representing the "vital few" crossing the 80% cumulative threshold.
- **Root Cause Isolation:** Ishikawa (Fishbone) analysis categorized root causes into:
  - *Software Code:* Unrestricted free-text fields, absence of input masks, lack of dropdown choice constraints.
  - *Process:* Absence of standardized data entry protocols, lack of confirmation prompts before destructive actions.
  - *People:* Operator fatigue and rushing during peak hospital intake.
- **Target Objectives:** Eliminate phone number formatting errors, prevent categorical spelling discrepancies (blood groups/departments), intercept duplicate patient records, and prevent accidental data loss.

### 2. DO
- **Poka-Yoke Input Masking:** Engineered `PhoneMaskEntry` (`src/widgets/phone_mask_entry.py`) to enforce `+91-XXXXX-XXXXX` format and reject non-digit keystrokes.
- **Dropdown List Enforcement:** Replaced all vulnerable text inputs with read-only `Combobox` widgets bound to centralized configuration lists in `src/config.py` for Gender, Blood Group, Department, Shift, and Payment methods.
- **Auto-Complete Lookup:** Built `AutocompleteEntry` (`src/widgets/autocomplete_entry.py`) dynamically querying patient names during registration, appointments, and billing.
- **Confirmation Modals:** Integrated `ConfirmDialog` (`src/widgets/confirm_dialog.py`) requiring explicit modal confirmation before any `UPDATE` or `DELETE`.
- **Immutable Audit Logging:** Activated `log_audit()` across all 8 data models, writing transaction metadata to `audit_log` in SQLite and `TQM/data/audit_logs.csv`.

### 3. CHECK
- Re-tested with a simulated batch of 20 patient registrations and 15 appointment bookings:
  - Phone format errors dropped from 5 logged instances to **0**.
  - Categorical typos dropped to **0**.
  - 1 duplicate patient registration attempt was intercepted in real-time by autocomplete before submission.
  - 100% of database mutations were verified captured in the audit log with accurate timestamps.
- **FMEA Verification:** Post-mitigation assessment recalculated the Risk Priority Number (RPN) for phone errors from **280 to 5** (>98% risk reduction) and blood group errors from **378 to 9**.

### 4. ACT
- **Standardization:** Adopted the Q07 widget and validation pattern as the mandatory architecture standard for all existing and future modules in the HMS application.
- **Continuous Maintenance:** Established automated unit tests (`tests/test_validators.py` and `tests/test_tqm_services.py`) to prevent regression in continuous integration.

---

## Defect Trend Analysis (Review 4 Evaluation Metric)

| Metric / Defect Mode | Pre-Control Status (Baseline) | Post-Control Status (After Q07) | Improvement (% Reduction) |
|---|:---:|:---:|:---:|
| Malformed Phone Numbers | 5 defects logged | 0 | **100% Reduction** |
| Free-text Typographical Errors | 2 defects logged | 0 | **100% Reduction** |
| Duplicate Patient Charts Created | Uncontrolled duplicates | 0 (caught pre-submit) | **100% Intercepted** |
| Accidental Record Deletions | 1 critical defect logged | 0 (modal blocked) | **100% Eliminated** |
| Untraceable Record Mutations | 100% untracked | 0% (all logged) | **100% Traceability** |
| Overall RPN (Top Failure Mode) | **280** | **5** | **98.2% Risk Reduction** |
