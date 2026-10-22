"""appointment.py -- Data-access functions for the appointments table."""
from datetime import datetime
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_manager import get_connection, log_audit  # noqa: E402


def now():
    return datetime.now().isoformat(timespec="seconds")


def list_all():
    conn = get_connection()
    rows = conn.execute("""
        SELECT a.appointment_id, p.full_name AS patient, d.full_name AS doctor,
               a.appt_date, a.appt_time, a.status
        FROM appointments a
        JOIN patients p ON p.patient_id = a.patient_id
        JOIN doctors d ON d.doctor_id = a.doctor_id
        ORDER BY a.appointment_id DESC
    """).fetchall()
    conn.close()
    return rows


def add(patient_id, doctor_id, appt_date, appt_time, status="Scheduled"):
    from utils.validators import validate_appointment_payload
    validate_appointment_payload({
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "appt_date": appt_date,
        "appt_time": appt_time,
        "status": status
    })
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO appointments (patient_id, doctor_id, appt_date, appt_time, status, created_at) "
        "VALUES (?,?,?,?,?,?)",
        (patient_id, doctor_id, appt_date, appt_time, status, now())
    )
    new_id = cur.lastrowid
    log_audit(conn, "appointments", new_id, "INSERT", "Appointment booked")
    conn.commit()
    conn.close()
    return new_id


def update(appointment_id, patient_id, doctor_id, appt_date, appt_time, status):
    from utils.validators import validate_appointment_payload
    validate_appointment_payload({
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "appt_date": appt_date,
        "appt_time": appt_time,
        "status": status
    })
    conn = get_connection()
    conn.execute(
        "UPDATE appointments SET patient_id=?, doctor_id=?, appt_date=?, appt_time=?, status=? "
        "WHERE appointment_id=?",
        (patient_id, doctor_id, appt_date, appt_time, status, appointment_id)
    )
    log_audit(conn, "appointments", appointment_id, "UPDATE", "Appointment updated")
    conn.commit()
    conn.close()


def delete(appointment_id):
    conn = get_connection()
    conn.execute("DELETE FROM appointments WHERE appointment_id=?", (appointment_id,))
    log_audit(conn, "appointments", appointment_id, "DELETE", "Appointment deleted")
    conn.commit()
    conn.close()


def has_conflict(doctor_id, appt_date, appt_time, exclude_id=None):
    """Poka-Yoke: Check if the doctor already has an active appointment at this date & time."""
    conn = get_connection()
    query = """
        SELECT a.appointment_id, p.full_name AS patient, d.full_name AS doctor, a.appt_date, a.appt_time
        FROM appointments a
        JOIN patients p ON p.patient_id = a.patient_id
        JOIN doctors d ON d.doctor_id = a.doctor_id
        WHERE a.doctor_id = ? AND a.appt_date = ? AND a.appt_time = ? AND a.status != 'Cancelled'
    """
    params = [doctor_id, appt_date, appt_time]
    if exclude_id:
        query += " AND a.appointment_id != ?"
        params.append(exclude_id)

    row = conn.execute(query, tuple(params)).fetchone()
    conn.close()
    return row


def has_patient_conflict(patient_id, appt_date, appt_time, exclude_id=None):
    """Poka-Yoke: Check if patient is already booked for another appointment at the same slot."""
    conn = get_connection()
    query = """
        SELECT a.appointment_id, d.full_name AS doctor, a.appt_date, a.appt_time
        FROM appointments a
        JOIN doctors d ON d.doctor_id = a.doctor_id
        WHERE a.patient_id = ? AND a.appt_date = ? AND a.appt_time = ? AND a.status != 'Cancelled'
    """
    params = [patient_id, appt_date, appt_time]
    if exclude_id:
        query += " AND a.appointment_id != ?"
        params.append(exclude_id)

    row = conn.execute(query, tuple(params)).fetchone()
    conn.close()
    return row


def get_doctor_booked_slots(doctor_id, appt_date):
    """Fetch all confirmed or scheduled time slots for a doctor on a specific date."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT appt_time FROM appointments WHERE doctor_id=? AND appt_date=? AND status != 'Cancelled'",
        (doctor_id, appt_date)
    ).fetchall()
    conn.close()
    return [r["appt_time"] for r in rows]


def get_doctor_available_slots(doctor_id, appt_date):
    """Return status of all standard slots for a given doctor on a date."""
    from config import STANDARD_APPOINTMENT_SLOTS
    booked = set(get_doctor_booked_slots(doctor_id, appt_date))
    return [
        {"slot": slot, "available": slot not in booked}
        for slot in STANDARD_APPOINTMENT_SLOTS
    ]

