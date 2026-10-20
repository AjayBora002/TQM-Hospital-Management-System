"""
system.py -- REST API Blueprint for System Administration & Automated Backups.
"""
from flask import Blueprint, jsonify, session
from utils.backup_service import backup_database, list_backups

system_bp = Blueprint("system", __name__)


@system_bp.route("/system/backup", methods=["POST"])
def trigger_backup():
    user = session.get("username", "admin")
    result = backup_database(performed_by=user)
    return jsonify({
        "message": "Database backup completed successfully",
        "backup": result
    }), 200


@system_bp.route("/system/backups", methods=["GET"])
def get_backups():
    backups = list_backups()
    return jsonify(backups), 200
