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


def add(patient_id, doctor_id, appt_date, appt_time, status):
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
