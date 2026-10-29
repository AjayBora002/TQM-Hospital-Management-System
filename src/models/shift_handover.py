"""
shift_handover.py -- NABH Shift Handover Protocol & Audit Tracking.
Records outgoing nurse summary, critical care alerts, pending clinical tasks,
and incoming nurse verification.
"""
from datetime import datetime
from database.db_manager import get_connection, log_audit
from utils.exception_handler import ValidationError


def create_handover(department: str, shift_from: str, shift_to: str,
                    outgoing_nurse: str, incoming_nurse: str,
                    critical_patients: str, pending_orders: str,
                    general_notes: str = "", ward_id: int = None):
    """
    Records a formal shift handover between nursing staff.
    """
    if not outgoing_nurse or not outgoing_nurse.strip():
        raise ValidationError("Outgoing nurse name is required", field="outgoing_nurse")
    if not incoming_nurse or not incoming_nurse.strip():
        raise ValidationError("Incoming nurse name is required", field="incoming_nurse")

    today_str = datetime.now().strftime("%Y-%m-%d")
    now_str = datetime.now().isoformat(timespec="seconds")

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO shift_handovers 
            (ward_id, department, shift_from, shift_to, handover_date, outgoing_nurse_name, incoming_nurse_name, critical_patients, pending_orders, general_notes, status, created_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,'Completed',?)
        """, (ward_id, department.strip(), shift_from, shift_to, today_str,
              outgoing_nurse.strip(), incoming_nurse.strip(),
              critical_patients.strip(), pending_orders.strip(), general_notes.strip(), now_str))

        new_id = cursor.lastrowid
        log_audit(conn, "shift_handovers", new_id, "INSERT", f"Shift handover from {outgoing_nurse} to {incoming_nurse} in {department}", outgoing_nurse)
        conn.commit()
        return new_id
    finally:
        conn.close()


def list_handovers(department: str = None, ward_id: int = None, limit: int = 20):
    """
    Lists shift handover logs for inspection and quality auditing.
    """
    conn = get_connection()
    try:
        query = """
            SELECT sh.handover_id, sh.ward_id, sh.department, sh.shift_from, sh.shift_to,
                   sh.handover_date, sh.outgoing_nurse_name, sh.incoming_nurse_name,
                   sh.critical_patients, sh.pending_orders, sh.general_notes,
                   sh.status, sh.created_at,
                   w.name AS ward_name
            FROM shift_handovers sh
            LEFT JOIN wards w ON w.ward_id = sh.ward_id
            WHERE 1=1
        """
        params = []
        if department:
            query += " AND sh.department = ?"
            params.append(department)
        if ward_id:
            query += " AND sh.ward_id = ?"
            params.append(ward_id)

        query += " ORDER BY sh.handover_id DESC LIMIT ?"
        params.append(limit)

        rows = conn.execute(query, tuple(params)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

