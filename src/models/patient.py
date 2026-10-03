"""patient.py -- Data-access functions for the patients table."""
from datetime import datetime
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_manager import get_connection, log_audit  # noqa: E402


def now():
    return datetime.now().isoformat(timespec="seconds")


def list_all(name_filter=""):
    conn = get_connection()
    if name_filter:
        rows = conn.execute(
            "SELECT * FROM patients WHERE full_name LIKE ? ORDER BY patient_id DESC",
            (f"%{name_filter}%",)
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM patients ORDER BY patient_id DESC").fetchall()
    conn.close()
    return rows


def name_candidates(prefix, limit=8):
    conn = get_connection()
    rows = conn.execute(
        "SELECT full_name FROM patients WHERE full_name LIKE ? LIMIT ?",
        (f"{prefix}%", limit)
    ).fetchall()
    conn.close()
    return [r["full_name"] for r in rows]


def get_id_by_name(name):
    conn = get_connection()
    row = conn.execute("SELECT patient_id FROM patients WHERE full_name = ?", (name,)).fetchone()
    conn.close()
    return row["patient_id"] if row else None


def add(full_name, gender, dob, blood_group, phone, address, room_id=None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO patients (full_name, gender, dob, blood_group, phone, address, room_id, "
        "created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?)",
        (full_name, gender, dob, blood_group, phone, address, room_id, now(), now())
    )
    new_id = cur.lastrowid
    log_audit(conn, "patients", new_id, "INSERT", f"Added patient '{full_name}'")
    conn.commit()
    conn.close()
    return new_id


def update(patient_id, full_name, gender, dob, blood_group, phone, address, room_id=None):
    conn = get_connection()
    conn.execute(
        "UPDATE patients SET full_name=?, gender=?, dob=?, blood_group=?, phone=?, address=?, "
        "room_id=?, updated_at=? WHERE patient_id=?",
        (full_name, gender, dob, blood_group, phone, address, room_id, now(), patient_id)
    )
    log_audit(conn, "patients", patient_id, "UPDATE", "Patient record updated")
    conn.commit()
    conn.close()


def delete(patient_id):
    conn = get_connection()
    conn.execute("DELETE FROM patients WHERE patient_id=?", (patient_id,))
    log_audit(conn, "patients", patient_id, "DELETE", "Patient record deleted")
    conn.commit()
    conn.close()
