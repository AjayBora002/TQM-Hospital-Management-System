"""
clinical_order.py -- Doctor-to-Nurse Clinical Orders & Execution Workflow.
Implements clinical order entry, STAT prioritization, nursing task acknowledgment,
and closed-loop execution tracking.
"""
from datetime import datetime
from database.db_manager import get_connection, log_audit
from utils.exception_handler import ValidationError
import config


def create_order(patient_id: int, doctor_id: int, doctor_name: str, order_type: str,
                 order_text: str, urgency: str = "Routine", ward_id: int = None,
                 bed_number: str = None, performed_by: str = "doctor"):
    """
    Creates a new doctor clinical order directed to the nursing station.
    Validates order type and urgency.
    """
    if not order_text or not order_text.strip():
        raise ValidationError("Order instructions / text cannot be empty", field="order_text")
    if order_type not in config.ORDER_TYPES:
        raise ValidationError(f"Invalid order type '{order_type}'. Allowed: {config.ORDER_TYPES}", field="order_type")
    if urgency not in config.ORDER_URGENCIES:
        raise ValidationError(f"Invalid urgency '{urgency}'. Allowed: {config.ORDER_URGENCIES}", field="urgency")

    conn = get_connection()
    try:
        # Resolve patient room if bed_number is not explicitly provided
        if not bed_number:
            p_row = conn.execute("SELECT r.room_number, r.ward_id FROM patients p LEFT JOIN rooms r ON r.room_id = p.room_id WHERE p.patient_id = ?", (patient_id,)).fetchone()
            if p_row and p_row["room_number"]:
                bed_number = p_row["room_number"]
                if not ward_id:
                    ward_id = p_row["ward_id"]

        now_str = datetime.now().isoformat(timespec="seconds")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO clinical_orders (patient_id, doctor_id, doctor_name, order_type, order_text, urgency, status, ward_id, bed_number, ordered_at)
            VALUES (?,?,?,?,?,?,'Ordered',?,?,?)
        """, (patient_id, doctor_id, doctor_name.strip(), order_type, order_text.strip(), urgency, ward_id, bed_number, now_str))

        new_id = cursor.lastrowid
        log_audit(conn, "clinical_orders", new_id, "INSERT", f"Doctor placed {urgency} {order_type} order for patient #{patient_id}", performed_by)
        conn.commit()
        return new_id
    finally:
        conn.close()


def list_orders(patient_id: int = None, ward_id: int = None, status: str = None, urgency: str = None):
    """
    Lists clinical orders with rich patient and ward metadata.
    Supports filtering by patient, ward, status, and urgency.
    """
    conn = get_connection()
    try:
        query = """
            SELECT co.order_id, co.patient_id, co.doctor_id, co.doctor_name,
                   co.order_type, co.order_text, co.urgency, co.status,
                   co.ward_id, co.bed_number, co.ordered_at,
                   co.acknowledged_by, co.acknowledged_at,
                   co.completed_by, co.completed_at, co.execution_notes,
                   p.full_name AS patient_name, p.phone AS patient_phone,
                   w.name AS ward_name
            FROM clinical_orders co
            JOIN patients p ON p.patient_id = co.patient_id
            LEFT JOIN wards w ON w.ward_id = co.ward_id
            WHERE 1=1
        """
        params = []
        if patient_id:
            query += " AND co.patient_id = ?"
            params.append(patient_id)
        if ward_id:
            query += " AND co.ward_id = ?"
            params.append(ward_id)
        if status:
            query += " AND co.status = ?"
            params.append(status)
        if urgency:
            query += " AND co.urgency = ?"
            params.append(urgency)

        # STAT orders always sorted to the very top, then by most recent
        query += " ORDER BY CASE WHEN co.urgency = 'STAT (Immediate)' THEN 0 WHEN co.urgency = 'Urgent' THEN 1 ELSE 2 END, co.order_id DESC"

        rows = conn.execute(query, tuple(params)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def acknowledge_order(order_id: int, nurse_name: str):
    """Nurse acknowledges receipt of doctor's clinical order."""
    if not nurse_name or not nurse_name.strip():
        nurse_name = "Sister Sunita Patel"

    conn = get_connection()
    try:
        now_str = datetime.now().isoformat(timespec="seconds")
        conn.execute("""
            UPDATE clinical_orders
            SET status = 'Acknowledged', acknowledged_by = ?, acknowledged_at = ?
            WHERE order_id = ? AND status = 'Ordered'
        """, (nurse_name.strip(), now_str, order_id))

        log_audit(conn, "clinical_orders", order_id, "UPDATE", f"Nurse '{nurse_name}' acknowledged order #{order_id}", nurse_name)
        conn.commit()
        return True
    finally:
        conn.close()


def complete_order(order_id: int, nurse_name: str, execution_notes: str = ""):
    """Nurse confirms administration/execution of clinical order."""
    if not nurse_name or not nurse_name.strip():
        nurse_name = "Sister Sunita Patel"

    conn = get_connection()
    try:
        now_str = datetime.now().isoformat(timespec="seconds")
        conn.execute("""
            UPDATE clinical_orders
            SET status = 'Completed', completed_by = ?, completed_at = ?, execution_notes = ?
            WHERE order_id = ?
        """, (nurse_name.strip(), now_str, execution_notes.strip(), order_id))

        log_audit(conn, "clinical_orders", order_id, "UPDATE", f"Nurse '{nurse_name}' completed order #{order_id}: {execution_notes}", nurse_name)
        conn.commit()
        return True
    finally:
        conn.close()

