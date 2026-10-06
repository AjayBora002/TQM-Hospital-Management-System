"""
patients.py -- Patient management REST API endpoints
"""
from flask import Blueprint, request, jsonify
from database.db_manager import get_connection
import models.patient as patient_model
from .helpers import rows_to_list

patients_bp = Blueprint("patients", __name__)

@patients_bp.route("/patients", methods=["GET"])
def get_patients():
    q = request.args.get("q", "").strip()
    return jsonify(rows_to_list(patient_model.list_all(q)))

@patients_bp.route("/patients/autocomplete", methods=["GET"])
def autocomplete_patients():
    prefix = request.args.get("prefix", "").strip()
    conn = get_connection()
    rows = conn.execute("SELECT patient_id, full_name, phone FROM patients WHERE full_name LIKE ? LIMIT 8", (f"{prefix}%",)).fetchall()
    conn.close()
    return jsonify([{"id": r["patient_id"], "label": f"{r['full_name']} ({r['phone']})"} for r in rows])

@patients_bp.route("/patients", methods=["POST"])
def create_patient():
    data = request.json or {}
    name = data.get("full_name", "").strip()
    if not name:
        return jsonify({"error": "Full name is required"}), 400
    
    room_id = data.get("room_id")
    if room_id:
        room_id = int(room_id)

    new_id = patient_model.add(
        full_name=name,
        gender=data.get("gender", "Other"),
        dob=data.get("dob", ""),
        blood_group=data.get("blood_group", "O+"),
        phone=data.get("phone", ""),
        address=data.get("address", ""),
        room_id=room_id
    )
    return jsonify({"patient_id": new_id, "status": "created"}), 201

@patients_bp.route("/patients/<int:patient_id>", methods=["PUT"])
def update_patient(patient_id):
    data = request.json or {}
    room_id = data.get("room_id")
    room_id = int(room_id) if room_id else None
    
    patient_model.update(
        patient_id=patient_id,
        full_name=data.get("full_name"),
        gender=data.get("gender"),
        dob=data.get("dob"),
        blood_group=data.get("blood_group"),
        phone=data.get("phone"),
        address=data.get("address"),
        room_id=room_id
    )
    return jsonify({"status": "updated"})

@patients_bp.route("/patients/<int:patient_id>", methods=["DELETE"])
def delete_patient(patient_id):
    patient_model.delete(patient_id)
    return jsonify({"status": "deleted"})

@patients_bp.route("/patients/<int:patient_id>/discharge-summary", methods=["GET"])
def get_discharge_summary(patient_id):
    summary = patient_model.get_discharge_summary(patient_id)
    if not summary:
        return jsonify({"error": "Patient not found"}), 404
    return jsonify(summary)

@patients_bp.route("/patients/<int:patient_id>/discharge", methods=["POST"])
def discharge_patient(patient_id):
    data = request.json or {}
    notes = data.get("discharge_notes", "").strip()
    room_status_after = data.get("room_status", "Available")
    result = patient_model.discharge(patient_id, discharge_notes=notes, room_status_after=room_status_after)
    if not result:
        return jsonify({"error": "Patient not found"}), 404
    return jsonify({"status": "discharged", "details": result})

