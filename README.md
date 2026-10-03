# Hospital Management System — TQM Project

**Student:** Ajay Bora
**Branch:** CSE — Section B
**Course:** BBAT104 — Fundamentals of Total Quality Management
**Academic Session:** 2026–27
**Repository:** `TQM-Hospital-Management-System`

---

## Assigned Project

| Item | Details |
|---|---|
| Baseline System | Hospital Management System |
| Roll No. Digit | 2 |
| Assigned Quality Goal | **Q07 — Improve Data Accuracy** |
| Q07 Features Implemented | Input Masking · Dropdown Lists · Auto-Complete · Confirmation Modals · Audit Logs |

---

## TQM Approach

**Prevent → Validate → Confirm → Log → Analyze → Improve**

Quality is built into every data entry point using **Poka-Yoke (mistake-proofing)** rather than corrected after the fact. The five Q07 features are implemented once as reusable widgets and applied consistently across all eight data-entry modules.

---

## How to Run

```bash
# 1. Install SQC and Excel dependencies
pip install -r requirements.txt

# 2. Launch the application (database auto-created on first run)
python src/main.py

# 3. Run unit tests (uses a throwaway database, never touches hms.db)
python tests/test_db.py

# 4. Regenerate SQC charts from defect data
python sqc/pareto_chart.py
python sqc/fishbone_diagram.py

# 5. Regenerate FMEA Excel workbook
python docs/build_fmea.py
```

---

## System Modules

| Tab | Model | Core Purpose |
|---|---|---|
| Dashboard | All tables | Live counts — patients, doctors, appointments, available rooms, unpaid bills, defects, audit entries |
| Patients | `models/patient.py` | Register / update / delete patients with optional room assignment |
| Doctors | `models/doctor.py` | Doctor roster by department |
| Appointments | `models/appointment.py` | Schedule appointments linking a patient and a consulting doctor |
| Rooms / Wards | `models/room.py` | Room inventory — type, occupancy status, daily rate |
| Staff | `models/staff.py` | Nursing and support staff by role and shift |
| Pharmacy | `models/medicine.py` | Medicine stock with automatic low-stock flagging |
| Billing | `models/bill.py` | Itemized bills with auto-calculated totals and payment tracking |
| Audit Log | `models/audit.py` | Read-only trail of every INSERT, UPDATE, DELETE across all tables |
| Defect Checksheet | `models/audit.py` | Quality defect log that feeds the Pareto analysis |

---

## Q07 Feature Implementation

Each feature is written once and reused across every relevant module.

| # | Feature | File | How It Works |
|---|---|---|---|
| 1 | **Input Masking** | `src/widgets/phone_mask_entry.py` | Subclass of `ttk.Entry`; traces `StringVar` on every keystroke, strips non-digits with `re.sub`, enforces `+91-XXXXX-XXXXX` format, caps at 10 digits |
| 2 | **Dropdown Lists** | `src/config.py` + `ttk.Combobox(state="readonly")` | All categorical fields (Gender, Blood Group, Department, Status, Role, Shift, Payment) are bound to fixed lists defined once in `config.py` — free-text entry is not possible |
| 3 | **Auto-Complete** | `src/widgets/autocomplete_entry.py` | Queries `patient.name_candidates(prefix)` on every keystroke; shows a floating `Listbox` of matches; fires `on_select` callback to prevent new duplicate records |
| 4 | **Confirmation Modals** | `src/widgets/confirm_dialog.py` | `confirm_delete()` and `confirm_update()` wrap `messagebox.askyesno()`; every view checks the boolean return before executing any destructive database operation |
| 5 | **Audit Logs** | `src/database/db_manager.log_audit()` | Called inside every model write function in the same transaction; records `table_name`, `record_id`, `action (INSERT/UPDATE/DELETE)`, `details`, and `timestamp`; readable in the Audit Log tab |

---

## Project Structure

