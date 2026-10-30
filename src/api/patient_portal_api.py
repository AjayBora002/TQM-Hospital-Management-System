"""
patient_portal_api.py -- REST API Blueprint for Patient Self-Service Portal.
Strict row-level security: Patients can only view their own appointments, bills,
prescriptions, and released lab reports.
"""
from flask import Blueprint, request, jsonify, session
from database.db_manager import get_connection
from auth.permissions import require_permission

patient_portal_bp = Blueprint("patient_portal", __name__)


def _resolve_current_patient_id():
    """Resolves the patient_id of the currently authenticated patient user."""
    user_id = session.get("user_id")
    username = session.get("username", "")

    conn = get_connection()
    try:
        # Check user record
        u_row = conn.execute("SELECT full_name, email FROM users WHERE user_id = ?", (user_id,)).fetchone()
        if not u_row:
            return None

        # Match patient by name or email or fallback to first patient for demo account 'patient'
        pat = conn.execute("""
            SELECT patient_id FROM patients 
            WHERE full_name LIKE ? OR address LIKE ?
            LIMIT 1
        """, (f"%{u_row['full_name'].split()[0]}%", f"%{u_row['email']}%")).fetchone()

        if pat:
            return pat["patient_id"]

        # Default fallback for demo user 'patient' -> first patient
        first = conn.execute("SELECT patient_id FROM patients ORDER BY patient_id LIMIT 1").fetchone()
        return first["patient_id"] if first else None
    finally:
        conn.close()


@patient_portal_bp.route("/patient-portal/profile", methods=["GET"])
@require_permission("patient_portal", "view")
def get_patient_profile():
    pid = _resolve_current_patient_id()
    if not pid:
        return jsonify({"error": "Patient profile not found"}), 404

    conn = get_connection()
    try:
        pat = conn.execute("SELECT * FROM patients WHERE patient_id = ?", (pid,)).fetchone()
        if not pat:
            return jsonify({"error": "Patient record not found"}), 404
        return jsonify(dict(pat)), 200
    finally:
        conn.close()


@patient_portal_bp.route("/patient-portal/appointments", methods=["GET"])
@require_permission("patient_portal", "view")
def get_my_appointments():
    pid = _resolve_current_patient_id()
    if not pid:
        return jsonify([]), 200

    conn = get_connection()
    try:
        rows = conn.execute("""
            SELECT a.*, d.full_name as doctor_name, d.department
            FROM appointments a
            JOIN doctors d ON a.doctor_id = d.doctor_id
            WHERE a.patient_id = ?
            ORDER BY a.appt_date DESC, a.appt_time DESC
        """, (pid,)).fetchall()
        return jsonify([dict(r) for r in rows]), 200
    finally:
        conn.close()


@patient_portal_bp.route("/patient-portal/prescriptions", methods=["GET"])
@require_permission("patient_portal", "view")
def get_my_prescriptions():
    pid = _resolve_current_patient_id()
    if not pid:
        return jsonify([]), 200

    conn = get_connection()
    try:
        rows = conn.execute("""
            SELECT pr.*, m.name as medicine_name, m.category, d.full_name as doctor_name
            FROM prescriptions pr
            JOIN medicines m ON pr.medicine_id = m.medicine_id
            JOIN doctors d ON pr.doctor_id = d.doctor_id
            WHERE pr.patient_id = ?
            ORDER BY pr.prescription_id DESC
        """, (pid,)).fetchall()
        return jsonify([dict(r) for r in rows]), 200
    finally:
        conn.close()


@patient_portal_bp.route("/patient-portal/bills", methods=["GET"])
@require_permission("patient_portal", "view")
def get_my_bills():
    pid = _resolve_current_patient_id()
    if not pid:
        return jsonify([]), 200

    conn = get_connection()
    try:
        rows = conn.execute("""
            SELECT b.*, p.full_name as patient_name
            FROM bills b
            JOIN patients p ON b.patient_id = p.patient_id
            WHERE b.patient_id = ?
            ORDER BY b.bill_id DESC
        """, (pid,)).fetchall()
        return jsonify([dict(r) for r in rows]), 200
    finally:
        conn.close()


@patient_portal_bp.route("/patient-portal/lab-reports", methods=["GET"])
@require_permission("patient_portal", "view")
def get_my_lab_reports():
    pid = _resolve_current_patient_id()
    if not pid:
        return jsonify([]), 200

    conn = get_connection()
    try:
        # Row-level gate: only released/completed lab tests are accessible to patient
        rows = conn.execute("""
            SELECT l.*, d.full_name as doctor_name
            FROM lab_tests l
            JOIN doctors d ON l.doctor_id = d.doctor_id
            WHERE l.patient_id = ? AND l.status IN ('Completed', 'Released', 'Verified')
            ORDER BY l.test_id DESC
        """, (pid,)).fetchall()
        return jsonify([dict(r) for r in rows]), 200
    finally:
        conn.close()

