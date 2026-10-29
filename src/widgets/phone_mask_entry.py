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
        self._digits = ""
        self._updating = False

        self.bind("<KeyPress>", self._on_key_press)
        self.bind("<BackSpace>", self._on_backspace)
        self.bind("<Delete>", self._on_delete)
        self.bind("<<Paste>>", self._on_paste)
        self.bind("<Control-v>", self._on_paste)
        self.bind("<Control-V>", self._on_paste)
        self.bind("<Control-a>", self._select_all)
        self.bind("<Control-A>", self._select_all)
        self.var.trace_add("write", self._on_var_write)

    def _update_display(self):
        self._updating = True
        d = self._digits
        if not d:
            formatted = ""
        elif len(d) <= 5:
            formatted = f"+91-{d}"
        else:
            formatted = f"+91-{d[:5]}-{d[5:]}"
        self.var.set(formatted)
        try:
            self.icursor(tk.END)
        except Exception:
            pass
        self._updating = False

    def _on_key_press(self, event):
        # Allow keyboard shortcuts with Ctrl (Ctrl+C, Ctrl+A, Ctrl+X, etc.)
        if event.state & 4:
            if event.keysym in ("x", "X"):
                try:
                    self.clipboard_clear()
                    self.clipboard_append(self.var.get())
                except Exception:
                    pass
                self._digits = ""
                self._update_display()
                return "break"
            return

        # Allow navigation and control keys
        if event.keysym in (
            "Left", "Right", "Up", "Down", "Home", "End",
            "Tab", "Return", "Escape", "Shift_L", "Shift_R",
            "Control_L", "Control_R", "Alt_L", "Alt_R", "Caps_Lock"
        ):
            return

        # Handle printable characters
        if event.char:
            if event.char.isdigit():
                try:
                    if self.selection_present():
                        self._digits = ""
                except Exception:
                    pass
                if len(self._digits) < 10:
                    self._digits += event.char
                    self._update_display()
            # Silently reject non-digits (Poka-Yoke) and prevent default Tkinter insertion
            return "break"

    def _on_backspace(self, event):
        try:
            if self.selection_present():
                self._digits = ""
                self._update_display()
                return "break"
        except Exception:
            pass
        if self._digits:
            self._digits = self._digits[:-1]
            self._update_display()
        return "break"

    def _on_delete(self, event):
        try:
            if self.selection_present():
                self._digits = ""
                self._update_display()
                return "break"
        except Exception:
            pass
        if self._digits:
            self._digits = self._digits[:-1]
            self._update_display()
        return "break"

    def _select_all(self, event=None):
        self.select_range(0, tk.END)
        self.icursor(tk.END)
        return "break"

    def _on_paste(self, event=None):
        try:
            text = self.clipboard_get()
        except Exception:
            return "break"
        self.set(text)
        return "break"

    def _on_var_write(self, *_):
        if self._updating:
            return
        val = self.var.get()
        digits = re.sub(r"\D", "", val)
        if len(digits) == 12 and digits.startswith("91"):
            digits = digits[2:]
        elif digits.startswith("91") and len(digits) > 10:
            digits = digits[2:]
        self._digits = digits[:10]
        self._update_display()

    def get_digits(self):
        return self._digits

    def get(self):
        return self.var.get()

    def set(self, value):
        val = str(value or "").strip()
        digits = re.sub(r"\D", "", val)
        if len(digits) == 12 and digits.startswith("91"):
            digits = digits[2:]
        elif digits.startswith("91") and len(digits) > 10:
            digits = digits[2:]
        self._digits = digits[:10]
        self._update_display()

    def delete(self, first, last=None):
        super().delete(first, last)
        self._digits = ""
        self._update_display()

    def insert(self, index, string):
        self.set(self._digits + str(string))
