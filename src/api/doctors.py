"""
doctors.py -- Doctor directory, profiles, and choices REST API endpoints with RBAC.
"""
from flask import Blueprint, request, jsonify
import models.doctor as doctor_model
import models.doctor_profile as doc_profile_model
from auth.permissions import require_permission
from .helpers import rows_to_list

doctors_bp = Blueprint("doctors", __name__)


@doctors_bp.route("/doctors", methods=["GET"])
@require_permission("front_office", "view")
def get_doctors():
    return jsonify(rows_to_list(doctor_model.list_all()))


@doctors_bp.route("/doctors/specialized", methods=["GET"])
@require_permission("front_office", "view")
def get_specialized_doctors():
    department = request.args.get("department")
    docs = doc_profile_model.list_specialized_doctors(department=department)
    return jsonify(docs), 200


@doctors_bp.route("/doctors/choices", methods=["GET"])
@require_permission("front_office", "view")
def get_doctor_choices():
    cmap = doctor_model.choices_map()
    return jsonify([{"id": v, "label": k} for k, v in cmap.items()])


@doctors_bp.route("/doctors", methods=["POST"])
@require_permission("people", "create")
def create_doctor():
    data = request.json or {}
    new_id = doctor_model.add(
        full_name=data.get("full_name"),
        department=data.get("department"),
        phone=data.get("phone")
    )
    if data.get("specialization"):
        doc_profile_model.save_profile(
            doctor_id=new_id,
            specialization=data.get("specialization"),
            qualifications=data.get("qualifications", "MBBS, MD"),
            experience_years=int(data.get("experience_years", 5)),
            consultation_fee=float(data.get("consultation_fee", 500.0)),
            room_number=data.get("room_number", "OPD-101"),
            max_daily_patients=int(data.get("max_daily_patients", 30))
        )
    return jsonify({"doctor_id": new_id, "status": "created"}), 201


@doctors_bp.route("/doctors/<int:doctor_id>", methods=["PUT"])
@require_permission("people", "edit")
def update_doctor(doctor_id):
    data = request.json or {}
    doctor_model.update(
        doctor_id=doctor_id,
        full_name=data.get("full_name"),
        department=data.get("department"),
        phone=data.get("phone")
    )
    if data.get("specialization"):
        doc_profile_model.save_profile(
            doctor_id=doctor_id,
            specialization=data.get("specialization"),
            qualifications=data.get("qualifications", "MBBS, MD"),
            experience_years=int(data.get("experience_years", 5)),
            consultation_fee=float(data.get("consultation_fee", 500.0)),
            room_number=data.get("room_number", "OPD-101"),
            max_daily_patients=int(data.get("max_daily_patients", 30))
        )
    return jsonify({"status": "updated"})


@doctors_bp.route("/doctors/<int:doctor_id>", methods=["DELETE"])
@require_permission("people", "delete")
def delete_doctor(doctor_id):
    doctor_model.delete(doctor_id)
    return jsonify({"status": "deleted"})
