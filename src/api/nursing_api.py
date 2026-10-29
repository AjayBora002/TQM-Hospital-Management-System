"""
nursing_api.py -- REST API Blueprint for Nursing Station & Inpatient Ward Care.
"""
from flask import Blueprint, request, jsonify
from models import nursing as nursing_model

nursing_bp = Blueprint("nursing_api", __name__)


@nursing_bp.route("/nursing/roster", methods=["GET"])
def get_nursing_roster():
    ward_id = request.args.get("ward_id")
    dept = request.args.get("department")
    roster = nursing_model.list_nurses(
        department=dept,
        ward_id=int(ward_id) if ward_id else None
    )
    return jsonify(roster), 200


@nursing_bp.route("/nursing/inpatients", methods=["GET"])
def get_ward_patients():
    ward_id = request.args.get("ward_id")
    patients = nursing_model.get_ward_inpatients(
        ward_id=int(ward_id) if ward_id else None
    )
    return jsonify(patients), 200

