"""
inventory_api.py -- REST API Blueprint for Central Stores & Ward Consumables Management.
"""
from flask import Blueprint, request, jsonify, session
from database.db_manager import get_connection, log_audit
from auth.permissions import require_permission
from utils.exception_handler import ValidationError
from datetime import datetime

inventory_bp = Blueprint("inventory", __name__)


@inventory_bp.route("/inventory/items", methods=["GET"])
@require_permission("pharmacy", "view")
def list_inventory_items():
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM inventory_items ORDER BY item_name ASC").fetchall()
        return jsonify([dict(r) for r in rows]), 200
    finally:
        conn.close()


@inventory_bp.route("/inventory/items", methods=["POST"])
@require_permission("pharmacy", "create")
def add_inventory_item():
    data = request.get_json() or {}
    item_code = data.get("item_code", "").strip()
    item_name = data.get("item_name", "").strip()
    category = data.get("category", "Consumable")
    unit = data.get("unit", "Pieces")
    stock_qty = int(data.get("stock_qty", 0))
    reorder_level = int(data.get("reorder_level", 20))
    unit_cost = float(data.get("unit_cost", 0.0))
    location = data.get("location", "Central Store Rack A")
    user = session.get("username", "store_mgr")

    if not item_code or not item_name:
        raise ValidationError("Item code and name are required", field="item_name")
    if stock_qty < 0:
        raise ValidationError("Stock quantity cannot be negative", field="stock_qty")

    today_str = datetime.now().strftime("%Y-%m-%d")
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO inventory_items (item_code, item_name, category, unit, stock_qty, reorder_level, unit_cost, location, last_restocked)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (item_code, item_name, category, unit, stock_qty, reorder_level, unit_cost, location, today_str))
        item_id = cursor.lastrowid
        log_audit(conn, "inventory_items", item_id, "INSERT", f"Added item '{item_name}' ({item_code})", user)
        conn.commit()
        return jsonify({"message": "Inventory item registered", "item_id": item_id}), 201
    finally:
        conn.close()


@inventory_bp.route("/inventory/issue-ward", methods=["POST"])
@require_permission("pharmacy", "edit")
def issue_consumables_to_ward():
    data = request.get_json() or {}
    item_id = data.get("item_id")
    ward_id = data.get("ward_id")
    qty = int(data.get("qty", 1))
    notes = data.get("notes", "")
    user = session.get("username", "store_mgr")

    if not item_id or not ward_id:
        raise ValidationError("Item and target ward are required", field="item_id")
    if qty <= 0:
        raise ValidationError("Issue quantity must be greater than zero", field="qty")

    today_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    try:
        item = conn.execute("SELECT * FROM inventory_items WHERE item_id = ?", (item_id,)).fetchone()
        if not item:
            return jsonify({"error": "Item not found"}), 404

        if item["stock_qty"] < qty:
            raise ValidationError(f"Insufficient stock: requested {qty}, but available stock is {item['stock_qty']}", field="qty")

        # Deduct stock
        new_qty = item["stock_qty"] - qty
        conn.execute("UPDATE inventory_items SET stock_qty = ? WHERE item_id = ?", (new_qty, item_id))

        # Record transaction
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO inventory_transactions (item_id, txn_type, qty, ward_id, reference_no, performed_by, notes, txn_date)
            VALUES (?, 'ISSUE_TO_WARD', ?, ?, ?, ?, ?, ?)
        """, (item_id, qty, ward_id, f"ISSUE-WARD-{ward_id}", user, notes, today_str))
        txn_id = cursor.lastrowid

        log_audit(conn, "inventory_items", item_id, "UPDATE", f"Issued {qty} {item['unit']} of {item['item_name']} to Ward {ward_id}", user)
        conn.commit()
        return jsonify({"message": f"Issued {qty} unit(s) to ward successfully", "remaining_stock": new_qty, "txn_id": txn_id}), 200
    finally:
        conn.close()
