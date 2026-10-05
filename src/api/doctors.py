"""
doctors.py -- Doctor management REST API endpoints
"""
from flask import Blueprint, request, jsonify
import models.doctor as doctor_model
from .helpers import rows_to_list

doctors_bp = Blueprint("doctors", __name__)

@doctors_bp.route("/doctors", methods=["GET"])
def get_doctors():
    return jsonify(rows_to_list(doctor_model.list_all()))

@doctors_bp.route("/doctors/choices", methods=["GET"])
def get_doctor_choices():
    cmap = doctor_model.choices_map()
    return jsonify([{"id": v, "label": k} for k, v in cmap.items()])

@doctors_bp.route("/doctors", methods=["POST"])
def create_doctor():
    data = request.json or {}
    new_id = doctor_model.add(
        full_name=data.get("full_name"),
        department=data.get("department"),
        phone=data.get("phone")
    )
    return jsonify({"doctor_id": new_id, "status": "created"}), 201

@doctors_bp.route("/doctors/<int:doctor_id>", methods=["PUT"])
def update_doctor(doctor_id):
    data = request.json or {}
    doctor_model.update(
        doctor_id=doctor_id,
        full_name=data.get("full_name"),
        department=data.get("department"),
        phone=data.get("phone")
    )
    return jsonify({"status": "updated"})

@doctors_bp.route("/doctors/<int:doctor_id>", methods=["DELETE"])
def delete_doctor(doctor_id):
    doctor_model.delete(doctor_id)
    return jsonify({"status": "deleted"})
