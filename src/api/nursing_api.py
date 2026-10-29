"""
nursing_api.py -- REST API Blueprint for Nursing Station, Inpatient Ward Care, and MAR with RBAC.
"""
from flask import Blueprint, request, jsonify, session
from models import nursing as nursing_model
from database.db_manager import get_connection, log_audit
from auth.permissions import require_permission
from datetime import datetime

nursing_bp = Blueprint("nursing_api", __name__)


@nursing_bp.route("/nursing/roster", methods=["GET"])
@require_permission("inpatient", "view")
def get_nursing_roster():
    ward_id = request.args.get("ward_id")
    dept = request.args.get("department")
    roster = nursing_model.list_nurses(
        department=dept,
        ward_id=int(ward_id) if ward_id else None
    )
    return jsonify(roster), 200


@nursing_bp.route("/nursing/inpatients", methods=["GET"])
@require_permission("inpatient", "view")
def get_ward_patients():
    ward_id = request.args.get("ward_id")
    patients = nursing_model.get_ward_inpatients(
        ward_id=int(ward_id) if ward_id else None
    )
    return jsonify(patients), 200


@nursing_bp.route("/nursing/mar", methods=["GET"])
@require_permission("inpatient", "view")
def get_patient_mar():
    patient_id = request.args.get("patient_id")
    conn = get_connection()
    try:
        query = "SELECT * FROM nursing_mar WHERE 1=1"
        params = []
        if patient_id:
            query += " AND patient_id = ?"
            params.append(patient_id)
        query += " ORDER BY mar_id DESC"
        rows = conn.execute(query, params).fetchall()
        return jsonify([dict(r) for r in rows]), 200
    finally:
        conn.close()


@nursing_bp.route("/nursing/mar", methods=["POST"])
@require_permission("inpatient", "create")
def schedule_mar_entry():
    data = request.get_json() or {}
    patient_id = data.get("patient_id")
    medicine_name = data.get("medicine_name")
    dosage = data.get("dosage")
    route = data.get("route", "Oral")
    scheduled_time = data.get("scheduled_time", datetime.now().strftime("%Y-%m-%d %H:%M"))
    notes = data.get("notes", "")

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO nursing_mar (patient_id, medicine_name, dosage, route, scheduled_time, status, notes)
            VALUES (?, ?, ?, ?, ?, 'Scheduled', ?)
        """, (patient_id, medicine_name, dosage, route, scheduled_time, notes))
        mar_id = cursor.lastrowid
        conn.commit()
        return jsonify({"message": "MAR dose scheduled", "mar_id": mar_id}), 201
    finally:
        conn.close()


@nursing_bp.route("/nursing/mar/<int:mar_id>/administer", methods=["PUT"])
@require_permission("inpatient", "edit")
def administer_medication(mar_id):
    data = request.get_json() or {}
    vital_check = data.get("vital_check", "Pulse: 76, BP: 120/80")
    notes = data.get("notes", "Administered as prescribed")
    nurse_name = session.get("full_name", "Sister Sunita Patel")
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE nursing_mar 
            SET status = 'Given', administered_time = ?, administered_by = ?, vital_check = ?, notes = ?
            WHERE mar_id = ?
        """, (now_str, nurse_name, vital_check, notes, mar_id))
        if cursor.rowcount == 0:
            return jsonify({"error": "MAR entry not found"}), 404
        log_audit(conn, "nursing_mar", mar_id, "UPDATE", f"Administered scheduled medication by {nurse_name}", nurse_name)
        conn.commit()
        return jsonify({"message": "Medication administration recorded in MAR"}), 200
    finally:
        conn.close()
