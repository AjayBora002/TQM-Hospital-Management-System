"""
logging_service.py -- Centralized TQM Logging and Auditing Service
Writes quality evidence, audit events, defects, and error records
both to SQLite database and persistent TQM CSV files for compliance verification.
"""
import os
import csv
from datetime import datetime

# Resolve base paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TQM_DATA_DIR = os.path.join(BASE_DIR, "TQM", "data")
AUDIT_LOG_CSV = os.path.join(TQM_DATA_DIR, "audit_logs.csv")
ERROR_LOG_CSV = os.path.join(TQM_DATA_DIR, "error_logs.csv")
CHECKSHEET_CSV = os.path.join(TQM_DATA_DIR, "checksheet.csv")
QUALITY_METRICS_CSV = os.path.join(TQM_DATA_DIR, "quality_metrics.csv")
PROCESS_METRICS_CSV = os.path.join(TQM_DATA_DIR, "process_metrics.csv")


def _ensure_csv_headers():
    os.makedirs(TQM_DATA_DIR, exist_ok=True)
    
    files_headers = [
        (AUDIT_LOG_CSV, ["timestamp", "user_id", "role", "module", "action", "record_id", "result", "description"]),
        (ERROR_LOG_CSV, ["timestamp", "error_id", "module", "error_type", "severity", "user_id", "action", "status", "message_reference"]),
        (CHECKSHEET_CSV, ["date", "module", "error_category", "count", "remarks"]),
        (QUALITY_METRICS_CSV, ["date", "metric_id", "metric_name", "value", "target", "status", "evidence_reference"]),
        (PROCESS_METRICS_CSV, ["timestamp", "phase", "metric", "expected", "actual", "variance", "status"])
    ]
    
    for path, headers in files_headers:
        if not os.path.exists(path) or os.path.getsize(path) == 0:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(headers)


def _get_path(env_var, default_path):
    return os.environ.get(env_var, default_path)


def is_test_environment():
    if os.environ.get("HMS_TEST_MODE") == "1":
        return True
    try:
        import config
        if "test" in os.path.basename(config.DB_PATH).lower():
            return True
    except Exception:
        pass
    return False


_ensure_csv_headers()


def log_audit_event(module, action, record_id="", result="SUCCESS", description="", user_id="front_desk_user", role="Staff"):
    """Logs an operational data modification to TQM audit_logs.csv."""
    if is_test_environment() and "HMS_AUDIT_LOG_CSV" not in os.environ:
        return
    _ensure_csv_headers()
    target_csv = _get_path("HMS_AUDIT_LOG_CSV", AUDIT_LOG_CSV)
    ts = datetime.now().isoformat(timespec="seconds")
    try:
        with open(target_csv, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([ts, user_id, role, module, action, str(record_id), result, description])
    except Exception as e:
        print(f"[LoggingService] Failed to append to audit CSV: {e}")


def log_error_event(module, error_type, severity="HIGH", message="", user_id="front_desk_user", action="Execute"):
    """Logs an operational error or exception to TQM error_logs.csv."""
    err_id = f"ERR-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    if is_test_environment() and "HMS_ERROR_LOG_CSV" not in os.environ:
        return err_id
    _ensure_csv_headers()
    target_csv = _get_path("HMS_ERROR_LOG_CSV", ERROR_LOG_CSV)
    ts = datetime.now().isoformat(timespec="seconds")
    clean_msg = str(message).replace("\n", " ").replace(",", ";")[:250]
    try:
        with open(target_csv, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([ts, err_id, module, error_type, severity, user_id, action, "Logged", clean_msg])
    except Exception as e:
        print(f"[LoggingService] Failed to append to error CSV: {e}")
    return err_id


def log_defect(module, error_category, count=1, remarks=""):
    """Logs defect checksheet count for Pareto chart & SQC tracking."""
    if is_test_environment() and "HMS_CHECKSHEET_CSV" not in os.environ:
        return
    _ensure_csv_headers()
    target_csv = _get_path("HMS_CHECKSHEET_CSV", CHECKSHEET_CSV)
    date_str = datetime.now().strftime("%Y-%m-%d")
    try:
        with open(target_csv, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([date_str, module, error_category, count, remarks])
    except Exception as e:
        print(f"[LoggingService] Failed to append to checksheet CSV: {e}")


def log_metric(metric_id, metric_name, value, target, status="Compliant", evidence="System Audit"):
    """Logs quality assurance metric tracking record."""
    if is_test_environment() and "HMS_QUALITY_METRICS_CSV" not in os.environ:
        return
    _ensure_csv_headers()
    target_csv = _get_path("HMS_QUALITY_METRICS_CSV", QUALITY_METRICS_CSV)
    date_str = datetime.now().strftime("%Y-%m-%d")
    try:
        with open(target_csv, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([date_str, metric_id, metric_name, value, target, status, evidence])
    except Exception as e:
        print(f"[LoggingService] Failed to append to quality metrics CSV: {e}")
