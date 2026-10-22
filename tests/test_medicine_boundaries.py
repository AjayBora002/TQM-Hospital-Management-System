import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from utils.validators import validate_medicine_payload
from utils.exception_handler import ValidationError
from database.db_manager import init_db
from models import medicine as medicine_model


class TestMedicineBoundaries(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def test_valid_medicine_payload(self):
        payload = {
            "name": "Ibuprofen 400mg",
            "category": "Tablet",
            "stock_qty": 100,
            "unit_price": 4.50,
            "reorder_level": 20,
            "expiry_date": "2028-05-30"
        }
        self.assertTrue(validate_medicine_payload(payload))

    def test_short_name_rejected(self):
        payload = {
            "name": "M",
            "category": "Tablet",
            "stock_qty": 50,
            "unit_price": 5.0,
            "reorder_level": 10
        }
        with self.assertRaises(ValidationError) as ctx:
            validate_medicine_payload(payload)
        self.assertEqual(ctx.exception.field, "name")

    def test_invalid_category_rejected(self):
        payload = {
            "name": "Vitamin C",
            "category": "Snack",
            "stock_qty": 50,
            "unit_price": 5.0,
            "reorder_level": 10
        }
        with self.assertRaises(ValidationError) as ctx:
            validate_medicine_payload(payload)
        self.assertEqual(ctx.exception.field, "category")

    def test_negative_stock_rejected(self):
        payload = {
            "name": "Aspirin 75mg",
            "category": "Tablet",
            "stock_qty": -10,
            "unit_price": 2.0,
            "reorder_level": 5
        }
        with self.assertRaises(ValidationError) as ctx:
            validate_medicine_payload(payload)
        self.assertEqual(ctx.exception.field, "stock_qty")

    def test_negative_unit_price_rejected(self):
        payload = {
            "name": "Aspirin 75mg",
            "category": "Tablet",
            "stock_qty": 20,
            "unit_price": -2.0,
            "reorder_level": 5
        }
        with self.assertRaises(ValidationError) as ctx:
            validate_medicine_payload(payload)
        self.assertEqual(ctx.exception.field, "unit_price")

    def test_negative_reorder_level_rejected(self):
        payload = {
            "name": "Aspirin 75mg",
            "category": "Tablet",
            "stock_qty": 20,
            "unit_price": 2.0,
            "reorder_level": -5
        }
        with self.assertRaises(ValidationError) as ctx:
            validate_medicine_payload(payload)
        self.assertEqual(ctx.exception.field, "reorder_level")

    def test_invalid_expiry_format_rejected(self):
        payload = {
            "name": "Paracetamol 500mg",
            "category": "Tablet",
            "stock_qty": 20,
            "unit_price": 2.0,
            "reorder_level": 5,
            "expiry_date": "31-12-2028"
        }
        with self.assertRaises(ValidationError) as ctx:
            validate_medicine_payload(payload)
        self.assertEqual(ctx.exception.field, "expiry_date")

    def test_model_add_blocks_negative_values(self):
        with self.assertRaises(ValidationError):
            medicine_model.add("Negative Stock Med", "Tablet", -5, 10.0, 5)

        with self.assertRaises(ValidationError):
            medicine_model.add("Negative Price Med", "Tablet", 10, -10.0, 5)


if __name__ == "__main__":
    unittest.main()
