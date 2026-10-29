"""
db_manager.py -- Connection handling + schema creation for every HMS module.
Models (src/models/*.py) call get_connection(); nothing outside this package
talks to sqlite3 directly, so the schema has exactly one source of truth.
"""
import sqlite3
import sys
import os
from datetime import datetime

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
    rate_per_day   REAL NOT NULL DEFAULT 0,
    ward_id        INTEGER
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
    reorder_level  INTEGER NOT NULL DEFAULT 10,
    batch_no       TEXT NOT NULL DEFAULT 'BAT-2026-01',
    expiry_date    TEXT NOT NULL DEFAULT '2027-12-31'
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

-- Authentication & Role-Based Access Control (All 10 Stakeholder Roles)
CREATE TABLE IF NOT EXISTS users (
    user_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role          TEXT NOT NULL,
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

-- Prescriptions & Clinical Medical History per Visit
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

-- Diagnostic Laboratory & Radiology Testing Module
CREATE TABLE IF NOT EXISTS lab_tests (
    test_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id     INTEGER NOT NULL,
    doctor_id      INTEGER NOT NULL,
    test_name      TEXT NOT NULL,
    category       TEXT NOT NULL,
    result_value   REAL,
    unit           TEXT NOT NULL,
    ref_min        REAL NOT NULL,
    ref_max        REAL NOT NULL,
    status         TEXT NOT NULL DEFAULT 'Pending' CHECK(status IN ('Pending','Completed','Cancelled')),
    abnormal_flag  INTEGER NOT NULL DEFAULT 0 CHECK(abnormal_flag IN (0, 1)),
    notes          TEXT,
    created_at     TEXT NOT NULL,
    completed_at   TEXT,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id)  REFERENCES doctors(doctor_id)  ON DELETE CASCADE
);

-- Automated Pharmacy Purchase Orders for Low-Stock Replenishment
CREATE TABLE IF NOT EXISTS purchase_orders (
    po_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    medicine_id    INTEGER NOT NULL,
    supplier_name  TEXT NOT NULL,
    order_qty      INTEGER NOT NULL,
    unit_cost      REAL NOT NULL,
    total_cost     REAL NOT NULL,
    status         TEXT NOT NULL DEFAULT 'Pending' CHECK(status IN ('Pending','Received','Cancelled')),
    order_date     TEXT NOT NULL,
    received_date  TEXT,
    FOREIGN KEY (medicine_id) REFERENCES medicines(medicine_id) ON DELETE CASCADE
);

-- NABH & ISO 9001 Hospital Quality Inspection Audit Checklist
CREATE TABLE IF NOT EXISTS quality_audits (
    audit_id           INTEGER PRIMARY KEY AUTOINCREMENT,
    department         TEXT NOT NULL,
    standard_code      TEXT NOT NULL,
    criterion          TEXT NOT NULL,
    score              INTEGER NOT NULL CHECK(score BETWEEN 0 AND 10),
    max_score          INTEGER NOT NULL DEFAULT 10,
    compliance_status  TEXT NOT NULL CHECK(compliance_status IN ('Compliant','Minor Non-Conformance','Major Non-Conformance')),
    audited_by         TEXT NOT NULL,
    audit_date         TEXT NOT NULL,
    corrective_action  TEXT
);

-- ================= NEW HOSPITAL SYSTEM TABLES =================

-- Hospital Departments Master
CREATE TABLE IF NOT EXISTS departments (
    department_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL UNIQUE,
    code            TEXT NOT NULL UNIQUE,
    description     TEXT,
    head_doctor_id  INTEGER,
    location        TEXT,
    phone           TEXT,
    has_opd         INTEGER NOT NULL DEFAULT 1,
    has_ipd         INTEGER NOT NULL DEFAULT 1,
    created_at      TEXT NOT NULL
);

-- Specialized Doctor Profiles & Credentials
CREATE TABLE IF NOT EXISTS doctor_profiles (
    profile_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    doctor_id          INTEGER NOT NULL UNIQUE,
    user_id            INTEGER,
    specialization     TEXT NOT NULL,
    qualifications     TEXT NOT NULL,
    experience_years   INTEGER NOT NULL DEFAULT 5,
    consultation_fee   REAL NOT NULL DEFAULT 500.0,
    room_number        TEXT,
    max_daily_patients INTEGER NOT NULL DEFAULT 30,
    is_available       INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
);

