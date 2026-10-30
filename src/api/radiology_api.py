"""
radiology_api.py -- REST API Blueprint for Diagnostic Radiology & Imaging Workflow.
Covers order -> scan -> radiologist report -> verified findings.
"""
from flask import Blueprint, request, jsonify, session
from database.db_manager import get_connection, log_audit
from auth.permissions import require_permission
from utils.exception_handler import ValidationError
from datetime import datetime

radiology_bp = Blueprint("radiology", __name__)


@radiology_bp.route("/radiology/orders", methods=["GET"])
@require_permission("diagnostics", "view")
def list_radiology_orders():
    patient_id = request.args.get("patient_id")
    status = request.args.get("status")

    query = """
        SELECT r.*, p.full_name as patient_name, p.gender, p.dob,
               d.full_name as ordering_doctor_name, rad.full_name as radiologist_name
        FROM radiology_orders r
        JOIN patients p ON r.patient_id = p.patient_id
        JOIN doctors d ON r.doctor_id = d.doctor_id
        LEFT JOIN doctors rad ON r.radiologist_id = rad.doctor_id
        WHERE 1=1
    """
    params = []
    if patient_id:
        query += " AND r.patient_id = ?"
        params.append(patient_id)
    if status:
        query += " AND r.status = ?"
        params.append(status)
    query += " ORDER BY r.order_id DESC"

    conn = get_connection()
    try:
        rows = conn.execute(query, params).fetchall()
        return jsonify([dict(r) for r in rows]), 200
    finally:
        conn.close()


@radiology_bp.route("/radiology/orders", methods=["POST"])
@require_permission("clinical", "create")
def order_radiology_scan():
    data = request.get_json() or {}
    patient_id = data.get("patient_id")
    doctor_id = data.get("doctor_id")
    modality = data.get("modality", "").strip()
    body_part = data.get("body_part", "").strip()
    clinical_indication = data.get("clinical_indication", "").strip()
    urgency = data.get("urgency", "Routine")
    user = session.get("username", "doc_user")

    valid_modalities = ("X-Ray", "CT Scan", "MRI", "Ultrasound", "Mammography", "DEXA")
    if modality not in valid_modalities:
        raise ValidationError(f"Modality must be one of {valid_modalities}", field="modality")
    if not patient_id:
        raise ValidationError("Patient is required", field="patient_id")
    if not doctor_id:
        raise ValidationError("Ordering doctor is required", field="doctor_id")
    if not body_part:
        raise ValidationError("Anatomical body part / view is required", field="body_part")

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO radiology_orders (patient_id, doctor_id, modality, body_part, clinical_indication, urgency, status, ordered_at)
            VALUES (?, ?, ?, ?, ?, ?, 'Ordered', ?)
        """, (patient_id, doctor_id, modality, body_part, clinical_indication, urgency, now_str))
        order_id = cursor.lastrowid
        log_audit(conn, "radiology_orders", order_id, "INSERT", f"Radiology order {modality} - {body_part}", user)
        conn.commit()
        return jsonify({"message": "Radiology order placed successfully", "order_id": order_id}), 201
    finally:
        conn.close()


@radiology_bp.route("/radiology/orders/<int:order_id>/report", methods=["PUT"])
@require_permission("diagnostics", "edit")
def report_radiology_findings(order_id):
    data = request.get_json() or {}
    findings = data.get("findings", "").strip()
    impression = data.get("impression", "").strip()
    dicom_link = data.get("dicom_link", "").strip()
    status = data.get("status", "Reported")
    radiologist_id = data.get("radiologist_id")
    user = session.get("username", "radiologist")

    if not findings:
        raise ValidationError("Diagnostic findings report cannot be empty", field="findings")
    if not impression:
        raise ValidationError("Clinical impression summary is required", field="impression")

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE radiology_orders
            SET findings = ?, impression = ?, dicom_link = ?, status = ?, radiologist_id = ?, reported_at = ?
            WHERE order_id = ?
        """, (findings, impression, dicom_link, status, radiologist_id, now_str, order_id))
        if cursor.rowcount == 0:
            return jsonify({"error": "Radiology order not found"}), 404
        log_audit(conn, "radiology_orders", order_id, "UPDATE", f"Radiology report filed: {status}", user)
        conn.commit()
        return jsonify({"message": "Radiology report submitted successfully"}), 200
    finally:
        conn.close()

