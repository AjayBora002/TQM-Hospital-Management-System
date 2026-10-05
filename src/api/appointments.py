"""
appointments.py -- Appointment scheduling REST API endpoints
"""
from flask import Blueprint, request, jsonify
import models.appointment as appointment_model
from .helpers import rows_to_list

appointments_bp = Blueprint("appointments", __name__)

@appointments_bp.route("/appointments", methods=["GET"])
def get_appointments():
    return jsonify(rows_to_list(appointment_model.list_all()))

@appointments_bp.route("/appointments", methods=["POST"])
def create_appointment():
    data = request.json or {}
    new_id = appointment_model.add(
        patient_id=int(data.get("patient_id")),
        doctor_id=int(data.get("doctor_id")),
        appt_date=data.get("appt_date"),
        appt_time=data.get("appt_time"),
        status=data.get("status", "Scheduled")
    )
    return jsonify({"appointment_id": new_id, "status": "created"}), 201

@appointments_bp.route("/appointments/<int:appointment_id>", methods=["PUT"])
def update_appointment(appointment_id):
    data = request.json or {}
    appointment_model.update(
        appointment_id=appointment_id,
        patient_id=int(data.get("patient_id")),
        doctor_id=int(data.get("doctor_id")),
        appt_date=data.get("appt_date"),
        appt_time=data.get("appt_time"),
        status=data.get("status")
    )
    return jsonify({"status": "updated"})

@appointments_bp.route("/appointments/<int:appointment_id>", methods=["DELETE"])
def delete_appointment(appointment_id):
    appointment_model.delete(appointment_id)
    return jsonify({"status": "deleted"})