-- Inpatient Wards & Unit Management
CREATE TABLE IF NOT EXISTS wards (
    ward_id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name               TEXT NOT NULL UNIQUE,
    department_id      INTEGER,
    ward_type          TEXT NOT NULL,
    floor_number       INTEGER NOT NULL DEFAULT 1,
    total_beds         INTEGER NOT NULL DEFAULT 10,
    manager_user_id    INTEGER,
    in_charge_nurse_id INTEGER,
    created_at         TEXT NOT NULL,
    FOREIGN KEY (department_id) REFERENCES departments(department_id) ON DELETE SET NULL,
    FOREIGN KEY (manager_user_id) REFERENCES users(user_id) ON DELETE SET NULL
);

-- Nurse Profiles & Ward Assignments
CREATE TABLE IF NOT EXISTS nurse_profiles (
    nurse_profile_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    staff_id           INTEGER,
    user_id            INTEGER NOT NULL UNIQUE,
    ward_id            INTEGER,
    department         TEXT NOT NULL,
    shift              TEXT NOT NULL DEFAULT 'Morning',
    qualifications     TEXT,
    assigned_patients  TEXT DEFAULT '',
    FOREIGN KEY (staff_id) REFERENCES staff(staff_id) ON DELETE SET NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (ward_id) REFERENCES wards(ward_id) ON DELETE SET NULL
);

-- OPD Queue & Token Desk
CREATE TABLE IF NOT EXISTS opd_queue (
    queue_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    appointment_id  INTEGER,
    patient_id      INTEGER NOT NULL,
    doctor_id       INTEGER NOT NULL,
    token_number    INTEGER NOT NULL,
    queue_date      TEXT NOT NULL,
    status          TEXT NOT NULL DEFAULT 'Waiting' CHECK(status IN ('Waiting','Called','In Consultation','Completed','Skipped')),
    check_in_time   TEXT NOT NULL,
    call_time       TEXT,
    complete_time   TEXT,
    vital_id        INTEGER,
    priority        TEXT NOT NULL DEFAULT 'Normal' CHECK(priority IN ('Normal','Urgent','Emergency')),
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id) ON DELETE CASCADE
);

-- Clinical Orders (Doctor -> Nurse Clinical Workflow)
CREATE TABLE IF NOT EXISTS clinical_orders (
    order_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id      INTEGER NOT NULL,
    doctor_id       INTEGER NOT NULL,
    doctor_name     TEXT,
    order_type      TEXT NOT NULL,
    order_text      TEXT NOT NULL,
    urgency         TEXT NOT NULL DEFAULT 'Routine' CHECK(urgency IN ('Routine','Urgent','STAT (Immediate)')),
    status          TEXT NOT NULL DEFAULT 'Ordered' CHECK(status IN ('Ordered','Acknowledged','In Progress','Completed','Discontinued')),
    ward_id         INTEGER,
    bed_number      TEXT,
    ordered_at      TEXT NOT NULL,
    acknowledged_by TEXT,
    acknowledged_at TEXT,
    completed_by    TEXT,
    completed_at    TEXT,
    execution_notes TEXT,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id) ON DELETE CASCADE
);

