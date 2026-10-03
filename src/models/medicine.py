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


def add(name, category, stock_qty, unit_price, reorder_level):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO medicines (name, category, stock_qty, unit_price, reorder_level) VALUES (?,?,?,?,?)",
        (name, category, stock_qty, unit_price, reorder_level)
    )
    new_id = cur.lastrowid
    log_audit(conn, "medicines", new_id, "INSERT", f"Added medicine '{name}'")
    conn.commit()
    conn.close()
    return new_id


def update(medicine_id, name, category, stock_qty, unit_price, reorder_level):
    conn = get_connection()
    conn.execute(
        "UPDATE medicines SET name=?, category=?, stock_qty=?, unit_price=?, reorder_level=? "
        "WHERE medicine_id=?",
        (name, category, stock_qty, unit_price, reorder_level, medicine_id)
    )
    log_audit(conn, "medicines", medicine_id, "UPDATE", "Medicine record updated")
    conn.commit()
    conn.close()


def delete(medicine_id):
    conn = get_connection()
    conn.execute("DELETE FROM medicines WHERE medicine_id=?", (medicine_id,))
    log_audit(conn, "medicines", medicine_id, "DELETE", "Medicine record deleted")
    conn.commit()
    conn.close()
