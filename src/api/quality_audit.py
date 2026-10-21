"""
quality_audit.py -- REST API Blueprint for NABH & ISO 9001 Hospital Quality Inspection Checklists.
"""
from flask import Blueprint, request, jsonify, session
from models import quality_audit as audit_model
from utils.exception_handler import ValidationError

quality_audit_bp = Blueprint("quality_audit", __name__)


@quality_audit_bp.route("/quality-audits", methods=["GET"])
def get_quality_audits():
    dept = request.args.get("department")
    if dept:
        audits = audit_model.list_by_department(dept)
    else:
        audits = audit_model.list_all()
    return jsonify(audits), 200


@quality_audit_bp.route("/quality-audits/summary", methods=["GET"])
def get_compliance_summary():
    summary = audit_model.get_compliance_summary()
    return jsonify(summary), 200


@quality_audit_bp.route("/quality-audits", methods=["POST"])
def add_quality_audit():
    data = request.get_json() or {}
    user = session.get("username", "tqm_lead")
    try:
        new_id = audit_model.add_audit_entry(
            department=data.get("department"),
            standard_code=data.get("standard_code"),
            criterion=data.get("criterion"),
            score=data.get("score"),
            max_score=data.get("max_score", 10),
            audited_by=user,
            audit_date=data.get("audit_date"),
            corrective_action=data.get("corrective_action", "")
        )
        return jsonify({"message": "Quality audit entry recorded", "audit_id": new_id}), 201
    except ValidationError as e:
        return jsonify({"error": e.message, "field": e.field}), 400
