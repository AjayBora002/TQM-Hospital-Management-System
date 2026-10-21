"""
quality_audit.py -- Model for NABH & ISO 9001 Hospital Quality Inspection Checklists.
Assesses clinical and operational compliance across hospital departments with automated
compliance percentage scoring and non-conformance detection.
"""
from datetime import datetime
from database.db_manager import get_connection, log_audit
from utils.exception_handler import ValidationError


def _now():
    return datetime.now().isoformat(timespec="seconds")


def add_audit_entry(
    department: str,
    standard_code: str,
    criterion: str,
    score: int,
    max_score: int = 10,
    audited_by: str = "TQM Lead",
    audit_date: str = None,
    corrective_action: str = ""
):
    """Logs a formal quality audit inspection item against NABH/ISO standards."""
    if not department or not department.strip():
        raise ValidationError("Department is required", field="department")
    if not standard_code or not standard_code.strip():
        raise ValidationError("Standard code (e.g. 'NABH-COP.1') is required", field="standard_code")
    if not criterion or not criterion.strip():
        raise ValidationError("Criterion description is required", field="criterion")

    try:
        score = int(score)
        max_score = int(max_score)
        if score < 0 or score > max_score:
            raise ValueError()
    except (TypeError, ValueError):
        raise ValidationError(f"Score must be between 0 and {max_score}", field="score")

    # Evaluate compliance classification
    ratio = score / max_score
    if ratio >= 0.80:
        compliance_status = "Compliant"
    elif ratio >= 0.50:
        compliance_status = "Minor Non-Conformance"
    else:
        compliance_status = "Major Non-Conformance"

    audit_date = audit_date or _now()[:10]
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO quality_audits (department, standard_code, criterion, score, max_score, compliance_status, audited_by, audit_date, corrective_action) "
            "VALUES (?,?,?,?,?,?,?,?,?)",
            (department.strip(), standard_code.strip(), criterion.strip(), score, max_score, compliance_status, audited_by.strip(), audit_date, (corrective_action or "").strip())
        )
        audit_id = cur.lastrowid
        log_audit(
            conn, "quality_audits", audit_id, "INSERT",
            f"Logged audit '{standard_code}' for '{department}': Score {score}/{max_score} ({compliance_status})",
            audited_by
        )
        conn.commit()
        return audit_id
    finally:
        conn.close()


def get_compliance_summary():
    """Calculates overall and departmental hospital quality compliance percentages."""
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM quality_audits ORDER BY audit_id").fetchall()
        if not rows:
            return {
                "total_criteria": 0,
                "overall_score": 0,
                "overall_max_score": 0,
                "compliance_percentage": 100.0,
                "departments": {},
                "non_conformances": []
            }

        total_score = sum(r["score"] for r in rows)
        total_max = sum(r["max_score"] for r in rows)
        compliance_pct = round((total_score / total_max) * 100, 2) if total_max > 0 else 100.0

        dept_map = {}
        non_conformances = []
        for r in rows:
            d = r["department"]
            if d not in dept_map:
                dept_map[d] = {"score": 0, "max_score": 0, "criteria_count": 0}
            dept_map[d]["score"] += r["score"]
            dept_map[d]["max_score"] += r["max_score"]
            dept_map[d]["criteria_count"] += 1

            if r["compliance_status"] != "Compliant":
                non_conformances.append(dict(r))

        dept_summary = {}
        for d, v in dept_map.items():
            pct = round((v["score"] / v["max_score"]) * 100, 1) if v["max_score"] > 0 else 100.0
            dept_summary[d] = {
                "score": v["score"],
                "max_score": v["max_score"],
                "compliance_pct": pct,
                "criteria_count": v["criteria_count"]
            }

        return {
            "total_criteria": len(rows),
            "overall_score": total_score,
            "overall_max_score": total_max,
            "compliance_percentage": compliance_pct,
            "departments": dept_summary,
            "non_conformances_count": len(non_conformances),
            "non_conformances": non_conformances
        }
    finally:
        conn.close()


def list_all():
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM quality_audits ORDER BY audit_id DESC").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def list_by_department(department: str):
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM quality_audits WHERE department = ? ORDER BY audit_id DESC", (department,)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()
