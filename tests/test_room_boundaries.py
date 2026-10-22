import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from utils.validators import validate_room_payload
from utils.exception_handler import ValidationError
from database.db_manager import init_db
from models import room as room_model


class TestRoomBoundaries(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
    def test_valid_room_payload(self):
        payload = {
            "room_number": "401A",
            "room_type": "ICU",
            "status": "Available",
            "rate_per_day": 3500.0
        }
        self.assertTrue(validate_room_payload(payload))

    def test_empty_room_number_rejected(self):
        payload = {
            "room_number": "   ",
            "room_type": "ICU",
            "status": "Available",
            "rate_per_day": 3500.0
        }
        with self.assertRaises(ValidationError) as ctx:
            validate_room_payload(payload)
        self.assertEqual(ctx.exception.field, "room_number")

    def test_invalid_room_type_rejected(self):
        payload = {
            "room_number": "402",
            "room_type": "FiveStarSuite",
            "status": "Available",
            "rate_per_day": 1000.0
        }
        with self.assertRaises(ValidationError) as ctx:
            validate_room_payload(payload)
        self.assertEqual(ctx.exception.field, "room_type")

    def test_invalid_room_status_rejected(self):
        payload = {
            "room_number": "403",
            "room_type": "Private",
            "status": "Broken",
            "rate_per_day": 1200.0
        }
        with self.assertRaises(ValidationError) as ctx:
            validate_room_payload(payload)
        self.assertEqual(ctx.exception.field, "status")

    def test_negative_rate_rejected(self):
        payload = {
            "room_number": "404",
            "room_type": "General Ward",
            "status": "Available",
            "rate_per_day": -150.0
        }
        with self.assertRaises(ValidationError) as ctx:
            validate_room_payload(payload)
        self.assertEqual(ctx.exception.field, "rate_per_day")

    def test_model_level_rejection_negative_rate(self):
        with self.assertRaises(ValidationError):
            room_model.add("405", "General Ward", "Available", -200)

    def test_model_level_invalid_status_rejection(self):
        r_id = room_model.add("406", "General Ward", "Available", 500)
        with self.assertRaises(ValidationError):
            room_model.set_status(r_id, "Demolished")


if __name__ == "__main__":
    unittest.main()
