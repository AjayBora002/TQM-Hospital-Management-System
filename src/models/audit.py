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


def add_defect(category, description, severity, module="General"):
    from config import DEFECT_CATEGORIES, DEFECT_SEVERITY
    from utils.exception_handler import ValidationError
    if category not in DEFECT_CATEGORIES:
        raise ValidationError(f"Defect category must be one of {', '.join(DEFECT_CATEGORIES)}.", field="category")
    if severity not in DEFECT_SEVERITY:
        raise ValidationError(f"Defect severity must be one of {', '.join(DEFECT_SEVERITY)}.", field="severity")
    if not description or not str(description).strip():
        raise ValidationError("Defect description cannot be empty.", field="description")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO defect_log (category, description, severity, status, logged_at) VALUES (?,?,?,?,?)",
        (category, str(description).strip(), severity, "Open", now())
    )
    new_id = cur.lastrowid
    conn.commit()
    conn.close()

    # Synchronize dual-tier persistence with TQM checksheet CSV
    try:
        from utils.logging_service import log_defect
        log_defect(module=module, error_category=category, count=1, remarks=str(description).strip())
    except Exception:
        pass

    return new_id


def update_defect_status(defect_id, status):
    from config import DEFECT_STATUS
    from utils.exception_handler import ValidationError
    if status not in DEFECT_STATUS:
        raise ValidationError(f"Defect status must be one of {', '.join(DEFECT_STATUS)}.", field="status")
    conn = get_connection()
    conn.execute("UPDATE defect_log SET status=? WHERE defect_id=?", (status, defect_id))
    conn.commit()
    conn.close()


def defect_counts_by_category():
    conn = get_connection()
    rows = conn.execute(
        "SELECT category, COUNT(*) AS cnt FROM defect_log GROUP BY category ORDER BY cnt DESC"
    ).fetchall()
    conn.close()
    return {r["category"]: r["cnt"] for r in rows}
