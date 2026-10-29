"""
communication.py -- REST API Blueprint for Inter-Professional Doctor <-> Nurse Messaging & Alerts.
"""
from flask import Blueprint, request, jsonify, session
from models import communication as comm_model

communication_bp = Blueprint("communication_api", __name__)


@communication_bp.route("/communication/messages", methods=["GET"])
def get_messages():
    role = session.get("role")
    dept = request.args.get("department")
    messages = comm_model.list_messages(role=role, department=dept)
    return jsonify(messages), 200


@communication_bp.route("/communication/messages", methods=["POST"])
def post_message():
    data = request.get_json() or {}
    sender_name = session.get("full_name", data.get("sender_name", "Staff Member"))
    sender_role = session.get("role", data.get("sender_role", "Nurse"))
    sender_user_id = session.get("user_id", int(data.get("sender_user_id", 1)))

    msg_id = comm_model.send_message(
        sender_user_id=sender_user_id,
        sender_name=sender_name,
        sender_role=sender_role,
        recipient_role=data.get("recipient_role", "All"),
        subject=data.get("subject"),
        message_body=data.get("message_body"),
        urgency=data.get("urgency", "Normal"),
        patient_id=data.get("patient_id"),
        department=data.get("department"),
        recipient_user_id=data.get("recipient_user_id")
    )
    return jsonify({"message": "Message sent successfully", "message_id": msg_id}), 201


@communication_bp.route("/communication/messages/<int:message_id>/read", methods=["POST"])
def mark_read(message_id):
    comm_model.mark_as_read(message_id)
    return jsonify({"message": "Message marked as read"}), 200


@communication_bp.route("/communication/broadcast-vitals-alert", methods=["POST"])
def broadcast_alert():
    data = request.get_json() or {}
    pat_id = data.get("patient_id")
    summary = data.get("summary", "Critical abnormal vitals detected")
    sender_name = session.get("full_name", "Sister Sunita Patel")
    sender_role = session.get("role", "Nurse")

    msg_id = comm_model.broadcast_vitals_alert(
        patient_id=pat_id,
        vital_summary=summary,
        sender_name=sender_name,
        sender_role=sender_role
    )
    return jsonify({"message": "Code Red Alert broadcasted to Attending Medical Team", "message_id": msg_id}), 201

