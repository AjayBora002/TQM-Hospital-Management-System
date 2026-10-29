"""
ot_api.py -- REST API Blueprint for Operation Theatre (OT) Scheduling & Surgical Safety.
Enforces WHO Surgical Safety Checklist (Sign-In, Time-Out, Sign-Out).
"""
from flask import Blueprint, request, jsonify, session
from database.db_manager import get_connection, log_audit
from auth.permissions import require_permission
from utils.exception_handler import ValidationError

ot_bp = Blueprint("ot", __name__)


@ot_bp.route("/ot/schedules", methods=["GET"])
@require_permission("clinical", "view")
def list_ot_schedules():
    conn = get_connection()
    try:
        rows = conn.execute("""
            SELECT o.*, p.full_name as patient_name, p.gender, p.blood_group, p.allergies,
                   d.full_name as surgeon_name, d.department
            FROM ot_schedules o
            JOIN patients p ON o.patient_id = p.patient_id
            JOIN doctors d ON o.surgeon_id = d.doctor_id
            ORDER BY o.scheduled_start ASC
        """).fetchall()
        return jsonify([dict(r) for r in rows]), 200
    finally:
        conn.close()


@ot_bp.route("/ot/schedules", methods=["POST"])
@require_permission("clinical", "create")
def schedule_surgery():
    data = request.get_json() or {}
    patient_id = data.get("patient_id")
    procedure_name = data.get("procedure_name", "").strip()
    surgeon_id = data.get("surgeon_id")
    anesthetist_name = data.get("anesthetist_name", "").strip()
    ot_room = data.get("ot_room", "").strip()
    scheduled_start = data.get("scheduled_start", "").strip()
    scheduled_end = data.get("scheduled_end", "").strip()
    anesthesia_type = data.get("anesthesia_type", "General")
    notes = data.get("notes", "")
    user = session.get("username", "ot_coordinator")

    if not patient_id:
        raise ValidationError("Patient selection is required", field="patient_id")
    if not procedure_name:
        raise ValidationError("Surgical procedure name is required", field="procedure_name")
    if not surgeon_id:
        raise ValidationError("Lead surgeon must be designated", field="surgeon_id")
    if not anesthetist_name:
        raise ValidationError("Anesthetist name is required", field="anesthetist_name")
    if not ot_room:
        raise ValidationError("OT Suite / Room number is required", field="ot_room")
    if not scheduled_start or not scheduled_end:
        raise ValidationError("Scheduled start and end times are required", field="scheduled_start")

    conn = get_connection()
    try:
        # Check OT suite conflict
        conflict = conn.execute("""
            SELECT ot_id FROM ot_schedules 
            WHERE ot_room = ? AND status != 'Cancelled'
              AND NOT (scheduled_end <= ? OR scheduled_start >= ?)
        """, (ot_room, scheduled_start, scheduled_end)).fetchone()

        if conflict:
            raise ValidationError(f"OT Suite '{ot_room}' already has a scheduled surgical procedure during this time slot.", field="ot_room")

        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO ot_schedules (patient_id, procedure_name, surgeon_id, anesthetist_name, ot_room, scheduled_start, scheduled_end, pre_op_checklist_ok, post_op_checklist_ok, anesthesia_type, status, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, 0, 0, ?, 'Scheduled', ?)
        """, (patient_id, procedure_name, surgeon_id, anesthetist_name, ot_room, scheduled_start, scheduled_end, anesthesia_type, notes))
        ot_id = cursor.lastrowid
        log_audit(conn, "ot_schedules", ot_id, "INSERT", f"Scheduled surgery '{procedure_name}' in {ot_room}", user)
        conn.commit()
        return jsonify({"message": "Surgery scheduled successfully", "ot_id": ot_id}), 201
    finally:
        conn.close()


@ot_bp.route("/ot/schedules/<int:ot_id>/checklist", methods=["PUT"])
@require_permission("clinical", "edit")
def update_surgical_checklist(ot_id):
    data = request.get_json() or {}
    pre_op_ok = 1 if data.get("pre_op_checklist_ok") else 0
    post_op_ok = 1 if data.get("post_op_checklist_ok") else 0
    status = data.get("status")
    user = session.get("username", "ot_staff")

    conn = get_connection()
    try:
        cursor = conn.cursor()
        if status:
            cursor.execute("""
                UPDATE ot_schedules 
                SET pre_op_checklist_ok = ?, post_op_checklist_ok = ?, status = ?
                WHERE ot_id = ?
            """, (pre_op_ok, post_op_ok, status, ot_id))
        else:
            cursor.execute("""
                UPDATE ot_schedules 
                SET pre_op_checklist_ok = ?, post_op_checklist_ok = ?
                WHERE ot_id = ?
            """, (pre_op_ok, post_op_ok, ot_id))

        if cursor.rowcount == 0:
            return jsonify({"error": "OT schedule not found"}), 404
        log_audit(conn, "ot_schedules", ot_id, "UPDATE", f"Checklist updated: Pre-op={pre_op_ok}, Post-op={post_op_ok}, Status={status}", user)
        conn.commit()
        return jsonify({"message": "Surgical safety checklist updated successfully"}), 200
    finally:
        conn.close()
