"""
auth.py -- REST API Blueprint for Authentication and Role-Based Access Control (RBAC).
"""
from flask import Blueprint, request, jsonify, session
from models import user as user_model
from utils.exception_handler import ValidationError

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")

    user = user_model.authenticate(username, password)
    if not user:
        return jsonify({"error": "Invalid username or password"}), 401

    session["user_id"] = user["user_id"]
    session["username"] = user["username"]
    session["role"] = user["role"]
    session["full_name"] = user["full_name"]

    return jsonify({
        "message": "Login successful",
        "user": user
    }), 200


@auth_bp.route("/auth/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"}), 200


@auth_bp.route("/auth/current", methods=["GET"])
def current_user():
    user_id = session.get("user_id")
    if user_id:
        user = user_model.get_by_id(user_id)
        if user:
            return jsonify({"user": user, "authenticated": True}), 200

    # Default fallback to Admin demo user if no explicit session
    admin_user = user_model.get_by_username("admin")
    if admin_user:
        return jsonify({"user": admin_user, "authenticated": False, "demo_mode": True}), 200

    return jsonify({"user": {"username": "admin", "role": "Admin", "full_name": "System Admin"}, "authenticated": False}), 200


@auth_bp.route("/auth/users", methods=["GET"])
def list_users():
    users = user_model.list_users()
    return jsonify(users), 200
