"""
opd_queue.py -- REST API Blueprint for OPD Token Queue & Consultation Desk with RBAC.
"""
from flask import Blueprint, request, jsonify, session
from models import opd_queue as queue_model
from auth.permissions import require_permission

opd_queue_bp = Blueprint("opd_queue_api", __name__)


@opd_queue_bp.route("/opd-queue/today", methods=["GET"])
@require_permission("front_office", "view")
def get_today_queue():
    doctor_id = request.args.get("doctor_id")
    doctor_id = int(doctor_id) if doctor_id else None
    queue = queue_model.get_today_queue(doctor_id=doctor_id)
    return jsonify(queue), 200


@opd_queue_bp.route("/opd-queue/token", methods=["POST"])
@require_permission("front_office", "create")
def issue_token():
    data = request.get_json() or {}
    pat_id = int(data.get("patient_id"))
    doc_id = int(data.get("doctor_id"))
    appt_id = data.get("appointment_id")
    priority = data.get("priority", "Normal")
    user = session.get("username", "receptionist")

    result = queue_model.generate_token(
        patient_id=pat_id,
        doctor_id=doc_id,
        appointment_id=int(appt_id) if appt_id else None,
        priority=priority,
        performed_by=user
    )
    return jsonify(result), 201


@opd_queue_bp.route("/opd-queue/<int:queue_id>/call", methods=["POST"])
@require_permission("clinical", "edit")
def call_token(queue_id):
    user = session.get("username", "doctor")
    queue_model.call_patient(queue_id, performed_by=user)
    return jsonify({"message": "Patient called to consultation room"}), 200


@opd_queue_bp.route("/opd-queue/<int:queue_id>/complete", methods=["POST"])
@require_permission("clinical", "edit")
def complete_token(queue_id):
    user = session.get("username", "doctor")
    queue_model.complete_consultation(queue_id, performed_by=user)
    return jsonify({"message": "Consultation completed"}), 200
