# Testing Strategy

Testing is a component of the assigned Q07 — Improve Data Accuracy quality goal.

## Testing Levels

### Unit / Module Testing

All data-access models (patient, doctor, appointment, room, staff, medicine, bill, audit) are tested independently without the GUI using a throwaway SQLite database.

### Validation Testing

Every Q07 input constraint is tested with both valid and invalid inputs to confirm acceptance and rejection behaviour.

### Integration Testing

Interactions between the widget layer, models, and database are tested end-to-end.

### Negative Testing

Invalid inputs and boundary conditions are deliberately tested.

### Regression Testing

Previously fixed defects are retested after relevant code changes.

## Test Record

Each test should record:

- Test ID
- Requirement ID
- Module
- Input
- Expected result
- Actual result
- Status
- Defect ID if applicable

## Test Areas & Coverage Matrix

| Test Suite Domain | Test Suites Count | Scope & Quality Goal | Verification Proof |
|---|:---:|---|---|
| **Base Data Models** | 8 suites | Pure SQL CRUD, foreign keys, cascade constraints | `test_db.py`, `test_staff_doctor_boundaries.py` |
| **Poka-Yoke Validators** | 6 suites | Keystroke phone masking, dropdown restrictions, boundary assertions | `test_validators.py`, `test_patient_boundaries.py` |
| **Clinical Safety & ADR** | 5 suites | Pre-flight drug contraindications, triage vitals boundaries, batch expiry | `test_clinical_poka_yoke.py`, `test_pharmacy_expiry.py` |
| **Diagnostics & Labs** | 3 suites | Reference intervals, automated abnormal flags ($0/1$) | `test_lab_module.py` |
| **Institutional Identity** | 2 suites | Standardized `UHID-2026-XXXXX` zero-padding, timeline aggregation | `test_institutional_uhid.py`, `test_patient_timeline.py` |
| **Process State Machines** | 2 suites | Extended appointment and room state transitions | `test_extended_process_states.py`, `test_room_boundaries.py` |
| **Quality & SQC Analytics** | 4 suites | Shewhart c-chart mathematical limits, Six Sigma DPMO engine, audit dual-sync | `test_spc_chart.py`, `test_six_sigma.py`, `test_quality_audits.py` |

**Total Automated Test Coverage:** **156 unit & integration tests across 30 test suites (100% pass rate).**

## How to Run

```bash
# Execute the complete automated test suite
python -m unittest discover tests
```

Expected result:
```text
Ran 156 tests in ~2.8s
OK
[+] Saved SPC Control Chart: sqc/spc_control_chart.png
[+] Saved SPC Metrics CSV: TQM/data/spc_metrics.csv
```
