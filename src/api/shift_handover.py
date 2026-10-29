"""
shift_handover.py -- REST API Blueprint for Nursing & Clinical Shift Handovers with RBAC.
"""
from flask import Blueprint, request, jsonify, session
from models import shift_handover as handover_model
from auth.permissions import require_permission

shift_handover_bp = Blueprint("shift_handover_api", __name__)


@shift_handover_bp.route("/shift-handover", methods=["GET"])
@require_permission("inpatient", "view")
def get_handovers():
    ward_id = request.args.get("ward_id")
    dept = request.args.get("department")
    handovers = handover_model.list_handovers(
        department=dept,
        ward_id=int(ward_id) if ward_id else None
    )
    return jsonify(handovers), 200


@shift_handover_bp.route("/shift-handover", methods=["POST"])
@require_permission("inpatient", "create")
def post_handover():
    data = request.get_json() or {}
    outgoing = session.get("full_name", data.get("outgoing_nurse_name", "Sister Sunita Patel"))
    incoming = data.get("incoming_nurse_name", "Nurse Rekha Sharma")
    dept = data.get("department", "Cardiology")
    shift_from = data.get("shift_from", "Morning")
    shift_to = data.get("shift_to", "Evening")
    critical_pats = data.get("critical_patients", "None")
    pending = data.get("pending_orders", "None")
    notes = data.get("general_notes", "")
    ward_id = data.get("ward_id")

    h_id = handover_model.create_handover(
        department=dept,
        shift_from=shift_from,
        shift_to=shift_to,
        outgoing_nurse=outgoing,
        incoming_nurse=incoming,
        critical_patients=critical_pats,
        pending_orders=pending,
        general_notes=notes,
        ward_id=int(ward_id) if ward_id else None
    )
    return jsonify({"message": "Shift handover logged successfully", "handover_id": h_id}), 201
