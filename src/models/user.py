"""
user.py -- Model for Authentication and Role-Based Access Control (RBAC).
Supports roles: Admin, Doctor, Receptionist.
"""
import hashlib
from datetime import datetime
import config
from database.db_manager import get_connection, log_audit
from utils.exception_handler import ValidationError


def hash_password(password: str) -> str:
    """Returns SHA-256 hash of plaintext password."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def authenticate(username: str, password: str):
    """
    Authenticates a user by username and plaintext password.
    Returns user dict on success, None on failure.
    """
    if not username or not password:
        return None
    pw_hash = hash_password(password)
    conn = get_connection()
    try:
        user = conn.execute(
            "SELECT user_id, username, role, full_name, email, created_at FROM users "
            "WHERE username = ? AND password_hash = ?",
            (username.strip(), pw_hash)
        ).fetchone()
        if user:
            return dict(user)
        return None
    finally:
        conn.close()


def get_by_id(user_id: int):
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT user_id, username, role, full_name, email, created_at FROM users WHERE user_id = ?",
            (user_id,)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_by_username(username: str):
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT user_id, username, role, full_name, email, created_at FROM users WHERE username = ?",
            (username.strip(),)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def list_users():
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT user_id, username, role, full_name, email, created_at FROM users ORDER BY user_id"
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def create_user(username, password, role, full_name, email=None, performed_by="admin"):
    valid_roles = config.USER_ROLES
    if role not in valid_roles:
        raise ValidationError(f"Role must be one of {valid_roles}", field="role")
    if not username or len(username.strip()) < 3:
        raise ValidationError("Username must be at least 3 characters", field="username")
    if not password or len(password) < 6:
        raise ValidationError("Password must be at least 6 characters", field="password")
    if not full_name or not full_name.strip():
        raise ValidationError("Full name is required", field="full_name")

    conn = get_connection()
    try:
        existing = conn.execute("SELECT 1 FROM users WHERE username = ?", (username.strip(),)).fetchone()
        if existing:
            raise ValidationError(f"Username '{username}' already exists", field="username")

        pw_hash = hash_password(password)
        now_str = datetime.now().isoformat(timespec="seconds")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password_hash, role, full_name, email, created_at) VALUES (?,?,?,?,?,?)",
            (username.strip(), pw_hash, role, full_name.strip(), (email or "").strip(), now_str)
        )
        user_id = cursor.lastrowid
        log_audit(conn, "users", user_id, "INSERT", f"Created user '{username}' with role '{role}'", performed_by)
        conn.commit()
        return user_id
    finally:
        conn.close()
