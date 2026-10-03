# PDCA (Plan-Do-Check-Act) Cycle Log
**Project:** Hospital Management System | **Quality Goal:** Q07 - Improve Data Accuracy
**Student:** Ajay Bora | CSE - B

This log records one full continuous-improvement cycle driven by the Pareto and Fishbone
analysis in `sqc/`, satisfying Review 4 (Step 6).

---

## Cycle 1 — Data Entry Accuracy

**PLAN**
- Pareto analysis showed **Data Entry** defects (5 of 11 logged, ~45%) as the leading category,
  followed by **Validation** and **UI** — together the "vital few" crossing the 80% line.
- Fishbone analysis traced the root causes to: free-text fields, no input masking, no
  validation regex, and no standardized entry SOP (see `sqc/fishbone_diagram.png`).
- **Target:** eliminate malformed phone numbers, invalid gender/blood-group values, and
  duplicate patient records.

**DO**
- Implemented `PhoneMaskEntry` widget — auto-formats to `+91-XXXXX-XXXXX`, rejects non-digits.
- Replaced free-text Gender/Blood Group/Department/Status fields with read-only `Combobox`
  dropdowns bound to a fixed value list.
- Implemented `AutocompleteEntry` on the patient search/appointment-booking screens to
  surface existing matches before a new record is created.
- Added `messagebox.askyesno` confirmation prompts before every Update/Delete.
- Added `audit_log` table + Audit Log viewer tab logging every INSERT/UPDATE/DELETE.

**CHECK**
- Re-ran the defect checksheet after deployment on 5 test users (front-desk simulation):
  phone-format defects dropped to 0/20 new entries; gender/blood-group typos dropped to 0/20;
  1 duplicate patient attempt was caught by auto-complete before submission.
- Audit log confirmed 100% of test CRUD actions were captured with timestamp and action type.
- FMEA Detection scores improved for the "Digits mistyped" and "Free-text typo" failure modes
  once controls were added (see `docs/FMEA_RiskAudit.xlsx`).

**ACT**
- Standardized the dropdown + masking + auto-complete + confirm + audit pattern as the default
  for any new data-entry field added to the system going forward.
- Next cycle candidate (not yet implemented): extend auto-complete/duplicate-check to the
  Doctor registration screen, and add DOB masking (currently regex-validated only).

---

## Defect Trend (for Review 4 discussion)
| Metric | Before Q07 features | After Q07 features (test batch) |
|---|---|---|
| Malformed phone entries | 5 logged | 0 |
| Free-text field typos | 2 logged | 0 |
| Duplicate patient attempts reaching DB | Not tracked | 0 (1 caught pre-submit) |
| Accidental deletes | 1 logged (Critical severity) | 0 (confirmation modal blocks) |
| Untraceable data changes | 100% before audit log | 0% (all logged) |
