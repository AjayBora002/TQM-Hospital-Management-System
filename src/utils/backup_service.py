"""
backup_service.py -- Automated and on-demand database backup engine.
Provides online atomic sqlite backups with audit trails and retention management.
"""
import os
import sqlite3
from datetime import datetime
import config
from database.db_manager import get_connection, log_audit


def get_backup_dir():
    b_dir = getattr(config, "BACKUP_DIR", os.path.join(config.BASE_DIR, "backups"))
    os.makedirs(b_dir, exist_ok=True)
    return b_dir


def backup_database(performed_by: str = "admin"):
    """
    Performs an atomic online backup of hms.db to the backups folder.
    Logs the backup operation to the audit trail.
    """
    b_dir = get_backup_dir()
    now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"hms_backup_{now_str}.db"
    backup_filepath = os.path.join(b_dir, backup_filename)

    src_conn = get_connection()
    try:
        dest_conn = sqlite3.connect(backup_filepath)
        try:
            # Atomic online sqlite3 backup
            src_conn.backup(dest_conn)
        finally:
            dest_conn.close()

        size_bytes = os.path.getsize(backup_filepath)
        size_kb = round(size_bytes / 1024, 2)

        # Audit log the backup event
        log_audit(
            src_conn,
            "system_backup",
            None,
            "INSERT",
            f"Created database snapshot '{backup_filename}' ({size_kb} KB)",
            performed_by
        )
        src_conn.commit()

        # Clean up old backups (keep most recent 15)
        _prune_backups(b_dir, keep=15)

        return {
            "success": True,
            "filename": backup_filename,
            "filepath": backup_filepath,
            "size_kb": size_kb,
            "created_at": datetime.now().isoformat(timespec="seconds")
        }
    finally:
        src_conn.close()


def list_backups():
    """Returns metadata for all available database backup files."""
    b_dir = get_backup_dir()
    backups = []
    if not os.path.exists(b_dir):
        return backups

    for fname in os.listdir(b_dir):
        if fname.startswith("hms_backup_") and fname.endswith(".db"):
            fpath = os.path.join(b_dir, fname)
            stat = os.stat(fpath)
            backups.append({
                "filename": fname,
                "size_kb": round(stat.st_size / 1024, 2),
                "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds")
            })

    # Sort descending by modified date
    backups.sort(key=lambda x: x["modified_at"], reverse=True)
    return backups


def _prune_backups(b_dir: str, keep: int = 15):
    """Retains the most recent 'keep' backups, deleting older ones."""
    files = [
        os.path.join(b_dir, f) for f in os.listdir(b_dir)
        if f.startswith("hms_backup_") and f.endswith(".db")
    ]
    files.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    for old_file in files[keep:]:
        try:
            os.remove(old_file)
        except OSError:
            pass
