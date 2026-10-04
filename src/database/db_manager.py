"""
db_manager.py -- Connection handling + schema creation for every HMS module.
Models (src/models/*.py) call get_connection(); nothing outside this package
talks to sqlite3 directly, so the schema has exactly one source of truth.
"""
import sqlite3
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DB_PATH  # noqa: E402


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


SCHEMA = """
CREATE TABLE IF NOT EXISTS patients (
    patient_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name      TEXT NOT NULL,
    gender         TEXT NOT NULL CHECK(gender IN ('Male','Female','Other')),
    dob            TEXT NOT NULL,
    blood_group    TEXT NOT NULL CHECK(blood_group IN ('A+','A-','B+','B-','AB+','AB-','O+','O-')),
    phone          TEXT NOT NULL,
    address        TEXT,
    room_id        INTEGER,
    created_at     TEXT NOT NULL,
    updated_at     TEXT NOT NULL,
    FOREIGN KEY (room_id) REFERENCES rooms(room_id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS doctors (
    doctor_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name      TEXT NOT NULL,
    department     TEXT NOT NULL,
    phone          TEXT NOT NULL,
    created_at     TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS appointments (
    appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id     INTEGER NOT NULL,
    doctor_id      INTEGER NOT NULL,
    appt_date      TEXT NOT NULL,
    appt_time      TEXT NOT NULL,
    status         TEXT NOT NULL DEFAULT 'Scheduled',
    notes          TEXT,
    created_at     TEXT NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id)  REFERENCES doctors(doctor_id)  ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS rooms (
    room_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    room_number    TEXT NOT NULL UNIQUE,
    room_type      TEXT NOT NULL,
    status         TEXT NOT NULL DEFAULT 'Available',
    rate_per_day   REAL NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS staff (
    staff_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name      TEXT NOT NULL,
    role           TEXT NOT NULL,
    shift          TEXT NOT NULL,
    phone          TEXT NOT NULL,
    created_at     TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS medicines (
    medicine_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    name           TEXT NOT NULL,
    category       TEXT NOT NULL,
    stock_qty      INTEGER NOT NULL DEFAULT 0,
    unit_price     REAL NOT NULL DEFAULT 0,
    reorder_level  INTEGER NOT NULL DEFAULT 10
);

CREATE TABLE IF NOT EXISTS bills (
    bill_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id     INTEGER NOT NULL,
    room_charges   REAL NOT NULL DEFAULT 0,
    consultation_charges REAL NOT NULL DEFAULT 0,
    medicine_charges REAL NOT NULL DEFAULT 0,
    total_amount   REAL NOT NULL DEFAULT 0,
    payment_method TEXT NOT NULL,
    payment_status TEXT NOT NULL DEFAULT 'Pending',
    created_at     TEXT NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE
);

-- Q07 Feature: Audit Logs -- immutable trail of every data-changing action, any table
CREATE TABLE IF NOT EXISTS audit_log (
    log_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    table_name     TEXT NOT NULL,
    record_id      INTEGER,
    action         TEXT NOT NULL CHECK(action IN ('INSERT','UPDATE','DELETE')),
    details        TEXT,
    performed_by   TEXT NOT NULL DEFAULT 'front_desk_user',
    timestamp      TEXT NOT NULL
);

-- Step 6: Defect / bug checksheet, feeds the Pareto chart
CREATE TABLE IF NOT EXISTS defect_log (
    defect_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    category       TEXT NOT NULL,
    description    TEXT NOT NULL,
    severity       TEXT NOT NULL,
    status         TEXT NOT NULL DEFAULT 'Open',
    logged_at      TEXT NOT NULL
);
"""


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_connection()
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()


def log_audit(conn, table_name, record_id, action, details, user="front_desk_user"):
    """Shared helper -- every model module calls this inside the same transaction
    as its INSERT/UPDATE/DELETE so the audit trail can never go out of sync."""
    from datetime import datetime
    conn.execute(
        "INSERT INTO audit_log (table_name, record_id, action, details, performed_by, timestamp) "
        "VALUES (?,?,?,?,?,?)",
        (table_name, record_id, action, details, user, datetime.now().isoformat(timespec="seconds")),
    )
    # Dual-persistence to TQM audit evidence CSV
    try:
        from src.utils.logging_service import log_audit_event
        log_audit_event(
            module=table_name,
            action=action,
            record_id=record_id or "",
            result="SUCCESS",
            description=details,
            user_id=user,
            role="Staff"
        )
    except Exception as e:
        print(f"[AuditSync] CSV write notice: {e}")



if __name__ == "__main__":
    init_db()
    print(f"Database initialized at {DB_PATH}")
