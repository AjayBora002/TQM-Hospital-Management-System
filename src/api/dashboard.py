"""
dashboard.py -- Dashboard statistics and overview metrics with RBAC.
"""
from flask import Blueprint, jsonify
from database.db_manager import get_connection
from auth.permissions import require_permission
from .helpers import rows_to_list

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard/stats", methods=["GET"])
def dashboard_stats():
    conn = get_connection()
    try:
        tot_patients = conn.execute("SELECT COUNT(*) AS c FROM patients").fetchone()["c"]
        tot_doctors = conn.execute("SELECT COUNT(*) AS c FROM doctors").fetchone()["c"]
        scheduled_appts = conn.execute("SELECT COUNT(*) AS c FROM appointments WHERE status='Scheduled'").fetchone()["c"]
        avail_rooms = conn.execute("SELECT COUNT(*) AS c FROM rooms WHERE status='Available'").fetchone()["c"]
        low_stock_meds = conn.execute("SELECT COUNT(*) AS c FROM medicines WHERE stock_qty <= reorder_level").fetchone()["c"]
        rev_row = conn.execute("SELECT SUM(total_amount) AS rev FROM bills WHERE payment_status='Paid'").fetchone()
        total_rev = rev_row["rev"] if rev_row["rev"] else 0.0
        recent_audit = conn.execute("SELECT * FROM audit_log ORDER BY log_id DESC LIMIT 10").fetchall()

        from utils.sigma_calculator import get_system_process_capability
        sigma_metrics = get_system_process_capability()

        return jsonify({
            "total_patients": tot_patients,
            "total_doctors": tot_doctors,
            "scheduled_appts": scheduled_appts,
            "available_rooms": avail_rooms,
            "low_stock_meds": low_stock_meds,
            "total_revenue": total_rev,
            "recent_audit": rows_to_list(recent_audit),
            "sigma_level": sigma_metrics["current_sigma_level"],
            "dpmo": sigma_metrics["dpmo"],
            "process_yield": sigma_metrics["process_yield_percent"]
        }), 200
    finally:
        conn.close()


@dashboard_bp.route("/tqm/six-sigma", methods=["GET"])
@require_permission("quality", "view")
def get_six_sigma_capability():
    from utils.sigma_calculator import get_system_process_capability
    return jsonify(get_system_process_capability()), 200
