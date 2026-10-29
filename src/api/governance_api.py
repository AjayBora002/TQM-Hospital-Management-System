"""
governance_api.py -- REST API Blueprint for Clinical Quality & Incident Reporting (NABH / ISO 9001).
Near-miss reporting, Sentinel event investigation, and CAPA (Corrective & Preventive Action) cycles.
"""
from flask import Blueprint, request, jsonify, session
from database.db_manager import get_connection, log_audit
from auth.permissions import require_permission
from utils.exception_handler import ValidationError
from datetime import datetime

governance_bp = Blueprint("governance", __name__)


@governance_bp.route("/governance/incidents", methods=["GET"])
@require_permission("quality", "view")
def list_quality_incidents():
    conn = get_connection()
    try:
        rows = conn.execute("""
            SELECT i.*, c.capa_id, c.root_cause, c.corrective_action, c.preventive_action, c.status as capa_status, c.due_date
            FROM quality_incidents i
            LEFT JOIN capa_actions c ON i.incident_id = c.incident_id
            ORDER BY i.incident_id DESC
        """).fetchall()
        return jsonify([dict(r) for r in rows]), 200
    finally:
        conn.close()


@governance_bp.route("/governance/incidents", methods=["POST"])
@require_permission("quality", "create")
def report_quality_incident():
    data = request.get_json() or {}
    incident_type = data.get("incident_type", "").strip()
    department = data.get("department", "").strip()
    severity = data.get("severity", "Near Miss")
    description = data.get("description", "").strip()
    user = session.get("username", "staff")

    valid_types = (
        "Medication Error", "Patient Fall", "Needlestick Injury",
        "Surgical Near Miss", "Hospital Acquired Infection",
        "Equipment Failure", "Documentation Defect", "Patient Identification Mismatch"
    )
    if incident_type not in valid_types:
        raise ValidationError(f"Incident type must be one of {valid_types}", field="incident_type")
    if not department:
        raise ValidationError("Department is required", field="department")
    if not description:
        raise ValidationError("Incident factual description is required", field="description")

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO quality_incidents (incident_type, department, severity, description, reported_by, reported_at, status)
            VALUES (?, ?, ?, ?, ?, ?, 'Reported')
        """, (incident_type, department, severity, description, user, now_str))
        incident_id = cursor.lastrowid
        log_audit(conn, "quality_incidents", incident_id, "INSERT", f"Reported {incident_type} [{severity}] in {department}", user)
        conn.commit()
        return jsonify({"message": "Incident logged for Quality Assurance", "incident_id": incident_id}), 201
    finally:
        conn.close()


@governance_bp.route("/governance/incidents/<int:incident_id>/capa", methods=["POST"])
@require_permission("quality", "approve")
def initiate_capa_action(incident_id):
    data = request.get_json() or {}
    root_cause = data.get("root_cause", "").strip()
    corrective_action = data.get("corrective_action", "").strip()
    preventive_action = data.get("preventive_action", "").strip()
    assigned_to = data.get("assigned_to", "").strip()
    due_date = data.get("due_date", "").strip()
    user = session.get("username", "quality_mgr")

    if not root_cause:
        raise ValidationError("Root cause analysis is required", field="root_cause")
    if not corrective_action or not preventive_action:
        raise ValidationError("Corrective and preventive actions are both required", field="corrective_action")
    if not assigned_to or not due_date:
        raise ValidationError("Assignee and due date are required", field="due_date")

    conn = get_connection()
    try:
        inc = conn.execute("SELECT incident_id FROM quality_incidents WHERE incident_id = ?", (incident_id,)).fetchone()
        if not inc:
            return jsonify({"error": "Incident not found"}), 404

        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO capa_actions (incident_id, root_cause, corrective_action, preventive_action, assigned_to, due_date, status)
            VALUES (?, ?, ?, ?, ?, ?, 'Open')
        """, (incident_id, root_cause, corrective_action, preventive_action, assigned_to, due_date))
        capa_id = cursor.lastrowid

        conn.execute("UPDATE quality_incidents SET status = 'CAPA Initiated' WHERE incident_id = ?", (incident_id,))
        log_audit(conn, "capa_actions", capa_id, "INSERT", f"Initiated CAPA for incident {incident_id}", user)
        conn.commit()
        return jsonify({"message": "CAPA cycle initiated successfully", "capa_id": capa_id}), 201
    finally:
        conn.close()
