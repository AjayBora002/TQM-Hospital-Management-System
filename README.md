# BBAT104 — TQM Course Project
## Hospital Management System | Quality Goal Q07: Improve Data Accuracy

**Student:** Ajay Bora &nbsp;|&nbsp; **Branch:** CSE &nbsp;|&nbsp; **Section:** B
**Baseline System:** Hospital Management System
**Quality Goal:** Q07 — Improve Data Accuracy
**Q07 Features (5/5):** Input Masking · Dropdown Lists · Auto-Complete · Confirmation Modals · Audit Logs

A full hospital-management desktop app — Patients, Doctors, Appointments, Rooms/Wards,
Staff, Pharmacy/Inventory, Billing, an Audit Log and a Defect Checksheet — built on a clean,
layered architecture so each Q07 feature is written **once** and reused everywhere it applies.

---

## 1. Folder Architecture
```
HMS_Project/
├── README.md
├── requirements.txt
├── .gitignore
│
├── src/                          # Application source
│   ├── main.py                    # Entry point — builds the window, wires up every tab
│   ├── config.py                  # ALL fixed dropdown lists + app constants (single source of truth)
│   │
│   ├── database/
│   │   └── db_manager.py          # SQLite connection + full schema + log_audit() helper
│   │
│   ├── models/                    # Data-access layer — one file per entity, no UI code
│   │   ├── patient.py
│   │   ├── doctor.py
│   │   ├── appointment.py
│   │   ├── room.py                 # Rooms / Wards
│   │   ├── staff.py
│   │   ├── medicine.py             # Pharmacy / Inventory
│   │   ├── bill.py                 # Billing / Invoicing
│   │   └── audit.py                # audit_log reads + defect_log CRUD
│   │
│   ├── widgets/                   # Reusable Q07 feature widgets (built once, imported everywhere)
│   │   ├── phone_mask_entry.py     # Feature 1: Input Masking
│   │   ├── autocomplete_entry.py   # Feature 3: Auto-Complete
│   │   └── confirm_dialog.py       # Feature 4: Confirmation Modals
│   │
│   ├── views/                     # UI layer — one Tkinter tab per module
│   │   ├── dashboard_view.py       # At-a-glance stats across every module
│   │   ├── patients_view.py
│   │   ├── doctors_view.py
│   │   ├── appointments_view.py
│   │   ├── rooms_view.py
│   │   ├── staff_view.py
│   │   ├── medicines_view.py
│   │   ├── billing_view.py
│   │   ├── audit_view.py           # Feature 5: Audit Logs (read-only viewer)
│   │   └── defects_view.py         # Defect Checksheet (feeds sqc/pareto_chart.py)
│   │
│   └── utils/
│       └── validators.py          # Shared date/time/phone/field validation rules
│
├── docs/                          # Review 1, 2, 3 deliverables
│   ├── SRS_HMS_AjayBora.docx       # Software Requirements Specification
│   ├── architecture.png            # System architecture flowchart
│   ├── sipoc_diagram.png           # SIPOC process map
│   ├── build_fmea.py               # Regenerates the FMEA workbook
│   ├── FMEA_RiskAudit.xlsx         # FMEA matrix (formula-driven RPN) + Defect Checksheet tab
│   └── PDCA_Log.md                 # Plan-Do-Check-Act continuous-improvement cycle
│
├── sqc/                           # Review 4 deliverables (Statistical Quality Control)
│   ├── pareto_chart.py / .png      # 80/20 defect analysis
│   └── fishbone_diagram.py / .png  # Ishikawa root-cause diagram
│
└── tests/
    └── test_db.py                 # Unit tests for the model/data-access layer
```

**Why this layout:** `models/` never imports `tkinter`, and `views/` never runs raw SQL —
each view calls its matching model function. That split is what let every Q07 feature be
written exactly once (in `widgets/`) and reused across all eight data-entry modules, instead
of being copy-pasted eight times with eight chances to drift out of sync.

## 2. Setup & Run
```bash
pip install -r requirements.txt     # only needed for docs/sqc scripts; app itself uses stdlib only
python src/main.py                  # launches the GUI; src/database/hms.db is auto-created
python -m pytest tests/             # or: python tests/test_db.py
```

## 3. Modules at a Glance
| Tab | Model | Purpose |
|---|---|---|
| Dashboard | (reads all tables) | Live counts: patients, doctors, rooms, bills, defects, audit entries |
| Patients | `models/patient.py` | Register/update/delete patients; optional room assignment |
| Doctors | `models/doctor.py` | Doctor roster by department |
| Appointments | `models/appointment.py` | Book/update/cancel appointments linking a patient + doctor |
| Rooms / Wards | `models/room.py` | Room inventory: type, occupancy status, daily rate |
| Staff | `models/staff.py` | Nurses, receptionists, pharmacists, etc. by role & shift |
| Pharmacy | `models/medicine.py` | Medicine stock, pricing, reorder-level flagging |
| Billing | `models/bill.py` | Generate itemized bills, track payment status |
| Audit Log | `models/audit.py` | Read-only trail of every INSERT/UPDATE/DELETE, any table |
| Defect Checksheet | `models/audit.py` | Logs defects found during testing — feeds the Pareto chart |

