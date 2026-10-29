"""
medicines.py -- Pharmacy inventory and medicine management REST API endpoints with RBAC.
"""
from flask import Blueprint, request, jsonify
import models.medicine as medicine_model
from auth.permissions import require_permission
from .helpers import rows_to_list

medicines_bp = Blueprint("medicines", __name__)


@medicines_bp.route("/medicines", methods=["GET"])
@require_permission("pharmacy", "view")
def get_medicines():
    low_stock = request.args.get("low_stock", "0") == "1"
    expired = request.args.get("expired", "0") == "1"
    if expired:
        rows = medicine_model.expired_medicines()
    elif low_stock:
        rows = medicine_model.low_stock()
    else:
        rows = medicine_model.list_all()
    return jsonify(rows_to_list(rows))


@medicines_bp.route("/medicines/expired", methods=["GET"])
@require_permission("pharmacy", "view")
def get_expired_medicines():
    rows = medicine_model.expired_medicines()
    return jsonify(rows_to_list(rows))


@medicines_bp.route("/medicines", methods=["POST"])
@require_permission("pharmacy", "create")
def create_medicine():
    data = request.json or {}
    new_id = medicine_model.add(
        name=data.get("name"),
        category=data.get("category"),
        stock_qty=int(data.get("stock_qty", 0)),
        unit_price=float(data.get("unit_price", 0)),
        reorder_level=int(data.get("reorder_level", 10)),
        batch_no=data.get("batch_no", "BAT-2026-01"),
        expiry_date=data.get("expiry_date", "2027-12-31")
    )
    return jsonify({"medicine_id": new_id, "status": "created"}), 201


@medicines_bp.route("/medicines/<int:medicine_id>", methods=["PUT"])
@require_permission("pharmacy", "edit")
def update_medicine(medicine_id):
    data = request.json or {}
    medicine_model.update(
        medicine_id=medicine_id,
        name=data.get("name"),
        category=data.get("category"),
        stock_qty=int(data.get("stock_qty", 0)),
        unit_price=float(data.get("unit_price", 0)),
        reorder_level=int(data.get("reorder_level", 10)),
        batch_no=data.get("batch_no", "BAT-2026-01"),
        expiry_date=data.get("expiry_date", "2027-12-31")
    )
    return jsonify({"status": "updated"})


@medicines_bp.route("/medicines/<int:medicine_id>", methods=["DELETE"])
@require_permission("pharmacy", "delete")
def delete_medicine(medicine_id):
    medicine_model.delete(medicine_id)
    return jsonify({"status": "deleted"})
