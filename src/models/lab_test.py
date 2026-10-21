"""
lab_test.py -- Model for Diagnostic Pathology, Hematology, and Radiology Laboratory Tests.
Enforces Poka-Yoke automated flagging when clinical test results violate biological reference ranges.
"""
from datetime import datetime
from database.db_manager import get_connection, log_audit
from utils.exception_handler import ValidationError
import config


def _now():
    return datetime.now().isoformat(timespec="seconds")


def order_test(
    patient_id: int,
    doctor_id: int,
    test_name: str,
    category: str = None,
    unit: str = None,
    ref_min: float = None,
    ref_max: float = None,
    notes: str = "",
    performed_by: str = "doctor"
):
    """
    Orders a diagnostic laboratory test for a patient.
    If test_name matches a standard template in config.LAB_TEST_TEMPLATES,
    reference values and category are auto-populated.
    """
    if not patient_id:
        raise ValidationError("Patient selection is required", field="patient_id")
    if not doctor_id:
        raise ValidationError("Doctor selection is required", field="doctor_id")
    if not test_name or not test_name.strip():
        raise ValidationError("Test name is required", field="test_name")

    template = config.LAB_TEST_TEMPLATES.get(test_name.strip())
    if template:
        category = category or template["category"]
        unit = unit or template["unit"]
        ref_min = ref_min if ref_min is not None else template["ref_min"]
        ref_max = ref_max if ref_max is not None else template["ref_max"]
    else:
        category = category or "General"
        unit = unit or "units"
        ref_min = float(ref_min or 0.0)
        ref_max = float(ref_max or 100.0)

    conn = get_connection()
    try:
        # Check patient & doctor existence
        p = conn.execute("SELECT full_name FROM patients WHERE patient_id = ?", (patient_id,)).fetchone()
        if not p:
            raise ValidationError(f"Patient #{patient_id} does not exist", field="patient_id")
        d = conn.execute("SELECT full_name FROM doctors WHERE doctor_id = ?", (doctor_id,)).fetchone()
        if not d:
            raise ValidationError(f"Doctor #{doctor_id} does not exist", field="doctor_id")

        cur = conn.cursor()
        created_ts = _now()
        cur.execute(
            "INSERT INTO lab_tests "
            "(patient_id, doctor_id, test_name, category, unit, ref_min, ref_max, status, abnormal_flag, notes, created_at) "
            "VALUES (?,?,?,?,?,?,?,?,0,?,?)",
            (patient_id, doctor_id, test_name.strip(), category, unit, float(ref_min), float(ref_max), "Pending", notes or "", created_ts)
        )
        test_id = cur.lastrowid
        log_audit(conn, "lab_tests", test_id, "INSERT", f"Ordered '{test_name}' for patient '{p['full_name']}'", performed_by)
        conn.commit()
        return test_id
    finally:
        conn.close()


def record_result(test_id: int, result_value: float, notes: str = "", performed_by: str = "lab_tech"):
    """
    Records the quantitative result for an ordered lab test.
    Poka-Yoke: Automatically cross-references result_value against ref_min and ref_max.
    If outside the reference interval, abnormal_flag is automatically set to 1.
    """
    if not test_id:
        raise ValidationError("Test ID is required", field="test_id")
    try:
        val = float(result_value)
    except (TypeError, ValueError):
        raise ValidationError("Numeric result value is required", field="result_value")

    conn = get_connection()
    try:
        t = conn.execute("SELECT * FROM lab_tests WHERE test_id = ?", (test_id,)).fetchone()
        if not t:
            raise ValidationError(f"Lab test #{test_id} not found", field="test_id")
        if t["status"] == "Completed":
            raise ValidationError(f"Lab test #{test_id} is already marked Completed", field="test_id")

        is_abnormal = 1 if (val < t["ref_min"] or val > t["ref_max"]) else 0
        completed_ts = _now()

        conn.execute(
            "UPDATE lab_tests SET result_value=?, status='Completed', abnormal_flag=?, notes=?, completed_at=? "
            "WHERE test_id=?",
            (val, is_abnormal, (notes or t["notes"] or "").strip(), completed_ts, test_id)
        )
        flag_desc = "ABNORMAL" if is_abnormal else "NORMAL"
        log_audit(
            conn, "lab_tests", test_id, "UPDATE",
            f"Recorded result {val} {t['unit']} ({flag_desc}) for {t['test_name']}",
            performed_by
        )
        conn.commit()
        return get_by_id(test_id)
    finally:
        conn.close()


def get_by_id(test_id: int):
    conn = get_connection()
    try:
        row = conn.execute("""
            SELECT l.*, p.full_name as patient_name, d.full_name as doctor_name
            FROM lab_tests l
            JOIN patients p ON l.patient_id = p.patient_id
            JOIN doctors d ON l.doctor_id = d.doctor_id
            WHERE l.test_id = ?
        """, (test_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def list_all():
    conn = get_connection()
    try:
        rows = conn.execute("""
            SELECT l.*, p.full_name as patient_name, d.full_name as doctor_name
            FROM lab_tests l
            JOIN patients p ON l.patient_id = p.patient_id
            JOIN doctors d ON l.doctor_id = d.doctor_id
            ORDER BY l.test_id DESC
        """).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def list_by_patient(patient_id: int):
    conn = get_connection()
    try:
        rows = conn.execute("""
            SELECT l.*, p.full_name as patient_name, d.full_name as doctor_name
            FROM lab_tests l
            JOIN patients p ON l.patient_id = p.patient_id
            JOIN doctors d ON l.doctor_id = d.doctor_id
            WHERE l.patient_id = ?
            ORDER BY l.test_id DESC
        """, (patient_id,)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def list_abnormal():
    conn = get_connection()
    try:
        rows = conn.execute("""
            SELECT l.*, p.full_name as patient_name, d.full_name as doctor_name
            FROM lab_tests l
            JOIN patients p ON l.patient_id = p.patient_id
            JOIN doctors d ON l.doctor_id = d.doctor_id
            WHERE l.abnormal_flag = 1
            ORDER BY l.test_id DESC
        """).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()
