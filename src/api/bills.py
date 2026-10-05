"""
bills.py -- Patient billing and invoice REST API endpoints
"""
from flask import Blueprint, request, jsonify
import models.bill as bill_model
from .helpers import rows_to_list

bills_bp = Blueprint("bills", __name__)

@bills_bp.route("/bills", methods=["GET"])
def get_bills():
    return jsonify(rows_to_list(bill_model.list_all()))

@bills_bp.route("/bills", methods=["POST"])
def create_bill():
    data = request.json or {}
    new_id, total = bill_model.add(
        patient_id=int(data.get("patient_id")),
        room_charges=float(data.get("room_charges", 0)),
        consultation_charges=float(data.get("consultation_charges", 0)),
        medicine_charges=float(data.get("medicine_charges", 0)),
        payment_method=data.get("payment_method", "Cash"),
        payment_status=data.get("payment_status", "Paid")
    )
    return jsonify({"bill_id": new_id, "total": total, "status": "created"}), 201

@bills_bp.route("/bills/<int:bill_id>/status", methods=["PUT"])
def update_bill_status(bill_id):
    data = request.json or {}
    bill_model.update_status(bill_id, data.get("payment_status", "Paid"))
    return jsonify({"status": "updated"})

@bills_bp.route("/bills/<int:bill_id>", methods=["DELETE"])
def delete_bill(bill_id):
    bill_model.delete(bill_id)
    return jsonify({"status": "deleted"})
