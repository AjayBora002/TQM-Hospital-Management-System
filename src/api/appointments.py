"""
appointments.py -- Appointment scheduling REST API endpoints with Clinical Poka-Yoke conflict prevention
"""
from flask import Blueprint, request, jsonify
import models.appointment as appointment_model
from utils.validators import validate_appointment_payload
from .helpers import rows_to_list

appointments_bp = Blueprint("appointments", __name__)


@appointments_bp.route("/appointments", methods=["GET"])
def get_appointments():
    return jsonify(rows_to_list(appointment_model.list_all()))


@appointments_bp.route("/appointments", methods=["POST"])
def create_appointment():
    data = request.json or {}
    validate_appointment_payload(data)

    patient_id = int(data.get("patient_id"))
    doctor_id = int(data.get("doctor_id"))
    appt_date = data.get("appt_date")
    appt_time = data.get("appt_time")
    status = data.get("status", "Scheduled")

    # Poka-Yoke Check 1: Doctor double-booking prevention
    doc_conflict = appointment_model.has_conflict(doctor_id, appt_date, appt_time)
    if doc_conflict:
        return jsonify({
            "error": "Doctor Double-Booking Conflict",
            "message": f"Clinical Poka-Yoke Alert: {doc_conflict['doctor']} is already booked at {appt_time} on {appt_date} (Patient: {doc_conflict['patient']}).",
            "conflict_type": "DOCTOR_OVERLAP"
        }), 409

    # Poka-Yoke Check 2: Patient overlapping appointment prevention
    pat_conflict = appointment_model.has_patient_conflict(patient_id, appt_date, appt_time)
    if pat_conflict:
        return jsonify({
            "error": "Patient Overlap Conflict",
            "message": f"Clinical Poka-Yoke Alert: Patient already has a scheduled appointment with {pat_conflict['doctor']} at {appt_time} on {appt_date}.",
            "conflict_type": "PATIENT_OVERLAP"
        }), 409

    new_id = appointment_model.add(
        patient_id=patient_id,
        doctor_id=doctor_id,
        appt_date=appt_date,
        appt_time=appt_time,
        status=status
    )
    return jsonify({"appointment_id": new_id, "status": "created"}), 201


@appointments_bp.route("/appointments/<int:appointment_id>", methods=["PUT"])
def update_appointment(appointment_id):
    data = request.json or {}
    validate_appointment_payload(data)

    patient_id = int(data.get("patient_id"))
    doctor_id = int(data.get("doctor_id"))
    appt_date = data.get("appt_date")
    appt_time = data.get("appt_time")
    status = data.get("status")

    # Poka-Yoke Check: Doctor double-booking prevention excluding current appointment
    if status != "Cancelled":
        doc_conflict = appointment_model.has_conflict(doctor_id, appt_date, appt_time, exclude_id=appointment_id)
        if doc_conflict:
            return jsonify({
                "error": "Doctor Double-Booking Conflict",
                "message": f"Clinical Poka-Yoke Alert: {doc_conflict['doctor']} is already booked at {appt_time} on {appt_date} (Patient: {doc_conflict['patient']}).",
                "conflict_type": "DOCTOR_OVERLAP"
            }), 409

    appointment_model.update(
        appointment_id=appointment_id,
        patient_id=patient_id,
        doctor_id=doctor_id,
        appt_date=appt_date,
        appt_time=appt_time,
        status=status
    )
    return jsonify({"status": "updated"})


@appointments_bp.route("/appointments/<int:appointment_id>", methods=["DELETE"])
def delete_appointment(appointment_id):
    appointment_model.delete(appointment_id)
    return jsonify({"status": "deleted"})


@appointments_bp.route("/doctors/<int:doctor_id>/slots", methods=["GET"])
def get_doctor_slots(doctor_id):
    """Retrieve slot availability for a doctor on a given date to guide conflict-free booking."""
    date_str = request.args.get("date")
    if not date_str:
        return jsonify({"error": "Missing 'date' query parameter (YYYY-MM-DD)."}), 400

    slots = appointment_model.get_doctor_available_slots(doctor_id, date_str)
    booked = appointment_model.get_doctor_booked_slots(doctor_id, date_str)
    return jsonify({
        "doctor_id": doctor_id,
        "date": date_str,
        "slots": slots,
        "booked_slots": booked,
        "total_available": sum(1 for s in slots if s["available"])
    })


@appointments_bp.route("/appointments/check-conflict", methods=["POST"])
def check_appointment_conflict():
    """Real-time pre-flight conflict checker before submitting form."""
    data = request.json or {}
    doctor_id = int(data.get("doctor_id", 0))
    patient_id = int(data.get("patient_id", 0))
    appt_date = data.get("appt_date")
    appt_time = data.get("appt_time")
    exclude_id = data.get("exclude_id")

    if not (doctor_id and appt_date and appt_time):
        return jsonify({"has_conflict": False, "message": "Incomplete slot parameters."})

    doc_conflict = appointment_model.has_conflict(doctor_id, appt_date, appt_time, exclude_id)
    if doc_conflict:
        return jsonify({
            "has_conflict": True,
            "type": "DOCTOR_OVERLAP",
            "message": f"Conflict: {doc_conflict['doctor']} is already booked at {appt_time} on {appt_date}."
        })

    if patient_id:
        pat_conflict = appointment_model.has_patient_conflict(patient_id, appt_date, appt_time, exclude_id)
        if pat_conflict:
            return jsonify({
                "has_conflict": True,
                "type": "PATIENT_OVERLAP",
                "message": f"Conflict: Patient already has an appointment with {pat_conflict['doctor']} at {appt_time}."
            })

    return jsonify({"has_conflict": False, "message": "Slot is available."})