-- Doctor <-> Nurse Clinical Communication & Urgent Alerts
CREATE TABLE IF NOT EXISTS doctor_nurse_messages (
    message_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id        INTEGER,
    sender_user_id    INTEGER NOT NULL,
    sender_name       TEXT NOT NULL,
    sender_role       TEXT NOT NULL,
    recipient_role    TEXT NOT NULL DEFAULT 'All',
    recipient_user_id INTEGER,
    department        TEXT,
    subject           TEXT NOT NULL,
    message_body      TEXT NOT NULL,
    urgency           TEXT NOT NULL DEFAULT 'Normal' CHECK(urgency IN ('Normal','Urgent','Code Red')),
    is_read           INTEGER NOT NULL DEFAULT 0,
    created_at        TEXT NOT NULL,
    FOREIGN KEY (sender_user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Nursing & Medical Shift Handover Protocol
CREATE TABLE IF NOT EXISTS shift_handovers (
    handover_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    ward_id             INTEGER,
    department          TEXT NOT NULL,
    shift_from          TEXT NOT NULL,
    shift_to            TEXT NOT NULL,
    handover_date       TEXT NOT NULL,
    outgoing_nurse_name TEXT NOT NULL,
    incoming_nurse_name TEXT NOT NULL,
    critical_patients   TEXT,
    pending_orders      TEXT,
    general_notes       TEXT,
    status              TEXT NOT NULL DEFAULT 'Completed',
    created_at          TEXT NOT NULL
);

-- Outpatient Clinical Encounters & SOAP Notes
CREATE TABLE IF NOT EXISTS encounters (
    encounter_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id      INTEGER NOT NULL,
    doctor_id       INTEGER NOT NULL,
    appointment_id  INTEGER,
    encounter_date  TEXT NOT NULL,
    chief_complaint TEXT NOT NULL,
    history_illness TEXT,
    examination     TEXT,
    diagnosis       TEXT NOT NULL,
    plan            TEXT,
    doctor_notes    TEXT,
    follow_up_date  TEXT,
    created_at      TEXT NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id) ON DELETE CASCADE
);
"""


def _hash_pw(password: str) -> str:
    import hashlib
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def init_db():
    os.makedirs(os.path.dirname(config.DB_PATH), exist_ok=True)
    conn = get_connection()
    conn.executescript(SCHEMA)

    # 1. Backward compatibility check & migration for users table CHECK constraint
    try:
        conn.execute("INSERT INTO users (username, password_hash, role, full_name, created_at) VALUES ('__probe__', 'x', 'Nurse', 'x', 'x')")
        conn.execute("DELETE FROM users WHERE username = '__probe__'")
    except sqlite3.IntegrityError:
        # Recreate users table without the restrictive CHECK constraint
        conn.execute("PRAGMA foreign_keys = OFF")
        conn.execute("ALTER TABLE users RENAME TO users_old")
        conn.execute("""
        CREATE TABLE users (
            user_id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username      TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role          TEXT NOT NULL,
            full_name     TEXT NOT NULL,
            email         TEXT,
            created_at    TEXT NOT NULL
        )""")
        conn.execute("INSERT INTO users (user_id, username, password_hash, role, full_name, email, created_at) SELECT user_id, username, password_hash, role, full_name, email, created_at FROM users_old")
        conn.execute("DROP TABLE users_old")
        conn.execute("PRAGMA foreign_keys = ON")

    # 2. Backward compatibility migration for patients.allergies
    cols = [r["name"] for r in conn.execute("PRAGMA table_info(patients)").fetchall()]
    if "allergies" not in cols:
        conn.execute("ALTER TABLE patients ADD COLUMN allergies TEXT NOT NULL DEFAULT 'None'")

    # 3. Backward compatibility migration for medicines
    med_cols = [r["name"] for r in conn.execute("PRAGMA table_info(medicines)").fetchall()]
    if "batch_no" not in med_cols:
        conn.execute("ALTER TABLE medicines ADD COLUMN batch_no TEXT NOT NULL DEFAULT 'BAT-2026-01'")
    if "expiry_date" not in med_cols:
        conn.execute("ALTER TABLE medicines ADD COLUMN expiry_date TEXT NOT NULL DEFAULT '2027-12-31'")

    # 4. Backward compatibility migration for rooms.ward_id
    room_cols = [r["name"] for r in conn.execute("PRAGMA table_info(rooms)").fetchall()]
    if "ward_id" not in room_cols:
        conn.execute("ALTER TABLE rooms ADD COLUMN ward_id INTEGER")

    # 5. Seed initial medicines if table empty
    med_count = conn.execute("SELECT COUNT(*) as c FROM medicines").fetchone()["c"]
    if med_count == 0:
        seed_meds = [
            ("Paracetamol 650mg", "Tablet", 120, 2.50, 20, "BAT-PCM-01", "2027-10-31"),
            ("Amoxicillin 500mg", "Capsule", 85, 12.00, 15, "BAT-AMX-02", "2027-08-15"),
            ("Azithromycin 500mg", "Tablet", 40, 25.00, 10, "BAT-AZM-03", "2027-12-01"),
            ("Cough Syrup 100ml", "Syrup", 30, 85.00, 10, "BAT-SYR-04", "2027-05-20"),
            ("Normal Saline 500ml", "Injection", 50, 45.00, 15, "BAT-INJ-05", "2028-01-10"),
            ("Pantoprazole 40mg", "Tablet", 95, 8.50, 20, "BAT-PAN-06", "2027-11-15"),
            ("Atorvastatin 20mg", "Tablet", 60, 18.00, 15, "BAT-ATV-07", "2028-02-28"),
            ("Metformin 500mg", "Tablet", 110, 4.00, 25, "BAT-MET-08", "2027-09-30"),
            ("Expired Batch Sample (Doxycycline)", "Capsule", 10, 18.00, 5, "BAT-EXP-00", "2024-01-01"),
        ]
        conn.executemany(
            "INSERT INTO medicines (name, category, stock_qty, unit_price, reorder_level, batch_no, expiry_date) "
            "VALUES (?,?,?,?,?,?,?)",
            seed_meds
        )

    # 6. Seed all 10 demo user accounts
    now_str = datetime.now().isoformat(timespec="seconds")
    demo_users = [
        ("admin", _hash_pw("admin123"), "Admin", "Dr. Ajay Bora (System Admin)", "admin@hospital.local"),
        ("doctor", _hash_pw("doctor123"), "Doctor", "Dr. Rajesh Sharma (Lead Cardiologist)", "doctor@hospital.local"),
        ("receptionist", _hash_pw("recep123"), "Receptionist", "Priya Verma (Front Desk Lead)", "reception@hospital.local"),
        ("nurse", _hash_pw("nurse123"), "Nurse", "Sister Sunita Patel (In-Charge Nurse)", "nurse@hospital.local"),
        ("ward_manager", _hash_pw("ward123"), "Ward Manager", "Vikram Joshi (Central Ward Supervisor)", "ward@hospital.local"),
        ("lab_tech", _hash_pw("lab123"), "Lab Technician", "Anil Kumar (Senior Medical Lab Tech)", "lab@hospital.local"),
        ("pharmacist", _hash_pw("pharma123"), "Pharmacist", "Meena Iyer (Chief Pharmacist)", "pharma@hospital.local"),
        ("cashier", _hash_pw("cash123"), "Cashier", "Ramesh Gupta (Senior Billing Officer)", "cashier@hospital.local"),
        ("hospital_manager", _hash_pw("hosp123"), "Hospital Manager", "Dr. Sunita Rao (Medical Superintendent)", "manager@hospital.local"),
        ("patient", _hash_pw("patient123"), "Patient", "Rohan Sharma (Patient Portal)", "rohan.patient@example.com"),
    ]
    for u in demo_users:
        exists = conn.execute("SELECT 1 FROM users WHERE username = ?", (u[0],)).fetchone()
        if not exists:
            conn.execute(
                "INSERT INTO users (username, password_hash, role, full_name, email, created_at) VALUES (?,?,?,?,?,?)",
                (u[0], u[1], u[2], u[3], u[4], now_str)
            )

    # 7. Seed Departments
    dept_count = conn.execute("SELECT COUNT(*) as c FROM departments").fetchone()["c"]
    if dept_count == 0:
        seed_depts = [
            ("Cardiology", "CARD", "Comprehensive cardiovascular care, ECG, ECHO, and Catheterization", "Wing A - 2nd Floor", "+91-98765-10001", 1, 1),
            ("Orthopedics", "ORTH", "Bone, joint, spine, and trauma care with arthroscopy unit", "Wing B - 3rd Floor", "+91-98765-10002", 1, 1),
            ("Pediatrics", "PED", "Neonatal and child healthcare with pediatric intensive care", "Wing A - 1st Floor", "+91-98765-10003", 1, 1),
            ("General Medicine", "MED", "Internal medicine, chronic illness, and general outpatient clinics", "Ground Floor - OPD", "+91-98765-10004", 1, 1),
            ("Neurology", "NEUR", "Brain, nerve, stroke unit, and neurosurgery consultation", "Wing C - 2nd Floor", "+91-98765-10005", 1, 1),
            ("ENT", "ENT", "Ear, Nose, Throat diagnosis and microsurgical procedures", "Ground Floor - OPD", "+91-98765-10006", 1, 0),
            ("Dermatology", "DERM", "Skin, allergy, cosmetology, and laser dermatology", "Ground Floor - OPD", "+91-98765-10007", 1, 0),
            ("Gynecology & Obstetrics", "GYN", "Maternity care, antenatal clinics, and women's health", "Wing B - 1st Floor", "+91-98765-10008", 1, 1),
            ("Emergency & Trauma", "EMER", "24/7 emergency resuscitation, trauma triage, and critical intake", "Ground Floor - ER Bay", "+91-98765-10009", 1, 1),
            ("Intensive Care Unit (ICU)", "ICU", "High-dependency multi-parameter critical care life support", "Wing A - 4th Floor", "+91-98765-10010", 0, 1),
            ("Operation Theatre", "OT", "State-of-the-art sterile surgical suites", "Wing C - 3rd Floor", "+91-98765-10011", 0, 1),
            ("Laboratory & Diagnostics", "LAB", "Automated clinical pathology, hematology, and biochemistry", "Basement - Level 1", "+91-98765-10012", 0, 0),
            ("Radiology & Imaging", "RAD", "Digital X-Ray, CT Scan, MRI, and Ultrasonography", "Basement - Level 1", "+91-98765-10013", 0, 0),
            ("Pharmacy", "PHARM", "24/7 central dispensary and inpatient unit-dose supply", "Ground Floor - Lobby", "+91-98765-10014", 0, 0),
        ]
        conn.executemany(
            "INSERT INTO departments (name, code, description, location, phone, has_opd, has_ipd, created_at) VALUES (?,?,?,?,?,?,?,?)",
            [(d[0], d[1], d[2], d[3], d[4], d[5], d[6], now_str) for d in seed_depts]
        )

    # 8. Seed Doctors across diverse specializations
    doc_count = conn.execute("SELECT COUNT(*) as c FROM doctors").fetchone()["c"]
    if doc_count == 0:
        seed_doctors = [
            ("Dr. Rajesh Sharma", "Cardiology", "+91-98765-43210"),
            ("Dr. Preeti Deshmukh", "Orthopedics", "+91-98765-43211"),
            ("Dr. Arvind Kejriwal", "Neurology", "+91-98765-43212"),
            ("Dr. Sneha Kulkarni", "Pediatrics", "+91-98765-43213"),
            ("Dr. Amit Mehra", "General Medicine", "+91-98765-43214"),
            ("Dr. Kavita Reddy", "Gynecology & Obstetrics", "+91-98765-43215"),
            ("Dr. Farhan Akhtar", "ENT", "+91-98765-43216"),
            ("Dr. Pooja Chopra", "Dermatology", "+91-98765-43217"),
            ("Dr. Sameer Khan", "Emergency & Trauma", "+91-98765-43218"),
        ]
        conn.executemany(
            "INSERT INTO doctors (full_name, department, phone, created_at) VALUES (?,?,?,?)",
            [(d[0], d[1], d[2], now_str) for d in seed_doctors]
        )

    # 9. Seed Doctor Profiles
    prof_count = conn.execute("SELECT COUNT(*) as c FROM doctor_profiles").fetchone()["c"]
    if prof_count == 0:
        doc_rows = conn.execute("SELECT doctor_id, full_name, department FROM doctors").fetchall()
        doc_specs = {
            "Dr. Rajesh Sharma": ("Cardiologist", "MBBS, MD (Medicine), DM (Cardiology)", 14, 800.0, "OPD-101"),
            "Dr. Preeti Deshmukh": ("Orthopedic Surgeon", "MBBS, MS (Orthopedics), MCh", 11, 700.0, "OPD-102"),
            "Dr. Arvind Kejriwal": ("Neurologist", "MBBS, MD, DM (Neurology)", 16, 900.0, "OPD-103"),
            "Dr. Sneha Kulkarni": ("Pediatrician", "MBBS, MD (Pediatrics), DCH", 9, 600.0, "OPD-104"),
            "Dr. Amit Mehra": ("General Physician", "MBBS, MD (Internal Medicine)", 8, 500.0, "OPD-105"),
            "Dr. Kavita Reddy": ("Gynecologist & Obstetrician", "MBBS, MS (OBG), DGO", 12, 750.0, "OPD-106"),
            "Dr. Farhan Akhtar": ("ENT Specialist", "MBBS, MS (ENT)", 7, 650.0, "OPD-107"),
            "Dr. Pooja Chopra": ("Dermatologist", "MBBS, MD (Dermatology)", 6, 700.0, "OPD-108"),
            "Dr. Sameer Khan": ("Emergency Medicine Specialist", "MBBS, MEM (Emergency Medicine)", 10, 500.0, "ER-01"),
        }
        for d in doc_rows:
            spec_info = doc_specs.get(d["full_name"], ("Consultant Specialist", "MBBS, MD", 5, 500.0, "OPD-100"))
            # Link doctor user_id if doctor username matches
            u_row = conn.execute("SELECT user_id FROM users WHERE username = 'doctor'").fetchone()
            u_id = u_row["user_id"] if d["full_name"] == "Dr. Rajesh Sharma" and u_row else None
            prof_exists = conn.execute("SELECT 1 FROM doctor_profiles WHERE doctor_id = ?", (d["doctor_id"],)).fetchone()
            if not prof_exists:
                conn.execute(
                    "INSERT INTO doctor_profiles (doctor_id, user_id, specialization, qualifications, experience_years, consultation_fee, room_number, max_daily_patients, is_available) "
                    "VALUES (?,?,?,?,?,?,?,?,1)",
                    (d["doctor_id"], u_id, spec_info[0], spec_info[1], spec_info[2], spec_info[3], spec_info[4], 30)
                )

    # 10. Seed Wards
    ward_count = conn.execute("SELECT COUNT(*) as c FROM wards").fetchone()["c"]
    if ward_count == 0:
        seed_wards = [
            ("Cardiac Care Ward (CCW)", 1, "Cardiac Care Ward", 2, 8),
            ("Ortho Trauma Ward (OTW)", 2, "Ortho Trauma Ward", 3, 10),
            ("General Medical Ward (GMW)", 4, "General Medical Ward", 1, 12),
            ("Pediatric Care Ward (PED)", 3, "Pediatric Ward", 2, 8),
            ("Maternity Care Ward (MAT)", 8, "Maternity Ward", 3, 8),
            ("Intensive Care Unit (ICU)", 10, "Intensive Care Unit (ICU)", 4, 6),
            ("Emergency Observation Bay (ER)", 9, "Emergency Observation Ward", 1, 10),
        ]
        conn.executemany(
            "INSERT INTO wards (name, department_id, ward_type, floor_number, total_beds, created_at) VALUES (?,?,?,?,?,?)",
            [(w[0], w[1], w[2], w[3], w[4], now_str) for w in seed_wards]
        )

    # 11. Seed Nurse Profiles
    nurse_count = conn.execute("SELECT COUNT(*) as c FROM nurse_profiles").fetchone()["c"]
    if nurse_count == 0:
        nurse_user = conn.execute("SELECT user_id FROM users WHERE username = 'nurse'").fetchone()
        if nurse_user:
            ccw_ward = conn.execute("SELECT ward_id FROM wards WHERE name LIKE '%Cardiac%'").fetchone()
            w_id = ccw_ward["ward_id"] if ccw_ward else 1
            conn.execute(
                "INSERT INTO nurse_profiles (staff_id, user_id, ward_id, department, shift, qualifications, assigned_patients) "
                "VALUES (NULL, ?, ?, 'Cardiology', 'Morning', 'B.Sc Nursing, Critical Care Certified', 'Bed 101, Bed 102')",
                (nurse_user["user_id"], w_id)
            )

    # 12. Seed initial rooms/beds if empty
    room_count = conn.execute("SELECT COUNT(*) as c FROM rooms").fetchone()["c"]
    if room_count == 0:
        seed_rooms = [
            ("CCW-Bed-01", "General Ward", "Available", 1500.0, 1),
            ("CCW-Bed-02", "General Ward", "Occupied", 1500.0, 1),
            ("CCW-Bed-03", "Semi-Private", "Available", 2200.0, 1),
            ("OTW-Bed-01", "General Ward", "Available", 1200.0, 2),
            ("OTW-Bed-02", "General Ward", "Cleaning / Sanitizing", 1200.0, 2),
            ("GMW-Bed-01", "General Ward", "Available", 800.0, 3),
            ("GMW-Bed-02", "General Ward", "Available", 800.0, 3),
            ("ICU-Bed-01", "ICU", "Occupied", 5000.0, 6),
            ("ICU-Bed-02", "ICU", "Available", 5000.0, 6),
            ("ER-Bay-01", "Emergency Observation", "Available", 1000.0, 7),
        ]
        conn.executemany(
            "INSERT INTO rooms (room_number, room_type, status, rate_per_day, ward_id) VALUES (?,?,?,?,?)",
            seed_rooms
        )

    # 13. Seed sample patients if empty
    pat_count = conn.execute("SELECT COUNT(*) as c FROM patients").fetchone()["c"]
    if pat_count == 0:
        seed_patients = [
            ("Amitabh Verma", "Male", "1978-05-12", "B+", "+91-98765-11001", "12 Park Street, Delhi", "Penicillin", None, now_str, now_str),
            ("Sunita Rao", "Female", "1985-09-24", "O+", "+91-98765-11002", "45 Green Avenue, Delhi", "None", 2, now_str, now_str),
            ("Vikramaditya Sen", "Male", "1992-11-03", "A+", "+91-98765-11003", "88 MG Road, Delhi", "Sulfa Drugs", None, now_str, now_str),
            ("Rohan Sharma", "Male", "1995-02-18", "AB+", "+91-98765-11004", "102 Ring Road, Delhi", "None", None, now_str, now_str),
        ]
        conn.executemany(
            "INSERT INTO patients (full_name, gender, dob, blood_group, phone, address, allergies, room_id, created_at, updated_at) "
            "VALUES (?,?,?,?,?,?,?,?,?,?)",
            seed_patients
        )

    # 14. Seed sample Clinical Orders & Communication (Doctor <-> Nurse)
    order_count = conn.execute("SELECT COUNT(*) as c FROM clinical_orders").fetchone()["c"]
    if order_count == 0:
        doc_row = conn.execute("SELECT doctor_id FROM doctors LIMIT 1").fetchone()
        pat_row = conn.execute("SELECT patient_id FROM patients LIMIT 1").fetchone()
        d_id = doc_row["doctor_id"] if doc_row else 1
        p_id = pat_row["patient_id"] if pat_row else 1

        seed_orders = [
            (p_id, d_id, "Dr. Rajesh Sharma", "Medication", "Administer IV Paracetamol 1g in 100ml NS immediately", "STAT (Immediate)", "Ordered", 1, "CCW-Bed-02", now_str, None, None, None, None, None),
            (p_id, d_id, "Dr. Rajesh Sharma", "Vital Sign Monitoring", "Record BP, Pulse, SpO2 every 2 hours and alert if Systolic > 160", "Urgent", "Acknowledged", 1, "CCW-Bed-02", now_str, "Sister Sunita Patel", now_str, None, None, "Vitals charting scheduled"),
            (p_id, d_id, "Dr. Rajesh Sharma", "Lab Test", "Draw venous blood sample for Cardiac Troponin-I and CBC", "STAT (Immediate)", "Completed", 1, "CCW-Bed-02", now_str, "Sister Sunita Patel", now_str, "Sister Sunita Patel", now_str, "Sample sent to central lab #TRP-902"),
        ]
        conn.executemany(
            "INSERT INTO clinical_orders (patient_id, doctor_id, doctor_name, order_type, order_text, urgency, status, ward_id, bed_number, ordered_at, acknowledged_by, acknowledged_at, completed_by, completed_at, execution_notes) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            seed_orders
        )

    # 15. Seed sample Doctor-Nurse Messages
    msg_count = conn.execute("SELECT COUNT(*) as c FROM doctor_nurse_messages").fetchone()["c"]
    if msg_count == 0:
        pat_row = conn.execute("SELECT patient_id FROM patients LIMIT 1").fetchone()
        p_id = pat_row["patient_id"] if pat_row else 1
        n_user = conn.execute("SELECT user_id FROM users WHERE username = 'nurse'").fetchone()
        d_user = conn.execute("SELECT user_id FROM users WHERE username = 'doctor'").fetchone()
        n_uid = n_user["user_id"] if n_user else 1
        d_uid = d_user["user_id"] if d_user else 1

        seed_messages = [
            (p_id, n_uid, "Sister Sunita Patel", "Nurse", "Doctor", d_uid, "Cardiology", "Vitals Alert: SpO2 dropping to 92%", "Patient in CCW-Bed-02 feels mild chest tightness, SpO2 92% on room air. Started 2L nasal cannula.", "Urgent", 0, now_str),
            (p_id, d_uid, "Dr. Rajesh Sharma", "Doctor", "Nurse", n_uid, "Cardiology", "Re: SpO2 Alert - Continue Oxygen", "Please maintain O2 at 2L/min, check ECG immediately and notify if chest pain increases.", "Urgent", 1, now_str),
            (p_id, n_uid, "Sister Sunita Patel", "Nurse", "All", None, "Cardiology", "STAT Medication Administered", "IV Paracetamol 1g given at 20:15. Temperature down to 99.1 F.", "Normal", 1, now_str),
        ]
        conn.executemany(
            "INSERT INTO doctor_nurse_messages (patient_id, sender_user_id, sender_name, sender_role, recipient_role, recipient_user_id, department, subject, message_body, urgency, is_read, created_at) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            seed_messages
        )

    # 16. Seed sample Shift Handover
    handover_count = conn.execute("SELECT COUNT(*) as c FROM shift_handovers").fetchone()["c"]
    if handover_count == 0:
        today_date = datetime.now().strftime("%Y-%m-%d")
        conn.execute(
            "INSERT INTO shift_handovers (ward_id, department, shift_from, shift_to, handover_date, outgoing_nurse_name, incoming_nurse_name, critical_patients, pending_orders, general_notes, status, created_at) "
            "VALUES (1, 'Cardiology', 'Morning', 'Evening', ?, 'Sister Sunita Patel', 'Nurse Rekha Sharma', 'Patient Amitabh Verma in Bed-02: post-angina monitoring, vitals stable', 'Repeat Troponin-I test at 22:00', 'Crash cart verified, O2 cylinder pressure 140 bar', 'Completed', ?)",
            (today_date, now_str)
        )

    # 17. Seed initial NABH & ISO quality audits if empty
    audit_count = conn.execute("SELECT COUNT(*) as c FROM quality_audits").fetchone()["c"]
    if audit_count == 0:
        seed_audits = [
            ("Patient Registration", "NABH-AAC.1", "Patient Identification & Keystroke Input Masking (+91 Phone)", 10, 10, "Compliant", "Dr. Ajay Bora (TQM Lead)", "2026-10-10", "Poka-Yoke input masking enforced across UI"),
            ("Pharmacy & Dispensary", "NABH-MOM.3", "Pharmaceutical Expiry Date Verification & Batch Integrity", 9, 10, "Compliant", "Dr. Ajay Bora (TQM Lead)", "2026-10-10", "Automated system blocks expired batch dispensing"),
            ("Clinical Consultations", "NABH-COP.4", "Adverse Drug Reaction (ADR) Pre-flight Allergy Contraindication", 10, 10, "Compliant", "Dr. Ajay Bora (TQM Lead)", "2026-10-11", "System blocks contra-indicated prescriptions"),
            ("Inpatient Wards", "NABH-HIC.2", "Bed Availability Tracking & Infection Control Sanitization", 8, 10, "Compliant", "Dr. Ajay Bora (TQM Lead)", "2026-10-11", "Bed status tracking integrated with discharge flow"),
            ("Billing & Accounts", "ISO-9001-8.2", "Itemized Invoicing Accuracy & Automated Arithmetic Calculation", 10, 10, "Compliant", "Dr. Ajay Bora (TQM Lead)", "2026-10-12", "Read-only calculation formula eliminates manual error"),
            ("Emergency & Triage", "NABH-COP.2", "Physiological Vital Boundaries & Severity Priority Triage", 9, 10, "Compliant", "Dr. Ajay Bora (TQM Lead)", "2026-10-12", "Code Red automatic prioritization operational"),
        ]
        conn.executemany(
            "INSERT INTO quality_audits (department, standard_code, criterion, score, max_score, compliance_status, audited_by, audit_date, corrective_action) "
            "VALUES (?,?,?,?,?,?,?,?,?)",
            seed_audits
        )

    conn.commit()
    conn.close()


def log_audit(conn, table_name, record_id, action, details, user="front_desk_user"):
    """Shared helper -- every model module calls this inside the same transaction
    as its INSERT/UPDATE/DELETE so the audit trail can never go out of sync."""
    conn.execute(
        "INSERT INTO audit_log (table_name, record_id, action, details, performed_by, timestamp) "
        "VALUES (?,?,?,?,?,?)",
        (table_name, record_id, action, details, user, datetime.now().isoformat(timespec="seconds")),
    )
    # Dual-persistence to TQM audit evidence CSV
    try:
        from utils.logging_service import log_audit_event
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
    print(f"Database initialized at {config.DB_PATH}")
