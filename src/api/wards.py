"""
wards.py -- REST API Blueprint for Inpatient Wards, Bed Board & Occupancy.
"""
from flask import Blueprint, request, jsonify, session
from models import ward_bed as ward_model

wards_bp = Blueprint("wards_api", __name__)


@wards_bp.route("/wards", methods=["GET"])
def get_wards():
    wards = ward_model.list_wards()
    return jsonify(wards), 200


@wards_bp.route("/wards/bed-board", methods=["GET"])
def get_bed_board():
    ward_id = request.args.get("ward_id")
    ward_id = int(ward_id) if ward_id else None
    matrix = ward_model.get_ward_bed_matrix(ward_id=ward_id)
    return jsonify(matrix), 200


@wards_bp.route("/wards/beds/<int:room_id>/status", methods=["PUT"])
def set_bed_status(room_id):
    data = request.get_json() or {}
    new_status = data.get("status")
    performed_by = session.get("username", "ward_manager")
    ward_model.update_bed_status(room_id, new_status, performed_by=performed_by)
    return jsonify({"message": "Bed status updated successfully"}), 200


@wards_bp.route("/wards/occupancy", methods=["GET"])
def get_occupancy():
    stats = ward_model.get_ward_occupancy_stats()
    return jsonify(stats), 200

