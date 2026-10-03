# System Architecture

## Overview

The Hospital Management System is built in three distinct layers — **User Interface**, **Data-Access Models**, and **Database** — with a fourth cross-cutting **Widgets** layer that carries all five Q07 accuracy controls. The strict rule that models never import Tkinter and views never run raw SQL is enforced throughout.

---

## High-Level Layer Diagram

```mermaid
flowchart TD
    U[User / Front-Desk Staff]
    U --> UI[Views Layer\nsrc/views/*.py]

    UI --> W[Q07 Widgets\nsrc/widgets/]
    W --> V[Validators\nsrc/utils/validators.py]

    UI --> M[Models Layer\nsrc/models/*.py]
    M --> DB[(SQLite Database\nsrc/database/hms.db)]
    M --> AL[Audit Logger\ndb_manager.log_audit]]

    DB --> AL
    AL --> AuditTable[(audit_log table)]
    DB --> DefectTable[(defect_log table)]

    DefectTable --> SQC[SQC Scripts\nsqc/]
    AuditTable --> AuditView[Audit Log Tab\nviews/audit_view.py]

    T[Unit Tests\ntests/test_db.py] --> M
```

---

## Q07 Accuracy Control Flow

```text
User Action (e.g. Patient Registration)
    ↓
PhoneMaskEntry (Input Masking)
    → Strips non-digits, enforces +91-XXXXX-XXXXX, caps at 10 digits
    ↓
ttk.Combobox state="readonly" (Dropdown Lists)
    → Gender / Blood Group / Department constrained to fixed lists in config.py
    ↓
AutocompleteEntry (Auto-Complete)
    → Queries patient.name_candidates(prefix) as user types
    → Surfaces existing records before a new one is created
    ↓
Validators (validators.py)
    → is_valid_date(), is_valid_time(), not_empty(), is_valid_phone_digits()
    ↓
confirm_delete() / confirm_update() (Confirmation Modal)
    → messagebox.askyesno() before any UPDATE or DELETE
    ↓
Model function (e.g. patient.add())
    → SQL INSERT/UPDATE/DELETE
    → log_audit() called inside same transaction
    ↓
audit_log table (Audit Logs)
    → table_name, record_id, action, details, performed_by, timestamp
```

---

## File-by-File Responsibilities

### Entry Point

| File | Role |
|---|---|
| `src/main.py` | Creates `HMSApp(tk.Tk)`, calls `init_db()`, assembles all 10 tabs into a `ttk.Notebook`, wires tab-change events to refresh dependent views |
| `src/config.py` | Single source of truth for all fixed dropdown lists (`GENDERS`, `BLOOD_GROUPS`, `DEPARTMENTS`, etc.) and app constants |

### Database Layer

| File | Role |
|---|---|
| `src/database/db_manager.py` | `get_connection()` — returns a `sqlite3.Row`-factory connection with `PRAGMA foreign_keys = ON`; `SCHEMA` — `CREATE TABLE IF NOT EXISTS` for all 9 tables; `init_db()` — runs schema once on first launch; `log_audit()` — shared helper called by every model |

### Q07 Widget Layer

| File | Q07 Feature | Mechanism |
|---|---|---|
| `src/widgets/phone_mask_entry.py` | Feature 1 — Input Masking | Subclasses `ttk.Entry`; `var.trace_add("write")` triggers `_format()` on every keystroke; `re.sub(r"\D","")` strips non-digits; auto-inserts `+91-` prefix and hyphen after 5th digit |
| `src/widgets/autocomplete_entry.py` | Feature 3 — Auto-Complete | Subclasses `ttk.Entry`; calls injected `fetch_candidates(prefix)` callable on each write trace; creates a floating `tk.Listbox` below the field; fires `on_select(value)` callback on pick |
| `src/widgets/confirm_dialog.py` | Feature 4 — Confirmation Modals | Three functions — `confirm()`, `confirm_delete()`, `confirm_update()` — all wrapping `messagebox.askyesno()`; returns `bool`; every view checks the return before proceeding |

### Validation Layer

| File | Role |
|---|---|
| `src/utils/validators.py` | `is_valid_date(v)` — regex `^\d{4}-\d{2}-\d{2}$`; `is_valid_time(v)` — regex `^([01]\d|2[0-3]):[0-5]\d$`; `is_valid_phone_digits(d)` — `len == 10`; `not_empty(v)` — truthy strip; `in_fixed_set(v, allowed)` — membership check |

### Models Layer (Data-Access)

Each model file contains only SQL functions — no Tkinter imports.

