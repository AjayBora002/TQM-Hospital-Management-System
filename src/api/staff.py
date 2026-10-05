"""
staff.py -- Hospital staff and nurse management REST API endpoints
"""
from flask import Blueprint, request, jsonify
import models.staff as staff_model
from .helpers import rows_to_list

staff_bp = Blueprint("staff", __name__)

@staff_bp.route("/staff", methods=["GET"])
def get_staff():
    return jsonify(rows_to_list(staff_model.list_all()))

@staff_bp.route("/staff", methods=["POST"])
def create_staff():
    data = request.json or {}
    new_id = staff_model.add(
        full_name=data.get("full_name"),
        role=data.get("role"),
        shift=data.get("shift"),
        phone=data.get("phone")
    )
    return jsonify({"staff_id": new_id, "status": "created"}), 201

@staff_bp.route("/staff/<int:staff_id>", methods=["PUT"])
def update_staff(staff_id):
    data = request.json or {}
    staff_model.update(
        staff_id=staff_id,
        full_name=data.get("full_name"),
        role=data.get("role"),
        shift=data.get("shift"),
        phone=data.get("phone")
    )
    return jsonify({"status": "updated"})

@staff_bp.route("/staff/<int:staff_id>", methods=["DELETE"])
def delete_staff(staff_id):
    staff_model.delete(staff_id)
    return jsonify({"status": "deleted"})
