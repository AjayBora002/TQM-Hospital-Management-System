"""
opd_queue.py -- Real-time OPD Token Queue Engine & Waiting Room Display.
Generates daily tokens, tracks patient progression from intake to consultation,
and feeds digital waiting room displays.
"""
from datetime import datetime
from database.db_manager import get_connection, log_audit
from utils.exception_handler import ValidationError


def generate_token(patient_id: int, doctor_id: int, appointment_id: int = None,
                   priority: str = "Normal", performed_by: str = "receptionist"):
    """
    Issues an incremental daily OPD token for a patient seeing a specific doctor.
    Enforces same-day unique token ordering.
    """
    today_str = datetime.now().strftime("%Y-%m-%d")
    now_str = datetime.now().isoformat(timespec="seconds")

    conn = get_connection()
    try:
        # Check if already queued for this doctor today
        existing = conn.execute(
            "SELECT token_number, status FROM opd_queue WHERE patient_id = ? AND doctor_id = ? AND queue_date = ? AND status != 'Completed'",
            (patient_id, doctor_id, today_str)
        ).fetchone()
        if existing:
            return {"token_number": existing["token_number"], "status": existing["status"], "already_queued": True}

        # Calculate next token number for this doctor today
        last_token = conn.execute(
            "SELECT MAX(token_number) as max_tok FROM opd_queue WHERE doctor_id = ? AND queue_date = ?",
            (doctor_id, today_str)
        ).fetchone()["max_tok"]

        next_token = (last_token or 0) + 1

        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO opd_queue (appointment_id, patient_id, doctor_id, token_number, queue_date, status, check_in_time, priority)
            VALUES (?,?,?,?,?,?,?,?)
        """, (appointment_id, patient_id, doctor_id, next_token, today_str, 'Waiting', now_str, priority))

        new_id = cursor.lastrowid
        log_audit(conn, "opd_queue", new_id, "INSERT", f"Generated Token #{next_token} for patient #{patient_id} (Doctor #{doctor_id})", performed_by)
        conn.commit()
        return {"queue_id": new_id, "token_number": next_token, "status": "Waiting", "already_queued": False}
    finally:
        conn.close()


def get_today_queue(doctor_id: int = None, date_str: str = None):
    """
    Returns today's active patient queue for a doctor or whole hospital.
    """
    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")

    conn = get_connection()
    try:
        query = """
            SELECT q.queue_id, q.token_number, q.queue_date, q.status, q.check_in_time,
                   q.call_time, q.complete_time, q.priority,
                   p.patient_id, p.full_name AS patient_name, p.gender, p.blood_group, p.phone,
                   d.doctor_id, d.full_name AS doctor_name, d.department,
                   dp.room_number AS opd_room
            FROM opd_queue q
            JOIN patients p ON p.patient_id = q.patient_id
            JOIN doctors d ON d.doctor_id = q.doctor_id
            LEFT JOIN doctor_profiles dp ON dp.doctor_id = d.doctor_id
            WHERE q.queue_date = ?
        """
        params = [date_str]
        if doctor_id:
            query += " AND q.doctor_id = ?"
            params.append(doctor_id)

        # Urgent / Emergency priority tokens first, then by token number
        query += " ORDER BY CASE WHEN q.priority = 'Emergency' THEN 0 WHEN q.priority = 'Urgent' THEN 1 ELSE 2 END, q.token_number ASC"

        rows = conn.execute(query, tuple(params)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def call_patient(queue_id: int, performed_by: str = "doctor"):
    """Doctor or Nurse calls the token into the consultation room."""
    conn = get_connection()
    try:
        now_str = datetime.now().isoformat(timespec="seconds")
        conn.execute("""
            UPDATE opd_queue 
            SET status = 'Called', call_time = ?
            WHERE queue_id = ?
        """, (now_str, queue_id))
        log_audit(conn, "opd_queue", queue_id, "UPDATE", "Token status changed to 'Called'", performed_by)
        conn.commit()
        return True
    finally:
        conn.close()


def complete_consultation(queue_id: int, performed_by: str = "doctor"):
    """Marks consultation as completed for this queue token."""
    conn = get_connection()
    try:
        now_str = datetime.now().isoformat(timespec="seconds")
        conn.execute("""
            UPDATE opd_queue 
            SET status = 'Completed', complete_time = ?
            WHERE queue_id = ?
        """, (now_str, queue_id))
        log_audit(conn, "opd_queue", queue_id, "UPDATE", "Token status changed to 'Completed'", performed_by)
        conn.commit()
        return True
    finally:
        conn.close()

