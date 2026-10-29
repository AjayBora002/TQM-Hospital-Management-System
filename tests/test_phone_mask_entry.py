"""
test_phone_mask_entry.py -- Unit tests for PhoneMaskEntry widget (Desktop Tkinter)
Validates Q07 Input Masking, Poka-Yoke non-digit rejection, and Backspace handling.
"""
import unittest
import os
import sys
import tkinter as tk

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from widgets.phone_mask_entry import PhoneMaskEntry


class DummyKeyEvent:
    def __init__(self, char="", keysym="", state=0):
        self.char = char
        self.keysym = keysym
        self.state = state


class TestPhoneMaskEntry(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = tk.Tk()
        cls.root.withdraw()

    @classmethod
    def tearDownClass(cls):
        try:
            cls.root.destroy()
        except Exception:
            pass

    def setUp(self):
        self.entry = PhoneMaskEntry(self.root)

    def test_initial_state(self):
        self.assertEqual(self.entry.get(), "")
        self.assertEqual(self.entry.get_digits(), "")

    def test_typing_digits(self):
        for digit in "9876543210":
            res = self.entry._on_key_press(DummyKeyEvent(char=digit, keysym=digit))
            self.assertEqual(res, "break")
        self.assertEqual(self.entry.get(), "+91-98765-43210")
        self.assertEqual(self.entry.get_digits(), "9876543210")

    def test_typing_capped_at_10_digits(self):
        for digit in "9876543210999":
            self.entry._on_key_press(DummyKeyEvent(char=digit, keysym=digit))
        self.assertEqual(self.entry.get(), "+91-98765-43210")
        self.assertEqual(self.entry.get_digits(), "9876543210")

    def test_reject_letters_and_symbols(self):
        self.entry.set("98765")
        for bad_char in ["a", "Z", "!", "@", "#", " ", "-", "+"]:
            res = self.entry._on_key_press(DummyKeyEvent(char=bad_char, keysym=bad_char))
            self.assertEqual(res, "break")
        self.assertEqual(self.entry.get(), "+91-98765")
        self.assertEqual(self.entry.get_digits(), "98765")

    def test_backspace_removes_digit(self):
        for digit in "987654":
            self.entry._on_key_press(DummyKeyEvent(char=digit, keysym=digit))
        self.assertEqual(self.entry.get(), "+91-98765-4")
        self.assertEqual(self.entry.get_digits(), "987654")

        # 1st backspace removes '4'
        res = self.entry._on_backspace(DummyKeyEvent(keysym="BackSpace"))
        self.assertEqual(res, "break")
        self.assertEqual(self.entry.get(), "+91-98765")
        self.assertEqual(self.entry.get_digits(), "98765")

        # 2nd backspace removes '5'
        self.entry._on_backspace(DummyKeyEvent(keysym="BackSpace"))
        self.assertEqual(self.entry.get(), "+91-9876")
        self.assertEqual(self.entry.get_digits(), "9876")

    def test_backspace_to_empty(self):
        self.entry.set("9")
        self.assertEqual(self.entry.get(), "+91-9")
        self.entry._on_backspace(DummyKeyEvent(keysym="BackSpace"))
        self.assertEqual(self.entry.get(), "")
        self.assertEqual(self.entry.get_digits(), "")

        # Extra backspace on empty does not crash
        self.entry._on_backspace(DummyKeyEvent(keysym="BackSpace"))
        self.assertEqual(self.entry.get(), "")
        self.assertEqual(self.entry.get_digits(), "")

    def test_set_and_clear(self):
        self.entry.set("+91-91234-56789")
        self.assertEqual(self.entry.get(), "+91-91234-56789")
        self.assertEqual(self.entry.get_digits(), "9123456789")

        self.entry.set("")
        self.assertEqual(self.entry.get(), "")
        self.assertEqual(self.entry.get_digits(), "")

    def test_set_raw_digits(self):
        self.entry.set("9876543210")
        self.assertEqual(self.entry.get(), "+91-98765-43210")
        self.assertEqual(self.entry.get_digits(), "9876543210")


if __name__ == "__main__":
    unittest.main()
