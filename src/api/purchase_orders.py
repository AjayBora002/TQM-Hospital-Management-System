"""
purchase_orders.py -- REST API Blueprint for Pharmacy Purchase Orders and Replenishment with RBAC.
"""
from flask import Blueprint, request, jsonify, session
from models import purchase_order as po_model
from auth.permissions import require_permission
from utils.exception_handler import ValidationError

purchase_orders_bp = Blueprint("purchase_orders", __name__)


@purchase_orders_bp.route("/purchase-orders", methods=["GET"])
@require_permission("pharmacy", "view")
def get_purchase_orders():
    orders = po_model.list_all()
    return jsonify(orders), 200


@purchase_orders_bp.route("/purchase-orders/<int:po_id>", methods=["GET"])
@require_permission("pharmacy", "view")
def get_purchase_order(po_id):
    order = po_model.get_by_id(po_id)
    if not order:
        return jsonify({"error": f"PO #{po_id} not found"}), 404
    return jsonify(order), 200


@purchase_orders_bp.route("/purchase-orders", methods=["POST"])
@require_permission("pharmacy", "create")
def create_purchase_order():
    data = request.get_json() or {}
    user = session.get("username", "pharmacist")
    try:
        po_id = po_model.create_po(
            medicine_id=int(data.get("medicine_id")),
            supplier_name=data.get("supplier_name", "National MedSupply Ltd"),
            order_qty=int(data.get("order_qty", 50)),
            unit_cost=data.get("unit_cost"),
            order_date=data.get("order_date"),
            performed_by=user
        )
        return jsonify({"message": "Purchase order created", "po_id": po_id}), 201
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid medicine ID, quantity, or unit cost"}), 400
    except ValidationError as e:
        return jsonify({"error": e.message, "field": e.field}), 400


@purchase_orders_bp.route("/purchase-orders/auto-generate", methods=["POST"])
@require_permission("pharmacy", "create")
def auto_generate_pos():
    user = session.get("username", "pharmacist")
    created_ids = po_model.generate_auto_pos_for_low_stock(performed_by=user)
    return jsonify({
        "message": f"Generated {len(created_ids)} replenishment purchase orders",
        "created_po_ids": created_ids
    }), 200


@purchase_orders_bp.route("/purchase-orders/<int:po_id>/receive", methods=["POST"])
@require_permission("pharmacy", "approve")
def receive_purchase_order(po_id):
    data = request.get_json(silent=True) or {}
    user = session.get("username", "pharmacist")
    try:
        updated = po_model.receive_po(
            po_id=po_id,
            received_date=data.get("received_date"),
            performed_by=user
        )
        return jsonify({
            "message": f"PO #{po_id} received into inventory",
            "purchase_order": updated
        }), 200
    except ValidationError as e:
        return jsonify({"error": e.message, "field": e.field}), 400
