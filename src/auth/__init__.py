"""
auth package -- Authentication, Sessions, and Role-Based Access Control (RBAC)
"""
from .permissions import (
    ALL_ROLES,
    ROLE_PERMISSIONS,
    has_permission,
    get_user_permissions,
    require_permission,
    SESSION_IDLE_TIMEOUT_SECONDS
)

__all__ = [
    "ALL_ROLES",
    "ROLE_PERMISSIONS",
    "has_permission",
    "get_user_permissions",
    "require_permission",
    "SESSION_IDLE_TIMEOUT_SECONDS"
]

