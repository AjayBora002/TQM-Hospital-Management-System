# Assigned Quality Goal

## Q07 — Improve Data Accuracy

**Course Guideline Reference:** BBAT104 Quality Goal Matrix, Q07.

Hospital Management Systems are especially sensitive to data inaccuracy. An incorrect blood group or misidentified patient can cause clinical harm. A malformed phone number prevents emergency contact. A duplicate patient record fragments the medical history.

Q07 targets these problems by building accuracy controls directly into every data entry point.

## Five Required Features

| ID | Feature | Implementation |
|---|---|---|
| QF-01 | Input Masking | `src/widgets/phone_mask_entry.py` — enforces `+91-XXXXX-XXXXX` format |
| QF-02 | Dropdown Lists | `src/config.py` + `ttk.Combobox(state="readonly")` |
| QF-03 | Auto-Complete | `src/widgets/autocomplete_entry.py` — live patient name matching |
| QF-04 | Confirmation Modals | `src/widgets/confirm_dialog.py` — explicit confirm before Update/Delete |
| QF-05 | Audit Logs | `src/database/db_manager.log_audit()` + `src/views/audit_view.py` |

## TQM Principle Applied

**Poka-Yoke (Mistake-Proofing):** Errors are prevented at the point of entry, not corrected after the fact.
