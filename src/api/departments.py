"""
departments.py -- REST API Blueprint for Hospital Departments & Specialties with RBAC.
"""
from flask import Blueprint, request, jsonify, session
from models import department as dept_model
from auth.permissions import require_permission

departments_bp = Blueprint("departments_api", __name__)


@departments_bp.route("/departments", methods=["GET"])
@require_permission("front_office", "view")
def get_departments():
    active_only = request.args.get("active_only") == "1"
    depts = dept_model.list_departments(active_only=active_only)
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
    user = session.get("username", "admin")
    new_id = dept_model.add(
        name=data.get("name"),
        code=data.get("code"),
        description=data.get("description", ""),
        head_of_dept=data.get("head_of_dept", ""),
        location=data.get("location", ""),
        phone=data.get("phone", ""),
        dept_type=data.get("type", "Clinical"),
        has_opd=int(data.get("has_opd", 1)),
        has_ipd=int(data.get("has_ipd", 1)),
        active=int(data.get("active", 1)),
        performed_by=user
    )
    return jsonify({"message": "Department created", "department_id": new_id}), 201


@departments_bp.route("/departments/<int:dept_id>", methods=["PUT"])
@require_permission("admin", "edit")
def update_department(dept_id):
    data = request.get_json() or {}
    user = session.get("username", "admin")
    dept_model.update(
        department_id=dept_id,
        name=data.get("name"),
        code=data.get("code"),
        description=data.get("description", ""),
        head_of_dept=data.get("head_of_dept", ""),
        location=data.get("location", ""),
        phone=data.get("phone", ""),
        dept_type=data.get("type", "Clinical"),
        has_opd=int(data.get("has_opd", 1)),
        has_ipd=int(data.get("has_ipd", 1)),
        active=int(data.get("active", 1)),
        performed_by=user
    )
    return jsonify({"message": "Department updated successfully"}), 200
