"""
rooms.py -- Room allocation and management REST API endpoints
"""
from flask import Blueprint, request, jsonify
import models.room as room_model
from .helpers import rows_to_list

rooms_bp = Blueprint("rooms", __name__)

@rooms_bp.route("/rooms", methods=["GET"])
def get_rooms():
    return jsonify(rows_to_list(room_model.list_all()))

@rooms_bp.route("/rooms/choices", methods=["GET"])
def get_room_choices():
    avail_only = request.args.get("available_only", "0") == "1"
    cmap = room_model.choices_map(only_available=avail_only)
    return jsonify([{"id": v, "label": k} for k, v in cmap.items()])

@rooms_bp.route("/rooms", methods=["POST"])
def create_room():
    data = request.json or {}
    new_id = room_model.add(
        room_number=data.get("room_number"),
        room_type=data.get("room_type"),
        status=data.get("status", "Available"),
        rate_per_day=float(data.get("rate_per_day", 0))
    )
    return jsonify({"room_id": new_id, "status": "created"}), 201

@rooms_bp.route("/rooms/<int:room_id>", methods=["PUT"])
def update_room(room_id):
    data = request.json or {}
    room_model.update(
        room_id=room_id,
        room_number=data.get("room_number"),
        room_type=data.get("room_type"),
        status=data.get("status"),
        rate_per_day=float(data.get("rate_per_day", 0))
    )
    return jsonify({"status": "updated"})

@rooms_bp.route("/rooms/<int:room_id>", methods=["DELETE"])
def delete_room(room_id):
    room_model.delete(room_id)
    return jsonify({"status": "deleted"})
