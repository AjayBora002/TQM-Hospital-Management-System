"""
triage.py -- REST API Blueprint for Emergency Priority Triage Queue with RBAC.
"""
from flask import Blueprint, request, jsonify
from models import triage as triage_model
from auth.permissions import require_permission

triage_bp = Blueprint("triage", __name__)


@triage_bp.route("/triage/queue", methods=["GET"])
@require_permission("clinical", "view")
def get_triage_queue():
    queue = triage_model.get_emergency_queue()
    summary = {
        "total_waiting": len(queue),
        "code_red": sum(1 for q in queue if q["tier"] == "Code Red"),
        "code_yellow": sum(1 for q in queue if q["tier"] == "Code Yellow"),
        "code_green": sum(1 for q in queue if q["tier"] == "Code Green"),
    }
    return jsonify({
        "summary": summary,
        "queue": queue
    }), 200


@triage_bp.route("/triage/evaluate", methods=["POST"])
@require_permission("clinical", "view")
def evaluate_vitals():
    data = request.get_json() or {}
    res = triage_model.evaluate_triage_tier(
        systolic=data.get("systolic"),
        diastolic=data.get("diastolic"),
        pulse=data.get("pulse"),
        temperature=data.get("temperature"),
        spo2=data.get("spo2")
    )
    return jsonify(res), 200
