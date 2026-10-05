"""
audit.py -- Audit log and defect checksheet REST API endpoints
"""
from flask import Blueprint, request, jsonify
import models.audit as audit_model
from .helpers import rows_to_list

audit_bp = Blueprint("audit", __name__)

@audit_bp.route("/audit", methods=["GET"])
def get_audit():
    return jsonify(rows_to_list(audit_model.list_audit(limit=200)))

@audit_bp.route("/defects", methods=["GET"])
def get_defects():
    return jsonify(rows_to_list(audit_model.list_defects()))

@audit_bp.route("/defects", methods=["POST"])
def create_defect():
    data = request.json or {}
    audit_model.add_defect(
        category=data.get("category"),
        description=data.get("description"),
        severity=data.get("severity")
    )
    return jsonify({"status": "created"}), 201
