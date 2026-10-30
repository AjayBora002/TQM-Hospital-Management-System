"""
department.py -- Data-access and domain operations for Hospital Departments.
Manages OPD and IPD departments, medical specialties, and staff assignments.
Data-driven departments: Clinical, Diagnostic, Support, Administrative.
"""
from datetime import datetime
from database.db_manager import get_connection, log_audit
from utils.exception_handler import ValidationError


def list_departments(active_only: bool = False):
    """Returns hospital departments with doctor count and ward count."""
    conn = get_connection()
    try:
        where_clause = "WHERE d.active = 1" if active_only else ""
        rows = conn.execute(f"""
            SELECT d.department_id, d.name, d.code, d.description, d.head_of_dept, d.location, d.phone,
                   COALESCE(d.type, 'Clinical') as type, d.has_opd, d.has_ipd, COALESCE(d.active, 1) as active,
                   (SELECT COUNT(*) FROM doctors doc WHERE doc.department = d.name) AS doctor_count,
                   (SELECT COUNT(*) FROM wards w WHERE w.department_id = d.department_id) AS ward_count
            FROM departments d
            {where_clause}
            ORDER BY d.type, d.name
        """).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_by_id(department_id: int):
    """Retrieves a single department record by ID."""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM departments WHERE department_id = ?",
            (department_id,)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def add(name: str, code: str, description: str = "", head_of_dept: str = "", location: str = "", phone: str = "",
        dept_type: str = "Clinical", has_opd: int = 1, has_ipd: int = 1, active: int = 1, performed_by: str = "admin"):
    """Adds a new hospital department with unique code and name validation."""
    if not name or not name.strip():
        raise ValidationError("Department name is required", field="name")
    if not code or not code.strip():
        raise ValidationError("Department code is required", field="code")

    name = name.strip()
    code = code.strip().upper()
    dept_type = dept_type.strip() or "Clinical"

    conn = get_connection()
    try:
        exists = conn.execute("SELECT 1 FROM departments WHERE code = ? OR name = ?", (code, name)).fetchone()
        if exists:
            raise ValidationError(f"Department with code '{code}' or name '{name}' already exists", field="code")

        now_str = datetime.now().isoformat(timespec="seconds")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO departments (name, code, description, head_of_dept, location, phone, type, has_opd, has_ipd, active, created_at) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (name, code, description.strip(), head_of_dept.strip(), location.strip(), phone.strip(), dept_type, has_opd, has_ipd, active, now_str)
        )
        new_id = cursor.lastrowid
        log_audit(conn, "departments", new_id, "INSERT", f"Added department '{name}' ({code}) - Type: {dept_type}", performed_by)
        conn.commit()
        return new_id
    finally:
        conn.close()


def update(department_id: int, name: str, code: str, description: str = "", head_of_dept: str = "", location: str = "",
           phone: str = "", dept_type: str = "Clinical", has_opd: int = 1, has_ipd: int = 1, active: int = 1, performed_by: str = "admin"):
    """Updates an existing hospital department record with validation."""
    if not name or not name.strip():
        raise ValidationError("Department name is required", field="name")
    if not code or not code.strip():
        raise ValidationError("Department code is required", field="code")

    name = name.strip()
    code = code.strip().upper()
    dept_type = dept_type.strip() or "Clinical"

    conn = get_connection()
    try:
        dup = conn.execute("SELECT 1 FROM departments WHERE (code = ? OR name = ?) AND department_id != ?", (code, name, department_id)).fetchone()
        if dup:
            raise ValidationError(f"Another department with code '{code}' or name '{name}' already exists", field="code")

        conn.execute(
            "UPDATE departments SET name = ?, code = ?, description = ?, head_of_dept = ?, location = ?, phone = ?, type = ?, has_opd = ?, has_ipd = ?, active = ? WHERE department_id = ?",
            (name, code, description.strip(), head_of_dept.strip(), location.strip(), phone.strip(), dept_type, has_opd, has_ipd, active, department_id)
        )
        log_audit(conn, "departments", department_id, "UPDATE", f"Updated department '{name}' ({code})", performed_by)
        conn.commit()
        return True
    finally:
        conn.close()


def get_department_summary():
    """Aggregates high-level stats across all departments for the executive dashboard."""
    conn = get_connection()
    try:
        total_depts = conn.execute("SELECT COUNT(*) as c FROM departments").fetchone()["c"]
        opd_depts = conn.execute("SELECT COUNT(*) as c FROM departments WHERE has_opd = 1").fetchone()["c"]
        ipd_depts = conn.execute("SELECT COUNT(*) as c FROM departments WHERE has_ipd = 1").fetchone()["c"]
        doctors_by_dept = conn.execute("""
            SELECT department, COUNT(*) as doc_count 
            FROM doctors 
            GROUP BY department
        """).fetchall()

        return {
            "total_departments": total_depts,
            "opd_departments": opd_depts,
            "ipd_departments": ipd_depts,
            "doctors_by_dept": [dict(r) for r in doctors_by_dept]
        }
    finally:
        conn.close()
