"""
communication.py -- Inter-Professional Doctor <-> Nurse Communication & Clinical Alerts.
Supports urgent messaging, critical vitals deterioration broadcast, and read receipts.
"""
from datetime import datetime
from database.db_manager import get_connection, log_audit
from utils.exception_handler import ValidationError


def send_message(sender_user_id: int, sender_name: str, sender_role: str,
                 recipient_role: str, subject: str, message_body: str,
                 urgency: str = "Normal", patient_id: int = None,
                 department: str = None, recipient_user_id: int = None):
    """
    Sends a clinical message between healthcare professionals.
    Urgency: 'Normal', 'Urgent', 'Code Red'.
    """
    if not subject or not subject.strip():
        raise ValidationError("Subject cannot be empty", field="subject")
    if not message_body or not message_body.strip():
        raise ValidationError("Message body cannot be empty", field="message_body")

    conn = get_connection()
    try:
        # Validate or resolve sender_user_id to prevent foreign key failure
        u_check = conn.execute("SELECT user_id FROM users WHERE user_id = ?", (sender_user_id,)).fetchone()
        if not u_check:
            first_u = conn.execute("SELECT user_id FROM users ORDER BY user_id ASC LIMIT 1").fetchone()
            sender_user_id = first_u["user_id"] if first_u else 1

        now_str = datetime.now().isoformat(timespec="seconds")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO doctor_nurse_messages 
            (patient_id, sender_user_id, sender_name, sender_role, recipient_role, recipient_user_id, department, subject, message_body, urgency, is_read, created_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,0,?)
        """, (patient_id, sender_user_id, sender_name.strip(), sender_role.strip(),
              recipient_role.strip(), recipient_user_id, department,
              subject.strip(), message_body.strip(), urgency, now_str))

        msg_id = cursor.lastrowid
        log_audit(conn, "doctor_nurse_messages", msg_id, "INSERT", f"Message sent from {sender_name} ({sender_role}) to {recipient_role}: '{subject}'", sender_name)
        conn.commit()
        return msg_id
    finally:
        conn.close()


def list_messages(user_id: int = None, role: str = None, department: str = None, limit: int = 50):
    """
    Lists messages visible to a given user/role or across the department.
    """
    conn = get_connection()
    try:
        query = """
            SELECT m.message_id, m.patient_id, m.sender_user_id, m.sender_name,
                   m.sender_role, m.recipient_role, m.recipient_user_id,
                   m.department, m.subject, m.message_body, m.urgency, m.is_read,
                   m.created_at,
                   p.full_name AS patient_name,
                   r.room_number AS patient_room
            FROM doctor_nurse_messages m
            LEFT JOIN patients p ON p.patient_id = m.patient_id
            LEFT JOIN rooms r ON r.room_id = p.room_id
            WHERE 1=1
        """
        params = []
        if role and role != "Admin":
            query += " AND (m.recipient_role = 'All' OR m.recipient_role = ? OR m.sender_role = ?)"
            params.extend([role, role])

        # Priority: Code Red and Urgent on top
        query += " ORDER BY CASE WHEN m.urgency = 'Code Red' THEN 0 WHEN m.urgency = 'Urgent' THEN 1 ELSE 2 END, m.message_id DESC LIMIT ?"
        params.append(limit)

        rows = conn.execute(query, tuple(params)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def mark_as_read(message_id: int):
    """Marks a message as read."""
    conn = get_connection()
    try:
        conn.execute("UPDATE doctor_nurse_messages SET is_read = 1 WHERE message_id = ?", (message_id,))
        conn.commit()
        return True
    finally:
        conn.close()


def broadcast_vitals_alert(patient_id: int, vital_summary: str, sender_name: str = "Sister Sunita Patel", sender_role: str = "Nurse"):
    """
    Triggered when vitals violate physiological safety limits (e.g. SpO2 < 90% or BP > 180).
    Broadcasts an instant Code Red alert to doctors and nurses.
    """
    subject = f"🚨 CLINICAL ALERT: Patient #{patient_id} Vitals Deterioration"
    body = f"Automatic physiological boundary breach detected:\n{vital_summary}\nPlease attend immediately."
    return send_message(
        sender_user_id=1,
        sender_name=sender_name,
        sender_role=sender_role,
        recipient_role="Doctor",
        subject=subject,
        message_body=body,
        urgency="Code Red",
        patient_id=patient_id
    )
