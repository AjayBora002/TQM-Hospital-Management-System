"""doctor.py -- Data-access functions for the doctors table."""
from datetime import datetime
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_manager import get_connection, log_audit  # noqa: E402


def now():
    return datetime.now().isoformat(timespec="seconds")


def list_all():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM doctors ORDER BY doctor_id DESC").fetchall()
    conn.close()
    return rows


def choices_map():
    """Returns {'Dr Name (Department)': doctor_id} for dropdown population."""
    conn = get_connection()
    rows = conn.execute("SELECT doctor_id, full_name, department FROM doctors").fetchall()
    conn.close()
    return {f"{r['full_name']} ({r['department']})": r["doctor_id"] for r in rows}


def add(full_name, department, phone):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO doctors (full_name, department, phone, created_at) VALUES (?,?,?,?)",
                (full_name, department, phone, now()))
    new_id = cur.lastrowid
    log_audit(conn, "doctors", new_id, "INSERT", f"Added doctor '{full_name}'")
    conn.commit()
    conn.close()
    return new_id


def update(doctor_id, full_name, department, phone):
    conn = get_connection()
    conn.execute("UPDATE doctors SET full_name=?, department=?, phone=? WHERE doctor_id=?",
                 (full_name, department, phone, doctor_id))
    log_audit(conn, "doctors", doctor_id, "UPDATE", "Doctor record updated")
    conn.commit()
    conn.close()


def delete(doctor_id):
    conn = get_connection()
    conn.execute("DELETE FROM doctors WHERE doctor_id=?", (doctor_id,))
    log_audit(conn, "doctors", doctor_id, "DELETE", "Doctor record deleted")
    conn.commit()
    conn.close()
