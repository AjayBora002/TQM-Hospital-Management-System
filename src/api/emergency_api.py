"""
emergency_api.py -- REST API Blueprint for Emergency & Casualty / Trauma Board.
NABH COP.2 compliant severity prioritization and bed disposition.
"""
from flask import Blueprint, request, jsonify, session
from database.db_manager import get_connection, log_audit
from auth.permissions import require_permission
from utils.exception_handler import ValidationError
from datetime import datetime

emergency_bp = Blueprint("emergency", __name__)


@emergency_bp.route("/emergency", methods=["GET"])
@require_permission("clinical", "view")
def list_emergency_cases():
    conn = get_connection()
    try:
        rows = conn.execute("""
            SELECT e.*, d.full_name as attending_doctor_name, p.dob, p.gender, p.blood_group
            FROM emergency_cases e
            LEFT JOIN doctors d ON e.attending_doctor_id = d.doctor_id
            LEFT JOIN patients p ON e.patient_id = p.patient_id
            ORDER BY 
                CASE e.triage_color 
                    WHEN 'Red' THEN 1 
                    WHEN 'Yellow' THEN 2 
                    WHEN 'Green' THEN 3 
                    ELSE 4 
                END,
                e.arrival_time DESC
        """).fetchall()
        return jsonify([dict(r) for r in rows]), 200
    finally:
        conn.close()


@emergency_bp.route("/emergency", methods=["POST"])
@require_permission("clinical", "create")
def intake_emergency_case():
    data = request.get_json() or {}
    patient_name = data.get("patient_name", "").strip()
    triage_color = data.get("triage_color", "Yellow")
    chief_complaint = data.get("chief_complaint", "").strip()
    vitals_summary = data.get("vitals_summary", "").strip()
    trauma_details = data.get("trauma_details", "").strip()
    attending_doctor_id = data.get("attending_doctor_id")
    arrival_mode = data.get("arrival_mode", "Walk-in")
    patient_id = data.get("patient_id")
    user = session.get("username", "er_staff")

    if not patient_name:
        raise ValidationError("Patient name or identifier is required for Emergency intake", field="patient_name")
    if triage_color not in ("Red", "Yellow", "Green", "Black"):
        raise ValidationError("Triage color must be Red, Yellow, Green, or Black", field="triage_color")
    if not chief_complaint:
        raise ValidationError("Chief complaint is mandatory in Emergency triage", field="chief_complaint")

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO emergency_cases (patient_id, patient_name, triage_color, chief_complaint, vitals_summary, trauma_details, attending_doctor_id, arrival_mode, arrival_time, disposition, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Trauma Bay Assessment', 'Active')
        """, (patient_id, patient_name, triage_color, chief_complaint, vitals_summary, trauma_details, attending_doctor_id, arrival_mode, now_str))
        case_id = cursor.lastrowid
        log_audit(conn, "emergency_cases", case_id, "INSERT", f"Emergency triage intake for '{patient_name}' [Color: {triage_color}]", user)
        conn.commit()
        return jsonify({"message": "Emergency case registered", "emergency_id": case_id}), 201
    finally:
        conn.close()


@emergency_bp.route("/emergency/<int:emergency_id>/disposition", methods=["PUT"])
@require_permission("clinical", "edit")
def update_emergency_disposition(emergency_id):
    data = request.get_json() or {}
    disposition = data.get("disposition", "").strip()
    status = data.get("status", "Active")
    user = session.get("username", "er_staff")

    valid_statuses = ("Active", "Transferred to ICU", "Admitted", "Discharged", "Deceased")
    if status not in valid_statuses:
        raise ValidationError(f"Status must be one of {valid_statuses}", field="status")

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE emergency_cases SET disposition = ?, status = ? WHERE emergency_id = ?
        """, (disposition, status, emergency_id))
        if cursor.rowcount == 0:
            return jsonify({"error": "Emergency case not found"}), 404
        log_audit(conn, "emergency_cases", emergency_id, "UPDATE", f"Updated disposition: {disposition} ({status})", user)
        conn.commit()
        return jsonify({"message": "Emergency disposition updated"}), 200
    finally:
        conn.close()

