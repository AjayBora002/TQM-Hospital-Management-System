"""
purchase_order.py -- Model for Automated Pharmacy Purchase Orders & Stock Replenishment.
Detects low inventory below reorder_level and creates standardized replenishment orders.
When orders are received, automatically restocks pharmacy inventory (Poka-Yoke).
"""
from datetime import datetime
from database.db_manager import get_connection, log_audit
from utils.exception_handler import ValidationError


def _now():
    return datetime.now().isoformat(timespec="seconds")


def create_po(
    medicine_id: int,
    supplier_name: str = "National MedSupply Ltd",
    order_qty: int = 50,
    unit_cost: float = None,
    order_date: str = None,
    performed_by: str = "pharmacist"
):
    """Creates a purchase order for a specific medicine."""
    if not medicine_id:
        raise ValidationError("Medicine ID is required", field="medicine_id")

    supplier_name = str(supplier_name or "").strip()
    if not supplier_name:
        raise ValidationError("Supplier name cannot be empty", field="supplier_name")

    try:
        order_qty = int(order_qty)
        if order_qty <= 0:
            raise ValueError()
    except (TypeError, ValueError):
        raise ValidationError("Order quantity must be an integer >= 1", field="order_qty")

    from utils.validators import is_valid_date
    order_date = str(order_date or _now()[:10]).strip()
    if not is_valid_date(order_date):
        raise ValidationError("Order date must be in YYYY-MM-DD format", field="order_date")

    conn = get_connection()
    try:
        med = conn.execute("SELECT * FROM medicines WHERE medicine_id = ?", (medicine_id,)).fetchone()
        if not med:
            raise ValidationError(f"Medicine #{medicine_id} not found", field="medicine_id")

        if unit_cost is None:
            unit_cost = round(float(med["unit_price"]) * 0.70, 2)
        else:
            try:
                unit_cost = round(float(unit_cost), 2)
                if unit_cost < 0:
                    raise ValueError()
            except (TypeError, ValueError):
                raise ValidationError("Unit cost must be a non-negative number", field="unit_cost")

        total_cost = round(order_qty * unit_cost, 2)

        cur = conn.cursor()
        cur.execute(
            "INSERT INTO purchase_orders (medicine_id, supplier_name, order_qty, unit_cost, total_cost, status, order_date) "
            "VALUES (?,?,?,?,?,'Pending',?)",
            (medicine_id, supplier_name, order_qty, unit_cost, total_cost, order_date)
        )
        po_id = cur.lastrowid
        log_audit(
            conn, "purchase_orders", po_id, "INSERT",
            f"Created PO #{po_id} for {order_qty}x '{med['name']}' from '{supplier_name}' (Total ₹{total_cost})",
            performed_by
        )
        conn.commit()
        return po_id
    finally:
        conn.close()


def generate_auto_pos_for_low_stock(supplier_name="National MedSupply Ltd", performed_by="auto_scheduler"):
    """
    Automated Inventory Replenishment:
    Scans for medicines at or below reorder_level that do not already have an active Pending PO,
    and automatically issues replenishment purchase orders.
    """
    conn = get_connection()
    try:
        # Find low-stock items
        low_meds = conn.execute("""
            SELECT m.* FROM medicines m
            WHERE m.stock_qty <= m.reorder_level
            AND m.medicine_id NOT IN (
                SELECT medicine_id FROM purchase_orders WHERE status = 'Pending'
            )
        """).fetchall()

        created_pos = []
        for m in low_meds:
            med_id = m["medicine_id"]
            reorder = m["reorder_level"]
            # Replenishment batch size = max(5 * reorder_level, 50)
            batch_qty = max(reorder * 5, 50)
            est_cost = round(float(m["unit_price"]) * 0.70, 2)
            total_cost = round(batch_qty * est_cost, 2)
            now_date = _now()[:10]

            cur = conn.cursor()
            cur.execute(
                "INSERT INTO purchase_orders (medicine_id, supplier_name, order_qty, unit_cost, total_cost, status, order_date) "
                "VALUES (?,?,?,?,?,'Pending',?)",
                (med_id, supplier_name, batch_qty, est_cost, total_cost, now_date)
            )
            new_id = cur.lastrowid
            log_audit(
                conn, "purchase_orders", new_id, "INSERT",
                f"Auto-generated replenishment PO #{new_id} for low-stock '{m['name']}' (Stock {m['stock_qty']} <= {m['reorder_level']})",
                performed_by
            )
            created_pos.append(new_id)

        conn.commit()
        return created_pos
    finally:
        conn.close()


def receive_po(po_id: int, received_date: str = None, performed_by: str = "pharmacist"):
    """
    Receives and clears a purchase order upon delivery.
    Poka-Yoke: Automatically increments medicines.stock_qty by the PO order quantity.
    """
    conn = get_connection()
    try:
        po = conn.execute("SELECT * FROM purchase_orders WHERE po_id = ?", (po_id,)).fetchone()
        if not po:
            raise ValidationError(f"Purchase order #{po_id} not found", field="po_id")
        if po["status"] != "Pending":
            raise ValidationError(f"PO #{po_id} is already '{po['status']}'", field="po_id")

        from utils.validators import is_valid_date
        rec_date = str(received_date or _now()[:10]).strip()
        if not is_valid_date(rec_date):
            raise ValidationError("Received date must be in YYYY-MM-DD format", field="received_date")

        if rec_date < po["order_date"]:
            raise ValidationError(
                f"Received date ({rec_date}) cannot be earlier than order date ({po['order_date']})",
                field="received_date"
            )

        qty = po["order_qty"]
        med_id = po["medicine_id"]

        cur = conn.cursor()
        # 1. Update PO status
        cur.execute(
            "UPDATE purchase_orders SET status = 'Received', received_date = ? WHERE po_id = ?",
            (rec_date, po_id)
        )
        # 2. Replenish medicine stock
        cur.execute(
            "UPDATE medicines SET stock_qty = stock_qty + ? WHERE medicine_id = ?",
            (qty, med_id)
        )
        # 3. Audit
        log_audit(
            conn, "purchase_orders", po_id, "UPDATE",
            f"Received PO #{po_id}: Restocked +{qty} units of medicine #{med_id}",
            performed_by
        )
        conn.commit()
        return get_by_id(po_id)
    finally:
        conn.close()


def get_by_id(po_id: int):
    conn = get_connection()
    try:
        row = conn.execute("""
            SELECT po.*, m.name as medicine_name, m.category, m.stock_qty as current_stock, m.reorder_level
            FROM purchase_orders po
            JOIN medicines m ON po.medicine_id = m.medicine_id
            WHERE po.po_id = ?
        """, (po_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def list_all():
    conn = get_connection()
    try:
        rows = conn.execute("""
            SELECT po.*, m.name as medicine_name, m.category, m.stock_qty as current_stock, m.reorder_level
            FROM purchase_orders po
            JOIN medicines m ON po.medicine_id = m.medicine_id
            ORDER BY po.po_id DESC
        """).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()
