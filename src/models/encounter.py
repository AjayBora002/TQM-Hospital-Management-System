"""
encounter.py -- Outpatient Clinical Encounters & SOAP Consultation Notes.
Supports structured clinical documentation, chief complaints, physical examination,
provisional diagnoses, and follow-up scheduling.
"""
from datetime import datetime
from database.db_manager import get_connection, log_audit
from utils.exception_handler import ValidationError


def create_encounter(patient_id: int, doctor_id: int, chief_complaint: str, diagnosis: str,
                     appointment_id: int = None, history_illness: str = "", examination: str = "",
                     plan: str = "", doctor_notes: str = "", follow_up_date: str = None,
                     performed_by: str = "doctor"):
    """
    Records a clinical encounter / consultation note.
    """
    if not chief_complaint or not chief_complaint.strip():
        raise ValidationError("Chief complaint cannot be empty", field="chief_complaint")
    if not diagnosis or not diagnosis.strip():
        raise ValidationError("Diagnosis cannot be empty", field="diagnosis")

    today_str = datetime.now().strftime("%Y-%m-%d")
    now_str = datetime.now().isoformat(timespec="seconds")

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO encounters 
            (patient_id, doctor_id, appointment_id, encounter_date, chief_complaint, history_illness, examination, diagnosis, plan, doctor_notes, follow_up_date, created_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
        """, (patient_id, doctor_id, appointment_id, today_str,
              chief_complaint.strip(), history_illness.strip(),
              examination.strip(), diagnosis.strip(), plan.strip(),
              doctor_notes.strip(), follow_up_date, now_str))

        new_id = cursor.lastrowid
        log_audit(conn, "encounters", new_id, "INSERT", f"Clinical consultation recorded for patient #{patient_id}: {diagnosis}", performed_by)
        conn.commit()
        return new_id
    finally:
        conn.close()


def get_patient_encounters(patient_id: int):
    """
    Returns clinical encounter history for a specific patient.
    """
    conn = get_connection()
    try:
        rows = conn.execute("""
            SELECT e.encounter_id, e.patient_id, e.doctor_id, e.encounter_date,
                   e.chief_complaint, e.history_illness, e.examination,
                   e.diagnosis, e.plan, e.doctor_notes, e.follow_up_date,
                   d.full_name AS doctor_name, d.department
            FROM encounters e
            JOIN doctors d ON d.doctor_id = e.doctor_id
            WHERE e.patient_id = ?
            ORDER BY e.encounter_id DESC
        """, (patient_id,)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

