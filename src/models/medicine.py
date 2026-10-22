"""medicine.py -- Data-access functions for the medicines table (Pharmacy/Inventory module)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_manager import get_connection, log_audit  # noqa: E402


def list_all():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM medicines ORDER BY name").fetchall()
    conn.close()
    return rows


def low_stock():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM medicines WHERE stock_qty <= reorder_level").fetchall()
    conn.close()
    return rows


def get_by_id(medicine_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM medicines WHERE medicine_id=?", (medicine_id,)).fetchone()
    conn.close()
    return row


def is_expired(expiry_date_str: str) -> bool:
    """Returns True if expiry_date_str is prior to today (YYYY-MM-DD)."""
    if not expiry_date_str:
        return False
    from datetime import date
    try:
        today_str = date.today().isoformat()
        return expiry_date_str.strip() < today_str
    except Exception:
        return False


def expired_medicines():
    """Returns all medicine rows whose expiry date is strictly earlier than today."""
    conn = get_connection()
    from datetime import date
    today_str = date.today().isoformat()
    rows = conn.execute("SELECT * FROM medicines WHERE expiry_date < ? ORDER BY expiry_date", (today_str,)).fetchall()
    conn.close()
    return rows


def add(name, category, stock_qty, unit_price, reorder_level, batch_no="BAT-2026-01", expiry_date="2027-12-31"):
    from utils.validators import validate_medicine_payload
    validate_medicine_payload({
        "name": name,
        "category": category,
        "stock_qty": stock_qty,
        "unit_price": unit_price,
        "reorder_level": reorder_level,
        "expiry_date": expiry_date
    })
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO medicines (name, category, stock_qty, unit_price, reorder_level, batch_no, expiry_date) VALUES (?,?,?,?,?,?,?)",
        (str(name).strip(), category, int(stock_qty), float(unit_price), int(reorder_level), batch_no or "BAT-2026-01", expiry_date or "2027-12-31")
    )
    new_id = cur.lastrowid
    log_audit(conn, "medicines", new_id, "INSERT", f"Added medicine '{name}' (Batch: {batch_no}, Expiry: {expiry_date})")
    conn.commit()
    conn.close()
    return new_id


def update(medicine_id, name, category, stock_qty, unit_price, reorder_level, batch_no="BAT-2026-01", expiry_date="2027-12-31"):
    from utils.validators import validate_medicine_payload
    validate_medicine_payload({
        "name": name,
        "category": category,
        "stock_qty": stock_qty,
        "unit_price": unit_price,
        "reorder_level": reorder_level,
        "expiry_date": expiry_date
    })
    conn = get_connection()
    conn.execute(
        "UPDATE medicines SET name=?, category=?, stock_qty=?, unit_price=?, reorder_level=?, batch_no=?, expiry_date=? "
        "WHERE medicine_id=?",
        (str(name).strip(), category, int(stock_qty), float(unit_price), int(reorder_level), batch_no or "BAT-2026-01", expiry_date or "2027-12-31", medicine_id)
    )
    log_audit(conn, "medicines", medicine_id, "UPDATE", f"Medicine updated (Batch: {batch_no}, Expiry: {expiry_date})")
    conn.commit()
    conn.close()


def delete(medicine_id):
    conn = get_connection()
    conn.execute("DELETE FROM medicines WHERE medicine_id=?", (medicine_id,))
    log_audit(conn, "medicines", medicine_id, "DELETE", "Medicine record deleted")
    conn.commit()
    conn.close()

