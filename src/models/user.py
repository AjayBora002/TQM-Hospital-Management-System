"""
user.py -- Model for Authentication, Password Security, and Account Lockout.
Supports all 21 modern hospital stakeholder roles.
"""
import hashlib
import time
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

import config
from database.db_manager import get_connection, log_audit
from utils.exception_handler import ValidationError


MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION_SECONDS = 15 * 60  # 15 minutes lockout


def hash_password(password: str) -> str:
    """Returns secure password hash using Werkzeug PBKDF2/scrypt."""
    return generate_password_hash(password)


def verify_password(plain_password: str, stored_hash: str) -> bool:
    """
    Verifies password against stored hash.
    Supports Werkzeug hashes (scrypt / pbkdf2) and legacy SHA-256 fallback.
    """
    if not plain_password or not stored_hash:
        return False

    # Check Werkzeug formatted hashes
    if stored_hash.startswith("scrypt:") or stored_hash.startswith("pbkdf2:"):
        try:
            return check_password_hash(stored_hash, plain_password)
        except Exception:
            return False

    # Legacy SHA-256 fallback
    legacy_hash = hashlib.sha256(plain_password.encode("utf-8")).hexdigest()
    return legacy_hash == stored_hash


def _ensure_attempts_table(conn):
    conn.execute("""
    CREATE TABLE IF NOT EXISTS login_attempts (
        username       TEXT PRIMARY KEY,
        failed_count   INTEGER NOT NULL DEFAULT 0,
        last_failed_at REAL NOT NULL,
        locked_until   REAL NOT NULL DEFAULT 0
    )
    """)


def is_account_locked(username: str):
    """
    Checks if account is locked due to too many failed attempts.
    Returns (is_locked: bool, minutes_remaining: int).
    """
    conn = get_connection()
    try:
        _ensure_attempts_table(conn)
        row = conn.execute(
            "SELECT failed_count, locked_until FROM login_attempts WHERE username = ?",
            (username.strip().lower(),)
        ).fetchone()

        if not row:
            return False, 0

        now = time.time()
        locked_until = row["locked_until"]
        if locked_until > now:
            mins_left = int((locked_until - now) / 60) + 1
            return True, mins_left
        return False, 0
    finally:
        conn.close()


def record_failed_attempt(username: str):
    """
    Records a failed login attempt and locks account for 15 minutes
    if failed attempts reach MAX_FAILED_ATTEMPTS (5).
    """
    u = username.strip().lower()
    now = time.time()
    conn = get_connection()
    try:
        _ensure_attempts_table(conn)
        row = conn.execute("SELECT failed_count FROM login_attempts WHERE username = ?", (u,)).fetchone()
        count = 1
        locked_until = 0.0

        if row:
            count = row["failed_count"] + 1
            if count >= MAX_FAILED_ATTEMPTS:
                locked_until = now + LOCKOUT_DURATION_SECONDS
            conn.execute(
                "UPDATE login_attempts SET failed_count = ?, last_failed_at = ?, locked_until = ? WHERE username = ?",
                (count, now, locked_until, u)
            )
        else:
            conn.execute(
                "INSERT INTO login_attempts (username, failed_count, last_failed_at, locked_until) VALUES (?, ?, ?, ?)",
                (u, count, now, locked_until)
            )
        conn.commit()
        return count >= MAX_FAILED_ATTEMPTS
    finally:
        conn.close()


def clear_failed_attempts(username: str):
    """Clears failed attempts upon successful login."""
    u = username.strip().lower()
    conn = get_connection()
    try:
        _ensure_attempts_table(conn)
        conn.execute("DELETE FROM login_attempts WHERE username = ?", (u,))
        conn.commit()
    finally:
        conn.close()


def authenticate(username: str, password: str):
    """
    Authenticates a user by username and plaintext password.
    Returns user dict on success, None on failure.
    Raises ValidationError if the account is currently locked out.
    """
    if not username or not password:
        return None

    u = username.strip()
    locked, mins_left = is_account_locked(u)
    if locked:
        raise ValidationError(
            f"Account is locked due to 5 consecutive failed login attempts. Please try again in {mins_left} minute(s).",
            field="account_locked"
        )

    conn = get_connection()
    try:
        user_row = conn.execute(
            "SELECT user_id, username, password_hash, role, full_name, email, created_at FROM users "
            "WHERE username = ?",
            (u,)
        ).fetchone()

        if not user_row:
            record_failed_attempt(u)
            return None

        user = dict(user_row)
        stored_hash = user.pop("password_hash")

        if verify_password(password, stored_hash):
            clear_failed_attempts(u)
            return user
        else:
            is_now_locked = record_failed_attempt(u)
            if is_now_locked:
                raise ValidationError(
                    "Account locked due to 5 consecutive failed login attempts. Please try again in 15 minutes.",
                    field="account_locked"
                )
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


def change_password(user_id: int, current_password: str, new_password: str):
    """Allows authenticated user to change their password."""
    if not new_password or len(new_password) < 6:
        raise ValidationError("New password must be at least 6 characters", field="new_password")

    conn = get_connection()
    try:
        user_row = conn.execute("SELECT password_hash, username FROM users WHERE user_id = ?", (user_id,)).fetchone()
        if not user_row:
            raise ValidationError("User not found", field="user_id")

        if not verify_password(current_password, user_row["password_hash"]):
            raise ValidationError("Current password does not match", field="current_password")

        new_hash = hash_password(new_password)
        conn.execute("UPDATE users SET password_hash = ? WHERE user_id = ?", (new_hash, user_id))
        log_audit(conn, "users", user_id, "UPDATE", "User changed their password", user_row["username"])
        conn.commit()
        return True
    finally:
        conn.close()


def admin_reset_password(target_username: str, new_password: str, performed_by: str = "admin"):
    """Allows Administrator to reset password and unlock a user account."""
    if not new_password or len(new_password) < 6:
        raise ValidationError("New password must be at least 6 characters", field="new_password")

    conn = get_connection()
    try:
        user_row = conn.execute("SELECT user_id FROM users WHERE username = ?", (target_username.strip(),)).fetchone()
        if not user_row:
            raise ValidationError(f"User '{target_username}' not found", field="target_username")

        user_id = user_row["user_id"]
        new_hash = hash_password(new_password)
        conn.execute("UPDATE users SET password_hash = ? WHERE user_id = ?", (new_hash, user_id))

        # Clear any lockouts
        _ensure_attempts_table(conn)
        conn.execute("DELETE FROM login_attempts WHERE username = ?", (target_username.strip().lower(),))

        log_audit(conn, "users", user_id, "UPDATE", f"Admin reset password for user '{target_username}'", performed_by)
        conn.commit()
        return True
    finally:
        conn.close()
