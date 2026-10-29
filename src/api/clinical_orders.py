"""
clinical_orders.py -- REST API Blueprint for Doctor Clinical Orders to Nursing Station with RBAC.
"""
from flask import Blueprint, request, jsonify, session
from models import clinical_order as order_model
from auth.permissions import require_permission

clinical_orders_bp = Blueprint("clinical_orders_api", __name__)


@clinical_orders_bp.route("/clinical-orders", methods=["GET"])
@require_permission("clinical", "view")
def get_orders():
    patient_id = request.args.get("patient_id")
    ward_id = request.args.get("ward_id")
    status = request.args.get("status")
    urgency = request.args.get("urgency")

    orders = order_model.list_orders(
        patient_id=int(patient_id) if patient_id else None,
        ward_id=int(ward_id) if ward_id else None,
        status=status,
        urgency=urgency
    )
    return jsonify(orders), 200


@clinical_orders_bp.route("/clinical-orders", methods=["POST"])
@require_permission("clinical", "create")
def place_order():
    data = request.get_json() or {}
    doctor_name = session.get("full_name", data.get("doctor_name", "Dr. Rajesh Sharma"))
    doctor_id = int(data.get("doctor_id", 1))
    patient_id = int(data.get("patient_id"))
    order_type = data.get("order_type")
    order_text = data.get("order_text")
    urgency = data.get("urgency", "Routine")
    ward_id = data.get("ward_id")
    bed_number = data.get("bed_number")

    new_id = order_model.create_order(
        patient_id=patient_id,
        doctor_id=doctor_id,
        doctor_name=doctor_name,
        order_type=order_type,
        order_text=order_text,
        urgency=urgency,
        ward_id=int(ward_id) if ward_id else None,
        bed_number=bed_number,
        performed_by=session.get("username", "doctor")
    )
    return jsonify({"message": "Clinical order placed", "order_id": new_id}), 201


@clinical_orders_bp.route("/clinical-orders/<int:order_id>/acknowledge", methods=["POST"])
@require_permission("clinical", "edit")
def acknowledge_order(order_id):
    nurse_name = session.get("full_name", "Sister Sunita Patel")
    order_model.acknowledge_order(order_id, nurse_name=nurse_name)
    return jsonify({"message": "Order acknowledged by nursing station"}), 200


@clinical_orders_bp.route("/clinical-orders/<int:order_id>/complete", methods=["POST"])
@require_permission("clinical", "edit")
def complete_order(order_id):
    data = request.get_json() or {}
    nurse_name = session.get("full_name", "Sister Sunita Patel")
    notes = data.get("execution_notes", "")
    order_model.complete_order(order_id, nurse_name=nurse_name, execution_notes=notes)
    return jsonify({"message": "Clinical order executed and documented"}), 200
