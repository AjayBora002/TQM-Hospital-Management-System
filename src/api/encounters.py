"""
encounters.py -- REST API Blueprint for SOAP Notes & Clinical Consultations.
"""
from flask import Blueprint, request, jsonify, session
from models import encounter as encounter_model

encounters_bp = Blueprint("encounters_api", __name__)


@encounters_bp.route("/encounters/patient/<int:patient_id>", methods=["GET"])
def get_patient_encounters(patient_id):
    history = encounter_model.get_patient_encounters(patient_id)
    return jsonify(history), 200


@encounters_bp.route("/encounters", methods=["POST"])
def post_encounter():
    data = request.get_json() or {}
    pat_id = int(data.get("patient_id"))
    doc_id = int(data.get("doctor_id", 1))
    appt_id = data.get("appointment_id")
    chief = data.get("chief_complaint", "")
    history = data.get("history_illness", "")
    exam = data.get("examination", "")
    diag = data.get("diagnosis", "")
    plan = data.get("plan", "")
    notes = data.get("doctor_notes", "")
    follow_up = data.get("follow_up_date")
    user = session.get("username", "doctor")

    enc_id = encounter_model.create_encounter(
        patient_id=pat_id,
        doctor_id=doc_id,
        chief_complaint=chief,
        diagnosis=diag,
        appointment_id=int(appt_id) if appt_id else None,
        history_illness=history,
        examination=exam,
        plan=plan,
        doctor_notes=notes,
        follow_up_date=follow_up,
        performed_by=user
    )
    return jsonify({"message": "Consultation record saved", "encounter_id": enc_id}), 201

