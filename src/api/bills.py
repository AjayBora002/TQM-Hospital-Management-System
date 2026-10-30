"""
bills.py -- Patient billing and invoice REST API endpoints with server-side RBAC.
"""
from flask import Blueprint, request, jsonify, Response, session
import models.bill as bill_model
from auth.permissions import require_permission
from .helpers import rows_to_list

bills_bp = Blueprint("bills", __name__)


@bills_bp.route("/bills", methods=["GET"])
@require_permission("finance", "view")
def get_bills():
    bills_list = rows_to_list(bill_model.list_all())
    user_role = session.get("role", "")
    # Field-level security: Cashiers and front desk cannot access clinical data
    if user_role in ("Cashier", "Receptionist"):
        for b in bills_list:
            b.pop("diagnosis", None)
            b.pop("allergies", None)
            b.pop("clinical_notes", None)
    return jsonify(bills_list)


@bills_bp.route("/bills", methods=["POST"])
@require_permission("finance", "create")
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
@require_permission("finance", "edit")
def update_bill_status(bill_id):
    data = request.json or {}
    bill_model.update_status(bill_id, data.get("payment_status", "Paid"))
    return jsonify({"status": "updated"})


@bills_bp.route("/bills/<int:bill_id>", methods=["DELETE"])
@require_permission("finance", "delete")
def delete_bill(bill_id):
    bill_model.delete(bill_id)
    return jsonify({"status": "deleted"})


@bills_bp.route("/bills/<int:bill_id>/receipt", methods=["GET"])
@require_permission("finance", "view")
def get_bill_receipt(bill_id):
    from utils.report_generator import generate_bill_receipt_html
    try:
        html = generate_bill_receipt_html(bill_id)
        return Response(html, mimetype="text/html")
    except Exception as e:
        return jsonify({"error": str(e)}), 404