## 4. Q07 Feature Map (built once, reused everywhere)
| # | Feature | Implementation | Used in |
|---|---|---|---|
| 1 | **Input Masking** | `widgets/phone_mask_entry.py` — auto-formats to `+91-XXXXX-XXXXX`, blocks non-digits | Patients, Doctors, Staff |
| 2 | **Dropdown Lists** | Fixed lists in `config.py` + `ttk.Combobox(state="readonly")` | Gender, Blood Group, Department, Appt Status, Room Type/Status, Staff Role/Shift, Medicine Category, Payment Method/Status |
| 3 | **Auto-Complete** | `widgets/autocomplete_entry.py` — suggests existing names while typing | Patient search, Appointment booking, Billing |
| 4 | **Confirmation Modals** | `widgets/confirm_dialog.py` — shared `confirm()/confirm_delete()/confirm_update()` | Every Update/Delete across all 8 modules |
| 5 | **Audit Logs** | `database/db_manager.log_audit()` inside every model's write call + `views/audit_view.py` | All CRUD across all 8 modules |

## 5. TQM / SQC Deliverables Map
| Review | Guideline requirement | File(s) |
|---|---|---|
| Review 1 | SRS, Architecture Flowchart, Scope | `docs/SRS_HMS_AjayBora.docx`, `docs/architecture.png` |
| Review 2 | Base CRUD + 5 Q07 features | `src/` (all modules) |
| Review 3 | FMEA + SIPOC + CTQ + Defect Logging | `docs/FMEA_RiskAudit.xlsx`, `docs/sipoc_diagram.png`, SRS §3 |
| Review 4 | Pareto, Fishbone, Checksheets, PDCA | `sqc/pareto_chart.png`, `sqc/fishbone_diagram.png`, `docs/PDCA_Log.md` |
| Demo & Viva | Live demo + defense | Run `src/main.py`; walk through each Q07 feature + Audit Log + Dashboard |
| GitHub Health | README, ≥30 commits, Issues | This file; see commit cadence below |

## 6. Suggested GitHub Commit Cadence (≥30 commits)
1. `Init repo scaffold + README + .gitignore`
2. `Add config.py (dropdown lists) + database schema`
3. `Add patient model + Patients tab`
4. `Add PhoneMaskEntry widget (Input Masking)`
5. `Add doctor model + Doctors tab`
6. `Add appointment model + Appointments tab`
7. `Add AutocompleteEntry widget (Auto-Complete)`
8. `Add room model + Rooms/Wards tab`
9. `Add staff model + Staff tab`
10. `Add medicine model + Pharmacy tab`
11. `Add bill model + Billing tab`
12. `Add confirm_dialog widget (Confirmation Modals) across all tabs`
13. `Add audit log + Audit Log tab (Audit Logs feature)`
14. `Add defect checksheet model + Defect Checksheet tab`
15. `Add Dashboard tab`
16. `Add unit tests (tests/test_db.py)`
17. `Add SRS document + architecture diagram`
18. `Add FMEA matrix + SIPOC diagram`
19. `Add Pareto chart + Fishbone diagram scripts`
20. `Add PDCA log`
21+ incremental bugfix commits — open a GitHub Issue per logged defect and close it in the
fixing commit (e.g. `Fixes #4: reject non-digit phone input`).

## 7. Step-by-Step Guideline Coverage
- **Step 1** — This README + clean repo scaffold. ✅
- **Step 2** — `docs/SRS_HMS_AjayBora.docx`, `docs/architecture.png`, CTQ table in SRS §3. ✅
- **Step 3** — `src/models/` + `src/views/` implement full CRUD for every module. ✅
- **Step 4** — All 5 Q07 features implemented once in `src/widgets/` and reused everywhere (§4). ✅
- **Step 5** — `docs/sipoc_diagram.png` + `docs/FMEA_RiskAudit.xlsx` (formula-driven RPN). ✅
- **Step 6** — `docs/FMEA_RiskAudit.xlsx` "Defect Checksheet" tab + `sqc/pareto_chart.py` +
  `sqc/fishbone_diagram.py` + `docs/PDCA_Log.md`. ✅
- **Step 7** — Commit cadence above; push as you build, not all at once. ⬜
- **Step 8** — Final push + live walkthrough of every module and Q07 feature for the viva;
  be ready to justify FMEA Severity/Occurrence/Detection scores and the Pareto "vital few". ⬜
