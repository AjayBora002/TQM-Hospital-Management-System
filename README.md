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
| Assigned Quality Goal | **Q07 — Improve Data Accuracy** |
| Q07 Features Implemented | Input Masking · Dropdown Lists · Auto-Complete · Confirmation Modals · Audit Logs |

---

## TQM Approach

**Prevent → Validate → Confirm → Log → Analyze → Improve**

Quality is built into every data entry point using **Poka-Yoke (mistake-proofing)** rather than corrected after the fact. The five Q07 features are implemented once as reusable widgets and applied consistently across all eight data-entry modules.

---

## How to Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Launch the Desktop GUI (Tkinter - Primary Syllabus Deliverable)
python run.py
# (Or directly via: python src/main.py)

# 3. (Optional) Launch Web Portal Demo
python run.py --web
# Opens http://127.0.0.1:5000 in your browser

# 4. Run automated test suite (31 tests covering CRUD, Validators, TQM logging, Web API & Clinical Poka-Yoke)
python -m unittest discover tests

# 5. Regenerate SQC Pareto & Fishbone charts
python sqc/pareto_chart.py
python sqc/fishbone_diagram.py

# 6. Regenerate FMEA Excel workbook
python docs/build_fmea.py
```

---

## System Modules

| Tab / Route | Model | Core Purpose |
|---|---|---|
| Dashboard | All tables | Live counts — patients, doctors, appointments, available rooms, unpaid bills, defects, audit entries |
| Patients | `models/patient.py` | Register / update / delete patients with allergy documentation, vitals, and bed management |
| Doctors | `models/doctor.py` | Doctor roster grouped by clinical specialty department |
| Appointments | `models/appointment.py` | Schedule appointments with automated slot conflict prevention & free slot lookup |
| Rooms / Wards | `models/room.py` | Room inventory — type, occupancy status, daily rate, bed clearance |
| Staff | `models/staff.py` | Nursing and support staff by role and shift |
| Pharmacy | `models/medicine.py` | Medicine stock with automated low-stock threshold flagging |
| Billing | `models/bill.py` | Itemized bills with auto-calculated charges and payment tracking |
| Audit Log | `models/audit.py` | Immutable trail of every INSERT, UPDATE, DELETE across all tables |
| Defect Checksheet | `models/audit.py` | Quality defect checksheet feeding the Pareto 80/20 analysis |

---

## Q07 Feature Implementation (Poka-Yoke & Clinical Safety)

Quality is enforced through Poka-Yoke mistake-proofing across both Desktop GUI and Web Application interfaces:

| # | Feature | Desktop GUI (Tkinter) | Web Portal (Flask / JS) | How It Works & Poka-Yoke Impact |
|---|---|---|---|---|
| 1 | **Input Masking** | `src/widgets/phone_mask_entry.py` | `src/static/js/app.js` | Enforces `+91-XXXXX-XXXXX` on every keystroke, strips non-digit characters via regex, and caps at 10 digits |
| 2 | **Dropdown Lists** | `src/config.py` + `ttk.Combobox(state="readonly")` | HTML `<select>` validated against `src/config.py` | Categorical values (Gender, Blood Group, Department, Status, Role, Shift, Payment, Allergies) are strictly locked to standard sets |
| 3 | **Auto-Complete** | `src/widgets/autocomplete_entry.py` | Dynamic debounce search in `app.js` + `/api/patients/search` | Real-time substring query surfaces existing patient records as user types, preventing accidental duplicate patient charts |
| 4 | **Confirmation Modals** | `src/widgets/confirm_dialog.py` | Custom async modal dialogs in `app.js` | Critical UPDATE and DELETE operations require explicit two-step user confirmation before database execution |
| 5 | **Audit Logs** | `db_manager.log_audit()` + `audit_view.py` | Dual-tier logging (`db_manager` + `logging_service.py`) | Atomic transactional logging of `table_name`, `record_id`, `action`, `details`, and `timestamp` across SQLite & CSV trails |
| 6 | **Schedule Conflict Prevention** | `src/models/appointment.py` (`has_conflict`) | Real-time pre-flight checker + Slot Picker in `app.js` | Blocks doctor double-booking and patient time slot clashes with HTTP 409 conflict safeguards |
| 7 | **Drug Allergy Safety (ADR)** | `src/utils/validators.py` | Patient allergy badges + Pre-flight contraindication API | Checks patient allergy history against prescribed medicine classes to prevent adverse drug reactions |
| 8 | **Triage Vitals Validation** | `src/models/patient.py` (`record_vitals`) | Boundary checks in `validators.py` | Validates BP, pulse, temp, SpO2 against physiological limits and automatically flags critical triage severity |

---

## Project Structure

```
HMS_Project/
├── run.py                         # Web Application launcher & port configuration
├── README.md                      # Project documentation and guide
├── requirements.txt               # Python project dependencies
├── .gitignore                     # Git ignore rules
│
├── src/
│   ├── main.py                    # Entry point — Native Desktop GUI (Tkinter, 10 tabs)
│   ├── web_app.py                 # Entry point — Flask Web Application & Blueprint router
│   ├── config.py                  # All dropdown lists + app constants (single source of truth)
│   │
│   ├── api/                       # Modular REST API Blueprints for Web Portal
│   │   ├── patients.py            # Patient CRUD & autocomplete API
│   │   ├── doctors.py             # Doctor roster API
│   │   ├── appointments.py        # Appointment scheduling API
│   │   ├── rooms.py               # Ward & bed inventory API
│   │   ├── staff.py               # Staff administration API
│   │   ├── medicines.py           # Pharmacy & low-stock API
│   │   ├── bills.py               # Billing & itemized invoicing API
│   │   ├── audit.py               # Audit trail viewer API
│   │   ├── dashboard.py           # Live KPI counters API
│   │   └── helpers.py             # API utilities & response helpers
│   │
│   ├── templates/                 # Jinja2 HTML templates for Web Application
│   │   └── index.html             # Responsive Single-Page Application interface
│   │
│   ├── static/                    # Responsive UI assets (Vanilla CSS & JS)
│   │   ├── css/
│   │   │   └── style.css          # Modern dark/light design system
│   │   └── js/
│   │       └── app.js             # Client-side validation, input masking & async REST client
│   │
│   ├── database/
│   │   └── db_manager.py          # SQLite schema, connection pool, init_db(), log_audit()
│   │
│   ├── models/                    # Data-access layer — pure SQL, framework-agnostic
│   │   ├── patient.py
│   │   ├── doctor.py
│   │   ├── appointment.py
│   │   ├── room.py
│   │   ├── staff.py
│   │   ├── medicine.py
│   │   ├── bill.py
│   │   └── audit.py               # audit_log reads + defect_log CRUD
│   │
│   ├── widgets/                   # Q07 Desktop GUI widgets (Tkinter)
│   │   ├── phone_mask_entry.py    # Feature 1: Input Masking
│   │   ├── autocomplete_entry.py  # Feature 3: Auto-Complete
│   │   └── confirm_dialog.py      # Feature 4: Confirmation Modals
│   │
│   ├── views/                     # Native Desktop GUI tabs (Tkinter)
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
│   └── utils/                     # Shared cross-cutting utilities
│       ├── validators.py          # Shared date, time, phone, and field validation rules
│       ├── logging_service.py     # Dual-tier logging service (SQLite + CSV)
│       └── exception_handler.py   # Global exception management & error logging
│
├── docs/
│   ├── SRS.md                     # Software Requirements Specification
│   ├── SRS_HMS_AjayBora.docx      # Formal SRS document
│   ├── architecture.md            # Full layer diagram and file-by-file responsibilities
│   ├── architecture.png           # System architecture flowchart image
│   ├── USER_MANUAL.md             # Comprehensive User and Operations Manual
│   ├── GITHUB_ISSUES.md           # Defect register mapped to checksheets & commits
│   ├── ER_Diagram.md              # Entity-relationship diagram (Mermaid)
│   ├── sipoc_diagram.png          # SIPOC process map image
│   ├── FMEA_RiskAudit.xlsx        # FMEA matrix with formula-driven RPN scores
│   ├── build_fmea.py              # Regenerates FMEA_RiskAudit.xlsx
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
│   ├── requirements_traceability.md
│   ├── software_features_tqm_mapping.md
│   └── data/                      # TQM SQC CSV Datasets & Audits
│       ├── audit_logs.csv
│       ├── checksheet.csv
│       ├── error_logs.csv
│       ├── process_metrics.csv
│       └── quality_metrics.csv
│
├── sqc/
│   ├── pareto_chart.py            # 80/20 defect frequency analysis
│   ├── pareto_chart.png           # Generated Pareto chart
│   ├── fishbone_diagram.py        # Ishikawa root-cause diagram generator
│   └── fishbone_diagram.png       # Generated Fishbone diagram
│
└── tests/                         # 31 automated unit & integration tests
    ├── test_db.py                 # Data access layer & CRUD tests
    ├── test_validators.py         # Input validation & boundary condition tests
    ├── test_tqm_services.py       # Dual-tier logging and exception handling tests
    ├── test_web_app.py            # Web application endpoints & static asset tests
    └── test_clinical_poka_yoke.py # Schedule conflict, allergy safety & triage vitals tests
