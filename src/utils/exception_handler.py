"""
exception_handler.py -- Centralized error handling and safety decorators for HMS.
Captures unexpected application errors, logs them to TQM error logs, and returns
safe standardized responses to callers to prevent application crashes.
"""
import functools
import traceback
from typing import Callable, Any
from .logging_service import log_error_event


class TQMException(Exception):
    """Base exception for all domain-level quality and data exceptions."""
    def __init__(self, message: str, code: str = "GENERIC_ERROR", field: str = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.field = field


class ValidationError(TQMException):
    """Raised when data input fails Q07 validation rules."""
    def __init__(self, message: str, field: str = None):
        super().__init__(message, code="VALIDATION_ERROR", field=field)


class DatabaseError(TQMException):
    """Raised when a database query or constraint fails."""
    def __init__(self, message: str):
        super().__init__(message, code="DATABASE_ERROR")


def safe_operation(module_name: str = "HMS"):
    """
    Decorator for operations that should gracefully handle exceptions.
    Logs error to TQM CSV and returns a standard error dictionary instead of crashing.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except ValidationError as ve:
                err_id = log_error_event(
                    module=module_name,
                    error_type="ValidationError",
                    severity="MEDIUM",
                    message=f"Field '{ve.field}': {ve.message}",
                    action=func.__name__
                )
                return {"success": False, "error": ve.message, "error_id": err_id, "field": ve.field}
            except Exception as ex:
                tb = traceback.format_exc()
                err_id = log_error_event(
                    module=module_name,
                    error_type=type(ex).__name__,
                    severity="HIGH",
                    message=f"{str(ex)} | {tb[-150:]}",
                    action=func.__name__
                )
                return {"success": False, "error": f"An error occurred ({err_id}): {str(ex)}", "error_id": err_id}
        return wrapper
    return decorator
