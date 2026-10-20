"""
admissions.py -- REST API Blueprint for Inpatient Admission and Stay Tracking.
"""
from flask import Blueprint, request, jsonify, session
from models import admission as admission_model
from utils.exception_handler import ValidationError

admissions_bp = Blueprint("admissions", __name__)


@admissions_bp.route("/admissions", methods=["GET"])
def list_admissions():
    active_only = request.args.get("active_only") in ["1", "true", "True"]
    admissions = admission_model.list_admissions(active_only=active_only)
    return jsonify(admissions), 200


@admissions_bp.route("/admissions", methods=["POST"])
def admit_patient():
    data = request.get_json() or {}
    user = session.get("username", "front_desk_user")
    try:
        adm_id = admission_model.admit_patient(
            patient_id=int(data.get("patient_id")),
            room_id=int(data.get("room_id")),
            admission_date=data.get("admission_date"),
            diagnosis=data.get("diagnosis", ""),
            performed_by=user
        )
        return jsonify({"message": "Patient admitted successfully", "admission_id": adm_id}), 201
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid patient or room identifier"}), 400
    except ValidationError as e:
        return jsonify({"error": e.message, "field": e.field}), 400


@admissions_bp.route("/admissions/<int:admission_id>/discharge", methods=["POST"])
def discharge_patient(admission_id):
    data = request.get_json() or {}
    user = session.get("username", "front_desk_user")
    try:
        res = admission_model.discharge_admission(
            admission_id=admission_id,
            discharge_date=data.get("discharge_date"),
            discharge_notes=data.get("discharge_notes", ""),
            room_status_after=data.get("room_status_after", "Available"),
            performed_by=user
        )
        return jsonify({"message": "Patient discharged successfully", "details": res}), 200
    except ValidationError as e:
        return jsonify({"error": e.message, "field": e.field}), 400


@admissions_bp.route("/admissions/patient/<int:patient_id>", methods=["GET"])
def get_patient_admissions(patient_id):
    stays = admission_model.get_patient_admissions(patient_id)
    active = admission_model.get_active_admission(patient_id)
    return jsonify({"stays": stays, "active_stay": active}), 200
