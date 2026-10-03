"""
phone_mask_entry.py -- Q07 Feature 1: Input Masking
Reusable across Patients, Doctors and Staff forms so phone numbers are
always stored in exactly one valid shape: +91-XXXXX-XXXXX.
"""
import tkinter as tk
from tkinter import ttk
import re


class PhoneMaskEntry(ttk.Entry):
    """Entry widget that auto-formats digits into +91-XXXXX-XXXXX as the user types.
    Poka-Yoke: non-digit characters are silently rejected; length capped at 10 digits."""

    def __init__(self, master, **kwargs):
        self.var = tk.StringVar()
        super().__init__(master, textvariable=self.var, **kwargs)
        self.var.trace_add("write", self._format)
        self._updating = False

    def _format(self, *_):
        if self._updating:
            return
        self._updating = True
        digits = re.sub(r"\D", "", self.var.get())[:10]
        formatted = digits
        if len(digits) > 5:
            formatted = f"{digits[:5]}-{digits[5:]}"
        if len(digits) > 0:
            formatted = f"+91-{formatted}"
        self.var.set(formatted)
        self.icursor(tk.END)
        self._updating = False

    def get_digits(self):
        return re.sub(r"\D", "", self.var.get())

    def get(self):
        return self.var.get()

    def set(self, value):
        self._updating = False
        self.var.set(value)
