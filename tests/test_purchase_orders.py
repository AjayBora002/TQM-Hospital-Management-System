"""
test_purchase_orders.py -- Unit tests for Pharmacy Automated Purchase Orders & Stock Replenishment.
"""
import unittest
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, "src"))

import config
config.DB_PATH = os.path.join(BASE_DIR, "tests", "test_po.db")

from database.db_manager import init_db
from models import medicine as medicine_model
from models import purchase_order as po_model
from utils.exception_handler import ValidationError


class TestPurchaseOrders(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if os.path.exists(config.DB_PATH):
            try:
                os.remove(config.DB_PATH)
            except Exception:
                pass
        init_db()
        cls.med_id = medicine_model.add("Metformin 500mg", "Tablet", 8, 4.0, 20, batch_no="BAT-MET-01", expiry_date="2028-12-31")

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(config.DB_PATH):
            try:
                os.remove(config.DB_PATH)
            except Exception:
                pass

    def test_01_auto_generate_replenishment_orders(self):
        # Med stock (8) is <= reorder_level (20)
        created_ids = po_model.generate_auto_pos_for_low_stock()
        self.assertGreaterEqual(len(created_ids), 1)

        po = po_model.get_by_id(created_ids[0])
        self.assertEqual(po["status"], "Pending")
        self.assertGreaterEqual(po["order_qty"], 50)
        self.assertGreater(po["total_cost"], 0.0)

    def test_02_receive_po_restocks_inventory(self):
        # Create explicit PO
        po_id = po_model.create_po(self.med_id, supplier_name="Apex Healthcare Ltd", order_qty=100, unit_cost=2.80)
        po_before = po_model.get_by_id(po_id)
        stock_before = po_before["current_stock"]

        # Receive PO
        po_after = po_model.receive_po(po_id)
        self.assertEqual(po_after["status"], "Received")

        # Verify stock incremented by exactly 100
        med_after = medicine_model.get_by_id(self.med_id)
        self.assertEqual(med_after["stock_qty"], stock_before + 100)

    def test_03_receive_already_received_po_fails(self):
        po_id = po_model.create_po(self.med_id, order_qty=25)
        po_model.receive_po(po_id)
        with self.assertRaises(ValidationError):
            po_model.receive_po(po_id)


if __name__ == "__main__":
    unittest.main()
