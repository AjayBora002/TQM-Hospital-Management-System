import unittest
import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from utils.exception_handler import ValidationError
from database.db_manager import init_db
from models import medicine as medicine_model
from models import purchase_order as po_model


class TestPurchaseBoundaries(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.med_id = medicine_model.add(
            name=f"Amoxicillin-{datetime.now().strftime('%f')[:4]}",
            category="Capsule",
            stock_qty=15,
            unit_price=12.50,
            reorder_level=20,
            batch_no="AMX-TEST-01",
            expiry_date="2027-12-31"
        )

    def test_empty_supplier_name_rejected(self):
        with self.assertRaises(ValidationError) as ctx:
            po_model.create_po(self.med_id, supplier_name="   ", order_qty=50)
        self.assertEqual(ctx.exception.field, "supplier_name")

    def test_negative_unit_cost_rejected(self):
        with self.assertRaises(ValidationError) as ctx:
            po_model.create_po(self.med_id, supplier_name="Pharma Corp", order_qty=50, unit_cost=-5.0)
        self.assertEqual(ctx.exception.field, "unit_cost")

    def test_invalid_order_date_format_rejected(self):
        with self.assertRaises(ValidationError) as ctx:
            po_model.create_po(self.med_id, supplier_name="Pharma Corp", order_qty=50, order_date="24-10-2026")
        self.assertEqual(ctx.exception.field, "order_date")

    def test_received_date_earlier_than_order_date_rejected(self):
        # PO ordered yesterday
        order_date = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
        po_id = po_model.create_po(
            self.med_id,
            supplier_name="Valid Supplier",
            order_qty=20,
            unit_cost=8.0,
            order_date=order_date
        )

        # Receive 3 days ago (before order date) must fail
        earlier_date = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
        with self.assertRaises(ValidationError) as ctx:
            po_model.receive_po(po_id, received_date=earlier_date)
        self.assertEqual(ctx.exception.field, "received_date")

        # Invalid date format on receive
        with self.assertRaises(ValidationError) as ctx2:
            po_model.receive_po(po_id, received_date="not-a-date")
        self.assertEqual(ctx2.exception.field, "received_date")

        # Valid receive on or after order date succeeds
        rec_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        res = po_model.receive_po(po_id, received_date=rec_date)
        self.assertEqual(res["status"], "Received")
        self.assertEqual(res["received_date"], rec_date)


if __name__ == "__main__":
    unittest.main()