```
HMS_Project/
├── README.md
├── requirements.txt
├── .gitignore
│
├── src/
│   ├── main.py                    # Entry point — HMSApp(tk.Tk), wires all 10 tabs
│   ├── config.py                  # All dropdown lists + app constants (single source of truth)
│   │
│   ├── database/
│   │   └── db_manager.py          # SQLite schema, get_connection(), init_db(), log_audit()
│   │
│   ├── models/                    # Data-access layer — pure SQL, no Tkinter imports
│   │   ├── patient.py
│   │   ├── doctor.py
│   │   ├── appointment.py
│   │   ├── room.py
│   │   ├── staff.py
│   │   ├── medicine.py
│   │   ├── bill.py
│   │   └── audit.py               # audit_log reads + defect_log CRUD
│   │
│   ├── widgets/                   # Q07 reusable controls — written once, imported everywhere
│   │   ├── phone_mask_entry.py    # Feature 1: Input Masking
│   │   ├── autocomplete_entry.py  # Feature 3: Auto-Complete
│   │   └── confirm_dialog.py      # Feature 4: Confirmation Modals
│   │
│   ├── views/                     # UI tabs — no raw SQL, only model calls
│   │   ├── dashboard_view.py
│   │   ├── patients_view.py
│   │   ├── doctors_view.py
│   │   ├── appointments_view.py
│   │   ├── rooms_view.py
│   │   ├── staff_view.py
│   │   ├── medicines_view.py
│   │   ├── billing_view.py
│   │   ├── audit_view.py          # Feature 5: Audit Log viewer (read-only)
│   │   └── defects_view.py        # Defect Checksheet UI
│   │
│   └── utils/
│       └── validators.py          # Shared date, time, phone, and field validation rules
│
├── docs/
│   ├── SRS.md                     # Software Requirements Specification
│   ├── SRS_HMS_AjayBora.docx      # Formal SRS document
│   ├── architecture.md            # Full layer diagram and file-by-file responsibilities
│   ├── architecture.png           # System architecture flowchart image
│   ├── ER_Diagram.md              # Entity-relationship diagram (Mermaid)
│   ├── sipoc_diagram.png          # SIPOC process map image
│   ├── FMEA_RiskAudit.xlsx        # FMEA matrix with formula-driven RPN scores
│   ├── build_fmea.py              # Regenerates FMEA_RiskAudit.xlsx
│   ├── project_overview.md        # Project info table and objective
│   ├── quality_objectives.md      # Measurable quality objectives
│   └── testing.md                 # Testing strategy and test record format
│
├── TQM/                           # TQM documentation
│   ├── assigned_quality_goal.md
│   ├── customer_requirements.md
│   ├── quality_features.md
│   ├── CTQ_Tree.md
│   ├── SIPOC.md
│   ├── FMEA.md
│   ├── Pareto.md
│   ├── Fishbone.md
│   ├── PDCA.md
│   ├── error_prevention.md
│   ├── process_control.md
│   ├── process_map.md
│   ├── quality_monitoring.md
│   └── requirements_traceability.md
│
├── sqc/
│   ├── pareto_chart.py            # 80/20 defect frequency analysis
│   ├── pareto_chart.png           # Generated Pareto chart
│   ├── fishbone_diagram.py        # Ishikawa root-cause diagram generator
│   └── fishbone_diagram.png       # Generated Fishbone diagram
│
└── tests/
    └── test_db.py                 # 10 unit tests across all models (no GUI required)
```

---

## Design Rules

1. **Models never import Tkinter.** All SQL lives in `src/models/` only.
2. **Views never run raw SQL.** Data access always goes through a model function.
3. **Widgets are written once.** `PhoneMaskEntry`, `AutocompleteEntry`, and `confirm_dialog` are defined once and imported wherever needed — not duplicated per form.
4. **Dropdowns are defined once.** All fixed value lists live in `src/config.py`.
5. **`log_audit()` is called inside the model, not the view.** The audit trail cannot be bypassed by a view that forgets to call it.

---

## TQM Deliverables Map

| Review | Requirement | Files |
|---|---|---|
| Review 1 | SRS, Architecture, Scope | `docs/SRS.md`, `docs/SRS_HMS_AjayBora.docx`, `docs/architecture.md`, `docs/architecture.png` |
| Review 2 | Base CRUD + 5 Q07 Features | `src/` — all models and views; `tests/test_db.py` |
| Review 3 | FMEA + SIPOC + CTQ + Defect Logging | `TQM/FMEA.md`, `docs/FMEA_RiskAudit.xlsx`, `TQM/SIPOC.md`, `TQM/CTQ_Tree.md`, `docs/sipoc_diagram.png` |
| Review 4 | Pareto + Fishbone + Checksheets + PDCA | `sqc/pareto_chart.py/.png`, `sqc/fishbone_diagram.py/.png`, `TQM/PDCA.md` |
| Demo & Viva | Live demonstration | Run `src/main.py`; walk through all 10 tabs and each Q07 feature |
| GitHub Health | README, ≥30 commits | This file; commit history on `main` branch |

---

## Repository Principle

> Data accuracy must be built into the entry process, not corrected after the fact.
