"""
nursing.py -- Nursing Station & Ward Inpatient Care Operations.
Manages nurse assignments, ward round schedules, and vital charting.
"""
from datetime import datetime
from database.db_manager import get_connection, log_audit
from utils.exception_handler import ValidationError


def list_nurses(department: str = None, ward_id: int = None):
    """
    Returns nurses roster with their assigned ward and shift.
    """
    conn = get_connection()
    try:
        query = """
            SELECT np.nurse_profile_id, np.staff_id, np.user_id, np.ward_id,
                   np.department, np.shift, np.qualifications, np.assigned_patients,
                   u.full_name, u.username, u.email,
                   w.name AS ward_name, w.floor_number
            FROM nurse_profiles np
            JOIN users u ON u.user_id = np.user_id
            LEFT JOIN wards w ON w.ward_id = np.ward_id
            WHERE 1=1
        """
        params = []
        if department:
            query += " AND np.department = ?"
            params.append(department)
        if ward_id:
            query += " AND np.ward_id = ?"
            params.append(ward_id)

        rows = conn.execute(query, tuple(params)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_ward_inpatients(ward_id: int = None):
    """
    Fetches currently admitted patients in a ward for nursing care and vitals monitoring.
    """
    conn = get_connection()
    try:
        query = """
            SELECT a.admission_id, a.patient_id, a.room_id, a.admission_date, a.diagnosis,
                   p.full_name AS patient_name, p.gender, p.dob, p.blood_group,
                   p.phone, p.allergies,
                   r.room_number, r.room_type, r.ward_id,
                   w.name AS ward_name,
                   (SELECT COUNT(*) FROM clinical_orders co WHERE co.patient_id = a.patient_id AND co.status IN ('Ordered', 'Acknowledged')) AS pending_orders_count
            FROM admissions a
            JOIN patients p ON p.patient_id = a.patient_id
            JOIN rooms r ON r.room_id = a.room_id
            LEFT JOIN wards w ON w.ward_id = r.ward_id
            WHERE a.status = 'Admitted'
        """
        params = []
        if ward_id:
            query += " AND r.ward_id = ?"
            params.append(ward_id)

        query += " ORDER BY r.room_number"
        rows = conn.execute(query, tuple(params)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

