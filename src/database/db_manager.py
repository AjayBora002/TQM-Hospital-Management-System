"""
db_manager.py -- Connection handling + schema creation for every HMS module.
Models (src/models/*.py) call get_connection(); nothing outside this package
talks to sqlite3 directly, so the schema has exactly one source of truth.
"""
import sqlite3
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config  # noqa: E402


def get_connection():
    conn = sqlite3.connect(config.DB_PATH, timeout=30.0)
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
    allergies      TEXT NOT NULL DEFAULT 'None',
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

-- Clinical Poka-Yoke: Triage Vitals Log with physiological boundaries
CREATE TABLE IF NOT EXISTS vitals_log (
    vital_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id     INTEGER NOT NULL,
    systolic       INTEGER,
    diastolic      INTEGER,
    pulse          INTEGER,
    temperature    REAL,
    spo2           INTEGER,
    triage_status  TEXT NOT NULL DEFAULT 'Normal',
    recorded_at    TEXT NOT NULL,
    recorded_by    TEXT NOT NULL DEFAULT 'front_desk_user',
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE
);

-- Authentication & Role-Based Access Control (Admin, Doctor, Receptionist)
CREATE TABLE IF NOT EXISTS users (
    user_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role          TEXT NOT NULL CHECK(role IN ('Admin','Doctor','Receptionist')),
    full_name     TEXT NOT NULL,
    email         TEXT,
    created_at    TEXT NOT NULL
);

-- Inpatient Admission & Bed Stay Tracking Workflow
CREATE TABLE IF NOT EXISTS admissions (
    admission_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id      INTEGER NOT NULL,
    room_id         INTEGER NOT NULL,
    admission_date  TEXT NOT NULL,
    discharge_date  TEXT,
    status          TEXT NOT NULL DEFAULT 'Admitted' CHECK(status IN ('Admitted','Discharged')),
    diagnosis       TEXT,
    discharge_notes TEXT,
    created_at      TEXT NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (room_id) REFERENCES rooms(room_id) ON DELETE RESTRICT
);

-- Prescriptions & Clinical Medical History per Visit (Linking Medicines to Patients)
CREATE TABLE IF NOT EXISTS prescriptions (
    prescription_id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id      INTEGER NOT NULL,
    doctor_id       INTEGER NOT NULL,
    appointment_id  INTEGER,
    medicine_id     INTEGER NOT NULL,
    dosage          TEXT NOT NULL,
    frequency       TEXT NOT NULL,
    duration_days   INTEGER NOT NULL DEFAULT 5,
    instructions    TEXT,
    prescribed_date TEXT NOT NULL,
    status          TEXT NOT NULL DEFAULT 'Active' CHECK(status IN ('Active','Dispensed','Completed','Discontinued')),
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id) ON DELETE CASCADE,
    FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id) ON DELETE SET NULL,
    FOREIGN KEY (medicine_id) REFERENCES medicines(medicine_id) ON DELETE RESTRICT
);
"""


def _hash_pw(password: str) -> str:
    import hashlib
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def init_db():
    os.makedirs(os.path.dirname(config.DB_PATH), exist_ok=True)
    conn = get_connection()
    conn.executescript(SCHEMA)

    # Backward compatibility migration for patients.allergies
    cols = [r["name"] for r in conn.execute("PRAGMA table_info(patients)").fetchall()]
    if "allergies" not in cols:
        conn.execute("ALTER TABLE patients ADD COLUMN allergies TEXT NOT NULL DEFAULT 'None'")

    # Seed initial demo user accounts if empty
    user_count = conn.execute("SELECT COUNT(*) as c FROM users").fetchone()["c"]
    if user_count == 0:
        from datetime import datetime
        now_str = datetime.now().isoformat(timespec="seconds")
        demo_users = [
            ("admin", _hash_pw("admin123"), "Admin", "Dr. Ajay Bora (System Admin)", "admin@hospital.local"),
            ("doctor", _hash_pw("doctor123"), "Doctor", "Dr. Rajesh Sharma (Lead Physician)", "doctor@hospital.local"),
            ("receptionist", _hash_pw("recep123"), "Receptionist", "Priya Verma (Front Desk)", "reception@hospital.local"),
        ]
        conn.executemany(
            "INSERT INTO users (username, password_hash, role, full_name, email, created_at) VALUES (?,?,?,?,?,?)",
            [(u[0], u[1], u[2], u[3], u[4], now_str) for u in demo_users]
        )

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
