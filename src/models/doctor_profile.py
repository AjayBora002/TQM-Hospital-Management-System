"""
doctor_profile.py -- Data-access functions for Doctor Credentials & Specializations.
Enriches the baseline doctor records with clinical specialty, qualifications,
consultation fees, room numbers, and OPD slot capacities.
"""
from datetime import datetime
from database.db_manager import get_connection, log_audit
from utils.exception_handler import ValidationError


def list_specialized_doctors(department: str = None):
    """
    Returns doctors enriched with their professional profile data.
    Optionally filters by department name.
    """
    conn = get_connection()
    try:
        query = """
            SELECT d.doctor_id, d.full_name, d.department, d.phone,
                   COALESCE(dp.specialization, 'General Specialist') AS specialization,
                   COALESCE(dp.qualifications, 'MBBS, MD') AS qualifications,
                   COALESCE(dp.experience_years, 5) AS experience_years,
                   COALESCE(dp.consultation_fee, 500.0) AS consultation_fee,
                   COALESCE(dp.room_number, 'OPD-101') AS room_number,
                   COALESCE(dp.max_daily_patients, 30) AS max_daily_patients,
                   COALESCE(dp.is_available, 1) AS is_available,
                   u.username AS linked_username
            FROM doctors d
            LEFT JOIN doctor_profiles dp ON dp.doctor_id = d.doctor_id
            LEFT JOIN users u ON u.user_id = dp.user_id
        """
        params = []
        if department:
            query += " WHERE d.department = ?"
            params.append(department)

        query += " ORDER BY d.department, d.full_name"
        rows = conn.execute(query, tuple(params)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_doctor_profile(doctor_id: int):
    """Retrieves full profile for a specific doctor ID."""
    conn = get_connection()
    try:
        row = conn.execute("""
            SELECT d.doctor_id, d.full_name, d.department, d.phone,
                   dp.profile_id, dp.specialization, dp.qualifications,
                   dp.experience_years, dp.consultation_fee, dp.room_number,
                   dp.max_daily_patients, dp.is_available, dp.user_id
            FROM doctors d
            LEFT JOIN doctor_profiles dp ON dp.doctor_id = d.doctor_id
            WHERE d.doctor_id = ?
        """, (doctor_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def save_profile(doctor_id: int, specialization: str, qualifications: str,
                 experience_years: int = 5, consultation_fee: float = 500.0,
                 room_number: str = "OPD-101", max_daily_patients: int = 30,
                 is_available: int = 1, user_id: int = None, performed_by: str = "admin"):
    """Creates or updates a doctor's specialized clinical profile."""
    if not specialization or not specialization.strip():
        raise ValidationError("Specialization is required", field="specialization")
    if not qualifications or not qualifications.strip():
        raise ValidationError("Qualifications are required", field="qualifications")
    if consultation_fee < 0:
        raise ValidationError("Consultation fee cannot be negative", field="consultation_fee")

    conn = get_connection()
    try:
        existing = conn.execute("SELECT profile_id FROM doctor_profiles WHERE doctor_id = ?", (doctor_id,)).fetchone()
        if existing:
            conn.execute("""
                UPDATE doctor_profiles 
                SET specialization=?, qualifications=?, experience_years=?, consultation_fee=?,
                    room_number=?, max_daily_patients=?, is_available=?, user_id=?
                WHERE doctor_id=?
            """, (specialization.strip(), qualifications.strip(), experience_years, consultation_fee,
                  room_number.strip(), max_daily_patients, is_available, user_id, doctor_id))
            log_audit(conn, "doctor_profiles", existing["profile_id"], "UPDATE", f"Updated profile for doctor #{doctor_id}", performed_by)
            conn.commit()
            return existing["profile_id"]
        else:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO doctor_profiles (doctor_id, user_id, specialization, qualifications, experience_years, consultation_fee, room_number, max_daily_patients, is_available)
                VALUES (?,?,?,?,?,?,?,?,?)
            """, (doctor_id, user_id, specialization.strip(), qualifications.strip(), experience_years,
                  consultation_fee, room_number.strip(), max_daily_patients, is_available))
            new_id = cursor.lastrowid
            log_audit(conn, "doctor_profiles", new_id, "INSERT", f"Created profile for doctor #{doctor_id}", performed_by)
            conn.commit()
            return new_id
    finally:
        conn.close()