| File | Tables | Key Functions |
|---|---|---|
| `src/models/patient.py` | `patients` | `list_all(filter)`, `name_candidates(prefix)`, `get_id_by_name(name)`, `add(...)`, `update(...)`, `delete(id)` |
| `src/models/doctor.py` | `doctors` | `list_all()`, `choices_map()` → `{label: id}` dict for Appointments dropdown, `add()`, `update()`, `delete()` |
| `src/models/appointment.py` | `appointments` | `list_all()` with JOIN on `patients` + `doctors`, `add()`, `update()`, `delete()` |
| `src/models/room.py` | `rooms` | `list_all()`, `choices_map(only_available)`, `add()`, `update()`, `delete()` |
| `src/models/staff.py` | `staff` | `list_all()`, `add()`, `update()`, `delete()` |
| `src/models/medicine.py` | `medicines` | `list_all()`, `low_stock()` — returns items where `stock_qty <= reorder_level`, `add()`, `update()`, `delete()` |
| `src/models/bill.py` | `bills` | `list_all()` with JOIN on `patients`, `add()` — auto-calculates `total = float(room) + float(consult) + float(medicine)`, `update_status()`, `delete()` |
| `src/models/audit.py` | `audit_log`, `defect_log` | `list_audit(limit)`, `list_defects()`, `add_defect(category, desc, severity)`, `defect_counts_by_category()` → dict fed to Pareto chart |

### Views Layer (UI Tabs)

Each view imports its model, relevant widgets, and validators — never raw SQL.

| File | Tab Name | Notable Q07 Usage |
|---|---|---|
| `src/views/dashboard_view.py` | Dashboard | Live KPI counts via direct model calls; Refresh button |
| `src/views/patients_view.py` | Patients | `PhoneMaskEntry`, `Combobox(GENDERS, BLOOD_GROUPS)`, `AutocompleteEntry`, `confirm_delete/update` |
| `src/views/doctors_view.py` | Doctors | `PhoneMaskEntry`, `Combobox(DEPARTMENTS)`, `confirm_delete/update` |
| `src/views/appointments_view.py` | Appointments | Patient `AutocompleteEntry`, Doctor `Combobox`, Status `Combobox(APPT_STATUS)`, `confirm_delete/update` |
| `src/views/rooms_view.py` | Rooms / Wards | `Combobox(ROOM_TYPES, ROOM_STATUS)`, `confirm_delete/update` |
| `src/views/staff_view.py` | Staff | `PhoneMaskEntry`, `Combobox(STAFF_ROLES, SHIFTS)`, `confirm_delete/update` |
| `src/views/medicines_view.py` | Pharmacy | `Combobox(MEDICINE_CATEGORIES)`, low-stock highlight, `confirm_delete/update` |
| `src/views/billing_view.py` | Billing | Patient `AutocompleteEntry`, `Combobox(PAYMENT_METHODS, PAYMENT_STATUS)`, auto-total, `confirm_delete` |
| `src/views/audit_view.py` | Audit Log | Read-only `Treeview` of `audit_log`; refreshed on tab switch |
| `src/views/defects_view.py` | Defect Checksheet | `Combobox(DEFECT_CATEGORIES, DEFECT_SEVERITY)`, feeds `sqc/pareto_chart.py` |

### Database Schema

9 tables — all enforced through `db_manager.SCHEMA` (run once at startup via `init_db()`):

```
patients     — patient_id PK, full_name, gender CHECK, dob, blood_group CHECK,
               phone, address, room_id FK→rooms, created_at, updated_at
doctors      — doctor_id PK, full_name, department, phone, created_at
appointments — appointment_id PK, patient_id FK→patients CASCADE,
               doctor_id FK→doctors CASCADE, appt_date, appt_time,
               status DEFAULT 'Scheduled', notes, created_at
rooms        — room_id PK, room_number UNIQUE, room_type, status, rate_per_day
staff        — staff_id PK, full_name, role, shift, phone, created_at
medicines    — medicine_id PK, name, category, stock_qty, unit_price, reorder_level
bills        — bill_id PK, patient_id FK→patients CASCADE, room_charges,
               consultation_charges, medicine_charges, total_amount,
               payment_method, payment_status, created_at
audit_log    — log_id PK, table_name, record_id, action CHECK(INSERT/UPDATE/DELETE),
               details, performed_by, timestamp
defect_log   — defect_id PK, category, description, severity, status, logged_at
```

### SQC Scripts

| File | Purpose |
|---|---|
| `sqc/pareto_chart.py` | Calls `audit.defect_counts_by_category()`, sorts by frequency, plots bars + cumulative % line, saves `sqc/pareto_chart.png` |
| `sqc/fishbone_diagram.py` | Draws a 4-branch Ishikawa diagram (People, Process, Software Code, Infrastructure) using Matplotlib patches, saves `sqc/fishbone_diagram.png` |
| `docs/build_fmea.py` | Generates `docs/FMEA_RiskAudit.xlsx` using openpyxl with formula-driven RPN columns |

---

## Design Rules (Separation of Concerns)

1. **Models never import Tkinter.** All SQL logic lives in `src/models/` only.
2. **Views never run raw SQL.** All data access goes through a model function.
3. **Widgets are written once.** `PhoneMaskEntry`, `AutocompleteEntry`, and `confirm_dialog` are in `src/widgets/` and imported wherever needed — not duplicated per screen.
4. **Dropdowns are defined once.** All fixed lists live in `src/config.py`. Adding a new department means editing one line in one file.
5. **`log_audit()` is called inside the model, not the view.** This guarantees the audit trail cannot be bypassed by a view that forgets to call it.
