"""staff.py -- Data-access functions for the staff table (nurses, receptionists, etc.)."""
from datetime import datetime
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_manager import get_connection, log_audit  # noqa: E402


def now():
    return datetime.now().isoformat(timespec="seconds")


def list_all():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM staff ORDER BY staff_id DESC").fetchall()
    conn.close()
    return rows


def add(full_name, role, shift, phone):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO staff (full_name, role, shift, phone, created_at) VALUES (?,?,?,?,?)",
                (full_name, role, shift, phone, now()))
    new_id = cur.lastrowid
    log_audit(conn, "staff", new_id, "INSERT", f"Added staff '{full_name}'")
    conn.commit()
    conn.close()
    return new_id


def update(staff_id, full_name, role, shift, phone):
    conn = get_connection()
    conn.execute("UPDATE staff SET full_name=?, role=?, shift=?, phone=? WHERE staff_id=?",
                 (full_name, role, shift, phone, staff_id))
    log_audit(conn, "staff", staff_id, "UPDATE", "Staff record updated")
    conn.commit()
    conn.close()


def delete(staff_id):
    conn = get_connection()
    conn.execute("DELETE FROM staff WHERE staff_id=?", (staff_id,))
    log_audit(conn, "staff", staff_id, "DELETE", "Staff record deleted")
    conn.commit()
    conn.close()
