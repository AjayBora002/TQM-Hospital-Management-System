"""
medicines.py -- Pharmacy inventory and medicine management REST API endpoints
"""
from flask import Blueprint, request, jsonify
import models.medicine as medicine_model
from .helpers import rows_to_list

medicines_bp = Blueprint("medicines", __name__)

@medicines_bp.route("/medicines", methods=["GET"])
def get_medicines():
    low_stock = request.args.get("low_stock", "0") == "1"
    if low_stock:
        rows = medicine_model.low_stock()
    else:
        rows = medicine_model.list_all()
    return jsonify(rows_to_list(rows))

@medicines_bp.route("/medicines", methods=["POST"])
def create_medicine():
    data = request.json or {}
    new_id = medicine_model.add(
        name=data.get("name"),
        category=data.get("category"),
        stock_qty=int(data.get("stock_qty", 0)),
        unit_price=float(data.get("unit_price", 0)),
        reorder_level=int(data.get("reorder_level", 10))
    )
    return jsonify({"medicine_id": new_id, "status": "created"}), 201

@medicines_bp.route("/medicines/<int:medicine_id>", methods=["PUT"])
def update_medicine(medicine_id):
    data = request.json or {}
    medicine_model.update(
        medicine_id=medicine_id,
        name=data.get("name"),
        category=data.get("category"),
        stock_qty=int(data.get("stock_qty", 0)),
        unit_price=float(data.get("unit_price", 0)),
        reorder_level=int(data.get("reorder_level", 10))
    )
    return jsonify({"status": "updated"})

@medicines_bp.route("/medicines/<int:medicine_id>", methods=["DELETE"])
def delete_medicine(medicine_id):
    medicine_model.delete(medicine_id)
    return jsonify({"status": "deleted"})
