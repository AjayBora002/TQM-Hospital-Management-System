"""
prescriptions.py -- REST API Blueprint for Prescriptions, Safety Verification, and Pharmacy Dispensing.
"""
from flask import Blueprint, request, jsonify, session
from models import prescription as prescription_model
from auth.permissions import require_permission
from utils.exception_handler import ValidationError

prescriptions_bp = Blueprint("prescriptions", __name__)


@prescriptions_bp.route("/prescriptions", methods=["GET"])
@require_permission("pharmacy", "view")
def list_prescriptions():
    patient_id = request.args.get("patient_id")
    active_only = request.args.get("active_only") in ["1", "true", "True"]
    try:
        pid = int(patient_id) if patient_id else None
    except ValueError:
        pid = None

    rx_list = prescription_model.list_prescriptions(patient_id=pid, active_only=active_only)
    return jsonify(rx_list), 200


@prescriptions_bp.route("/prescriptions", methods=["POST"])
@require_permission("clinical", "create")
def create_prescription():
    data = request.get_json() or {}
    user = session.get("username", "doctor_user")
    try:
        rx_id = prescription_model.create_prescription(
            patient_id=int(data.get("patient_id")),
            doctor_id=int(data.get("doctor_id")),
            medicine_id=int(data.get("medicine_id")),
            dosage=data.get("dosage", ""),
            frequency=data.get("frequency", ""),
            duration_days=int(data.get("duration_days", 5)),
            instructions=data.get("instructions", ""),
            appointment_id=data.get("appointment_id"),
            prescribed_date=data.get("prescribed_date"),
            performed_by=user
        )
        return jsonify({"message": "Prescription created successfully", "prescription_id": rx_id}), 201
    except (TypeError, ValueError) as e:
        return jsonify({"error": f"Invalid input parameter: {e}"}), 400
    except ValidationError as e:
        return jsonify({"error": e.message, "field": e.field}), 400


@prescriptions_bp.route("/prescriptions/<int:prescription_id>/dispense", methods=["POST"])
@require_permission("pharmacy", "edit")
def dispense_prescription(prescription_id):
    data = request.get_json() or {}
    user = session.get("username", "pharmacist_user")
    qty = data.get("qty")
    try:
        qty_int = int(qty) if qty is not None else None
        prescription_model.dispense_prescription(prescription_id, qty_dispensed=qty_int, performed_by=user)
        return jsonify({"message": f"Prescription #{prescription_id} dispensed and medicine inventory updated"}), 200
    except (TypeError, ValueError):
        return jsonify({"error": "Dispensed quantity must be an integer >= 1", "field": "qty"}), 400
    except ValidationError as e:
        return jsonify({"error": e.message, "field": e.field}), 400
