"""
departments.py -- REST API Blueprint for Hospital Departments & Specialties with RBAC.
"""
from flask import Blueprint, request, jsonify
from models import department as dept_model
from auth.permissions import require_permission

departments_bp = Blueprint("departments_api", __name__)


@departments_bp.route("/departments", methods=["GET"])
@require_permission("front_office", "view")
def get_departments():
    depts = dept_model.list_departments()
    return jsonify(depts), 200


@departments_bp.route("/departments/summary", methods=["GET"])
@require_permission("front_office", "view")
def get_departments_summary():
    summary = dept_model.get_department_summary()
    return jsonify(summary), 200


@departments_bp.route("/departments", methods=["POST"])
@require_permission("admin", "create")
def create_department():
    data = request.get_json() or {}
    new_id = dept_model.add(
        name=data.get("name"),
        code=data.get("code"),
        description=data.get("description", ""),
        location=data.get("location", ""),
        phone=data.get("phone", ""),
        has_opd=int(data.get("has_opd", 1)),
        has_ipd=int(data.get("has_ipd", 1))
    )
    return jsonify({"message": "Department created", "department_id": new_id}), 201
