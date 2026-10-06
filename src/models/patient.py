"""patient.py -- Data-access functions for the patients table."""
from datetime import datetime
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_manager import get_connection, log_audit  # noqa: E402


def now():
    return datetime.now().isoformat(timespec="seconds")


def list_all(name_filter=""):
    conn = get_connection()
    query = """
        SELECT p.*, r.room_number, r.room_type, r.status AS room_status
        FROM patients p
        LEFT JOIN rooms r ON p.room_id = r.room_id
    """
    if name_filter:
        query += " WHERE p.full_name LIKE ? ORDER BY p.patient_id DESC"
        rows = conn.execute(query, (f"%{name_filter}%",)).fetchall()
    else:
        query += " ORDER BY p.patient_id DESC"
        rows = conn.execute(query).fetchall()
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


def get_by_id(patient_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT p.*, r.room_number, r.room_type, r.rate_per_day, r.status AS room_status "
        "FROM patients p "
        "LEFT JOIN rooms r ON p.room_id = r.room_id "
        "WHERE p.patient_id = ?",
        (patient_id,)
    ).fetchone()
    conn.close()
    return row


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
    if room_id:
        cur.execute("UPDATE rooms SET status='Occupied' WHERE room_id=?", (room_id,))
        log_audit(conn, "rooms", room_id, "UPDATE", f"Bed allocated (Occupied) for admitted patient '{full_name}'")
    conn.commit()
    conn.close()
    return new_id


def update(patient_id, full_name, gender, dob, blood_group, phone, address, room_id=None):
    conn = get_connection()
    cur = conn.cursor()
    old = cur.execute("SELECT room_id, full_name FROM patients WHERE patient_id=?", (patient_id,)).fetchone()
    old_room_id = old["room_id"] if old else None

    cur.execute(
        "UPDATE patients SET full_name=?, gender=?, dob=?, blood_group=?, phone=?, address=?, "
        "room_id=?, updated_at=? WHERE patient_id=?",
        (full_name, gender, dob, blood_group, phone, address, room_id, now(), patient_id)
    )
    log_audit(conn, "patients", patient_id, "UPDATE", "Patient record updated")

    # Automated bed allocation & clearance on room reassignment
    if old_room_id != room_id:
        if old_room_id:
            cur.execute("UPDATE rooms SET status='Available' WHERE room_id=?", (old_room_id,))
            log_audit(conn, "rooms", old_room_id, "UPDATE",
                      f"Automated bed clearance: Room freed (Available) on patient room transfer")
        if room_id:
            cur.execute("UPDATE rooms SET status='Occupied' WHERE room_id=?", (room_id,))
            log_audit(conn, "rooms", room_id, "UPDATE",
                      f"Bed allocated (Occupied) for admitted patient '{full_name}'")

    conn.commit()
    conn.close()


def delete(patient_id):
    conn = get_connection()
    cur = conn.cursor()
    row = cur.execute("SELECT room_id, full_name FROM patients WHERE patient_id=?", (patient_id,)).fetchone()
    if row and row["room_id"]:
        cur.execute("UPDATE rooms SET status='Available' WHERE room_id=?", (row["room_id"],))
        log_audit(conn, "rooms", row["room_id"], "UPDATE",
                  f"Automated bed clearance: Room freed (Available) due to deletion of patient '{row['full_name']}'")

    cur.execute("DELETE FROM patients WHERE patient_id=?", (patient_id,))
    log_audit(conn, "patients", patient_id, "DELETE", "Patient record deleted")
    conn.commit()
    conn.close()


def get_discharge_summary(patient_id):
    conn = get_connection()
    patient = conn.execute(
        "SELECT p.*, r.room_number, r.room_type, r.rate_per_day "
        "FROM patients p LEFT JOIN rooms r ON p.room_id = r.room_id "
        "WHERE p.patient_id = ?",
        (patient_id,)
    ).fetchone()
    if not patient:
        conn.close()
        return None

    bills = conn.execute(
        "SELECT * FROM bills WHERE patient_id = ? ORDER BY bill_id DESC",
        (patient_id,)
    ).fetchall()
    conn.close()

    total_billed = sum(b["total_amount"] for b in bills)
    total_paid = sum(b["total_amount"] for b in bills if b["payment_status"] == "Paid")
    unpaid_bills = [b for b in bills if b["payment_status"] != "Paid"]

    return {
        "patient_id": patient["patient_id"],
        "full_name": patient["full_name"],
        "gender": patient["gender"],
        "dob": patient["dob"],
        "blood_group": patient["blood_group"],
        "phone": patient["phone"],
        "admission_date": patient["created_at"],
        "room_id": patient["room_id"],
        "room_number": patient["room_number"],
        "room_type": patient["room_type"],
        "rate_per_day": patient["rate_per_day"],
        "total_billed": round(total_billed, 2),
        "total_paid": round(total_paid, 2),
        "balance_due": round(total_billed - total_paid, 2),
        "has_unpaid_bills": len(unpaid_bills) > 0,
        "is_admitted": bool(patient["room_id"])
    }


def discharge(patient_id, discharge_notes="", room_status_after="Available"):
    conn = get_connection()
    cur = conn.cursor()
    row = cur.execute(
        "SELECT p.*, r.room_number FROM patients p LEFT JOIN rooms r ON p.room_id = r.room_id WHERE p.patient_id = ?",
        (patient_id,)
    ).fetchone()
    if not row:
        conn.close()
        return None

    room_id = row["room_id"]
    room_num = row["room_number"]
    full_name = row["full_name"]
    discharge_time = now()

    # Clear patient room assignment
    cur.execute(
        "UPDATE patients SET room_id = NULL, updated_at = ? WHERE patient_id = ?",
        (discharge_time, patient_id)
    )

    details = f"Discharged patient '{full_name}'."
    if room_num:
        details += f" Released Room #{room_num} (marked as {room_status_after})."
    if discharge_notes:
        details += f" Advice: {discharge_notes}"

    log_audit(conn, "patients", patient_id, "UPDATE", details)

    # Automated bed clearance
    if room_id:
        cur.execute("UPDATE rooms SET status = ? WHERE room_id = ?", (room_status_after, room_id))
        log_audit(conn, "rooms", room_id, "UPDATE",
                  f"Automated bed clearance: Room #{room_num} set to '{room_status_after}' upon patient discharge")

    conn.commit()
    conn.close()

    return {
        "patient_id": patient_id,
        "full_name": full_name,
        "freed_room_id": room_id,
        "freed_room_number": room_num,
        "room_status_after": room_status_after,
        "discharge_time": discharge_time,
        "notes": discharge_notes
    }