```

---

## Evaluation Deliverables & Marking Scheme (70 Raw Marks)

| Milestone / Deliverable | Max Marks | Mapped COs | Required Artefacts & Submission Files | Status |
|---|:---:|:---:|---|:---:|
| **Review 1: Setup & SRS** | 10 Marks | CO1 | GitHub repo initialized, System Architecture Flowchart (`docs/architecture.png`, `docs/architecture.md`), SRS document (`docs/SRS.md`, `docs/SRS_HMS_AjayBora.docx`), Scope definition. | Completed |
| **Review 2: Base System & CRUD** | 15 Marks | CO1, CO2 | 8 Core CRUD modules + 5 assigned Q07 features (Input Masking, Dropdown Lists, Auto-Complete, Confirmation Modals, Audit Logs). Verified via `tests/test_db.py` & web portal. | Completed |
| **Review 3: FMEA & Risk Audit** | 15 Marks | CO2 | Formula-driven FMEA Matrix with RPN calculations (`docs/FMEA_RiskAudit.xlsx`, `TQM/FMEA.md`), SIPOC Process Map (`TQM/SIPOC.md`, `docs/sipoc_diagram.png`), CTQ Tree (`TQM/CTQ_Tree.md`), Defect Checksheet (`TQM/data/checksheet.csv`). | Completed |
| **Review 4: SQC & Continuous Improvement** | 15 Marks | CO2, CO3 | Pareto Chart with 80/20 analysis (`sqc/pareto_chart.png`, `TQM/Pareto.md`), Ishikawa Fishbone Root-Cause Diagram (`sqc/fishbone_diagram.png`, `TQM/Fishbone.md`), PDCA continuous improvement cycle log (`TQM/PDCA.md`). | Completed |
| **Final Demonstration & Viva** | 10 Marks | CO3 | Live software demonstration (Web Portal `python run.py` / Desktop GUI `python src/main.py`), bug-handling defense, oral viva defense on TQM tools selection. | Ready |
| **Documentation & GitHub Health** | 5 Marks | CO3 | Comprehensive `README.md`, User & Operations Manual (`docs/USER_MANUAL.md`), ≥30 meaningful commit history (>50 commits), Defect Register / GitHub Issues (`docs/GITHUB_ISSUES.md`). | Completed |
| **Total Assessment** | **70 Marks** | **CO1, CO2, CO3** | All 4 reviews, live demonstration, and documentation artifacts fully synchronized. | **100% Complete** |

---

## Architectural Design Rules

1. **Models never import UI frameworks.** All SQL lives exclusively in `src/models/`.
2. **Views never execute raw SQL.** Data access always goes through validated model functions.
3. **Poka-Yoke widgets are written once.** `PhoneMaskEntry`, `AutocompleteEntry`, and `ConfirmDialog` are centralized in `src/widgets/` and imported everywhere.
4. **Categorical dropdowns are single-source.** All fixed value lists live in `src/config.py`.
5. **Atomic audit logging.** `log_audit()` is called inside the model within the database transaction, preventing unlogged side-effects.

---

## Repository Principle

> Data accuracy must be built into the entry process, not corrected after the fact.
