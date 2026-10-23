"""
admission.py -- Model for Inpatient Admission and Discharge Stay Tracking.
Connects bed allocations directly to timed clinical stays with audit trails.
"""
from datetime import datetime
from database.db_manager import get_connection, log_audit
from utils.exception_handler import ValidationError


def _now():
    return datetime.now().isoformat(timespec="seconds")


def admit_patient(patient_id: int, room_id: int, admission_date=None, diagnosis="", performed_by="front_desk_user"):
    """
    Admits a patient to a specified room/ward.
    Updates room status to 'Occupied' and patient record with room_id.
    """
    if not patient_id:
        raise ValidationError("Patient ID is required", field="patient_id")
    if not room_id:
        raise ValidationError("Room ID is required", field="room_id")

    from utils.validators import is_valid_date
    admission_date = str(admission_date or _now()[:10]).strip()
    if not is_valid_date(admission_date):
        raise ValidationError("Admission date must be in YYYY-MM-DD format", field="admission_date")
    today_str = _now()[:10]
    if admission_date > today_str:
        raise ValidationError(f"Admission date cannot be in the future ({admission_date} > {today_str})", field="admission_date")

    conn = get_connection()
    try:
        # Verify patient exists
        p = conn.execute("SELECT patient_id, full_name, room_id FROM patients WHERE patient_id = ?", (patient_id,)).fetchone()
        if not p:
            raise ValidationError(f"Patient #{patient_id} not found", field="patient_id")
        if p["room_id"]:
            # Check if active admission already exists
            active = conn.execute(
                "SELECT admission_id FROM admissions WHERE patient_id = ? AND status = 'Admitted'",
                (patient_id,)
            ).fetchone()
            if active:
                raise ValidationError(f"Patient is already admitted (Stay #{active['admission_id']})", field="patient_id")

        # Verify room exists and is available
        r = conn.execute("SELECT room_id, room_number, status, rate_per_day FROM rooms WHERE room_id = ?", (room_id,)).fetchone()
        if not r:
            raise ValidationError(f"Room #{room_id} not found", field="room_id")
        if r["status"] == "Occupied":
            raise ValidationError(f"Room #{r['room_number']} is currently occupied", field="room_id")

        cursor = conn.cursor()
        now_ts = _now()
        # 1. Create admission stay record
        cursor.execute(
            "INSERT INTO admissions (patient_id, room_id, admission_date, status, diagnosis, created_at) "
            "VALUES (?,?,?, 'Admitted', ?, ?)",
            (patient_id, room_id, admission_date, (diagnosis or "").strip(), now_ts)
        )
        admission_id = cursor.lastrowid

        # 2. Assign room to patient
        cursor.execute("UPDATE patients SET room_id = ?, updated_at = ? WHERE patient_id = ?", (room_id, now_ts, patient_id))

        # 3. Mark room as Occupied
        cursor.execute("UPDATE rooms SET status = 'Occupied' WHERE room_id = ?", (room_id,))

        # 4. Audit logging
        log_audit(
            conn,
            "admissions",
            admission_id,
            "INSERT",
            f"Admitted patient '{p['full_name']}' to Room #{r['room_number']}. Diagnosis: {diagnosis or 'General Admission'}",
            performed_by
        )
        conn.commit()
        return admission_id
    finally:
        conn.close()


def discharge_admission(admission_id: int, discharge_date=None, discharge_notes="", room_status_after="Available", performed_by="front_desk_user"):
    """
    Completes an inpatient admission stay, releases the room/bed, and logs clinical notes.
    """
    from utils.validators import is_valid_date
    discharge_date = str(discharge_date or _now()[:10]).strip()
    if not is_valid_date(discharge_date):
        raise ValidationError("Discharge date must be in YYYY-MM-DD format", field="discharge_date")

    conn = get_connection()
    try:
        adm = conn.execute(
            "SELECT a.*, p.full_name, r.room_number FROM admissions a "
            "JOIN patients p ON a.patient_id = p.patient_id "
            "JOIN rooms r ON a.room_id = r.room_id "
            "WHERE a.admission_id = ?",
            (admission_id,)
        ).fetchone()

        if not adm:
            raise ValidationError(f"Admission stay #{admission_id} not found", field="admission_id")
        if adm["status"] == "Discharged":
            raise ValidationError(f"Admission stay #{admission_id} is already discharged", field="admission_id")

        if discharge_date < adm["admission_date"]:
            raise ValidationError(
                f"Discharge date ({discharge_date}) cannot be earlier than admission date ({adm['admission_date']})",
                field="discharge_date"
            )

        now_ts = _now()
        cursor = conn.cursor()

        # 1. Mark admission discharged
        cursor.execute(
            "UPDATE admissions SET status = 'Discharged', discharge_date = ?, discharge_notes = ? WHERE admission_id = ?",
            (discharge_date, (discharge_notes or "").strip(), admission_id)
        )

        # 2. Release room
        target_status = room_status_after if room_status_after in ["Available", "Cleaning / Sanitizing"] else "Available"
        cursor.execute("UPDATE rooms SET status = ? WHERE room_id = ?", (target_status, adm["room_id"]))

        # 3. Clear patient room assignment
        cursor.execute("UPDATE patients SET room_id = NULL, updated_at = ? WHERE patient_id = ?", (now_ts, adm["patient_id"]))

        # 4. Audit logging
        log_audit(
            conn,
            "admissions",
            admission_id,
            "UPDATE",
            f"Discharged patient '{adm['full_name']}' from Room #{adm['room_number']}. Bed status: '{target_status}'. Notes: {discharge_notes}",
            performed_by
        )
        conn.commit()
        return {
            "admission_id": admission_id,
            "patient_name": adm["full_name"],
            "room_number": adm["room_number"],
            "discharge_date": discharge_date,
            "room_status": target_status
        }
    finally:
        conn.close()


def list_admissions(active_only=False):
    conn = get_connection()
    try:
        query = (
            "SELECT a.*, p.full_name as patient_name, p.phone as patient_phone, "
            "r.room_number, r.room_type, r.rate_per_day "
            "FROM admissions a "
            "JOIN patients p ON a.patient_id = p.patient_id "
            "JOIN rooms r ON a.room_id = r.room_id "
        )
        if active_only:
            query += "WHERE a.status = 'Admitted' "
        query += "ORDER BY a.admission_id DESC"
        rows = conn.execute(query).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_patient_admissions(patient_id: int):
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT a.*, r.room_number, r.room_type, r.rate_per_day "
            "FROM admissions a "
            "JOIN rooms r ON a.room_id = r.room_id "
            "WHERE a.patient_id = ? ORDER BY a.admission_id DESC",
            (patient_id,)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_active_admission(patient_id: int):
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT a.*, r.room_number, r.room_type, r.rate_per_day "
            "FROM admissions a "
            "JOIN rooms r ON a.room_id = r.room_id "
            "WHERE a.patient_id = ? AND a.status = 'Admitted'",
            (patient_id,)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()
