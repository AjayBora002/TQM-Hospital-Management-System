# Software Features to TQM Principles Mapping
**Project:** Hospital Management System (HMS)  
**Quality Focus:** Q07 -- Improve Data Accuracy  
**Author:** Ajay Bora  

---

## 1. Traceability Matrix: HMS Features to TQM Core Principles

| HMS Module / Feature | TQM Core Principle | Specific Mechanism Applied | Quality Metric / Target |
| :--- | :--- | :--- | :--- |
| **Patient Registration & Intake** | Poka-Yoke (Mistake Proofing) | Strictly enumerated blood groups, ISO-8601 DOB check, regex 10-digit phone validator, duplicate detection. | Data entry validation error rate < 0.5% |
| **Doctor Appointment Scheduling** | Zero Defects (Crosby) | Foreign key patient/doctor binding, scheduled status state machine, conflict checking. | Zero orphaned appointments or scheduling collisions |
| **Ward & Room Allocation** | Process Control (Deming) | Real-time status toggle (`Available` vs `Occupied`), unique room numbering constraint. | 100% room occupancy consistency |
| **Pharmacy Inventory & Dispensing** | Just-in-Time (JIT) & 5S | Stock levels tracking, automated low-stock warnings (`stock_qty <= reorder_level`), price constraints. | Zero unrecorded medicine stock adjustments |
| **Billing & Invoicing** | Continuous Quality Improvement | Server-side automated total arithmetic (`room + consult + meds = total`), non-negative amount assertions. | Zero manual calculation discrepancies |
| **Dual-Tier Audit Logging** | Total Accountability | Automated capture of every INSERT / UPDATE / DELETE into SQLite DB + append to `TQM/data/audit_logs.csv`. | 100% audit trail coverage for all mutations |
| **Defect Checksheet & Pareto** | Statistical Quality Control (SQC) | Categorization of user/system exceptions into `TQM/data/checksheet.csv` for Pareto 80/20 root cause analysis. | Systematic defect resolution targeting the vital few |
| **Exception Handling Decorators** | Fail-Safe Design | `@safe_operation` wraps system workflows to intercept crashes and document stack traces in `error_logs.csv`. | Zero unhandled runtime crash states |

---

## 2. Deming's 14 Points Alignment in HMS

1. **Point 1 (Constancy of Purpose)**: Continuous focus on patient data fidelity and healthcare administrative reliability.
2. **Point 5 (Improve Constantly & Forever)**: Utilizing Pareto and PDCA feedback to continually tighten validation rules.
3. **Point 8 (Drive Out Fear)**: Confirmation dialogs and intuitive field guidance prevent user hesitation and accidental loss of data.
4. **Point 12 (Pride of Workmanship)**: Clean, responsive user interface ensuring operators can record clinical data accurately and with confidence.
