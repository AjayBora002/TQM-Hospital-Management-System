"""audit.py -- Read access to audit_log, and CRUD for defect_log (SQC checksheet)."""
from datetime import datetime
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_manager import get_connection  # noqa: E402


def now():
    return datetime.now().isoformat(timespec="seconds")


def list_audit(limit=500):
    conn = get_connection()
    rows = conn.execute("SELECT * FROM audit_log ORDER BY log_id DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return rows


def list_defects():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM defect_log ORDER BY defect_id DESC").fetchall()
    conn.close()
    return rows


def add_defect(category, description, severity):
    conn = get_connection()
    conn.execute(
        "INSERT INTO defect_log (category, description, severity, status, logged_at) VALUES (?,?,?,?,?)",
        (category, description, severity, "Open", now())
    )
    conn.commit()
    conn.close()


def defect_counts_by_category():
    conn = get_connection()
    rows = conn.execute(
        "SELECT category, COUNT(*) AS cnt FROM defect_log GROUP BY category ORDER BY cnt DESC"
    ).fetchall()
    conn.close()
    return {r["category"]: r["cnt"] for r in rows}
