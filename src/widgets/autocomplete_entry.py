"""
autocomplete_entry.py -- Q07 Feature 3: Auto-Complete
Reusable search box used for patient lookup (Patients tab, Appointments tab,
Billing tab, Room Allocation) so the same existing record is always reused
instead of re-typed -- preventing duplicate / inconsistent entries.
"""
import tkinter as tk
from tkinter import ttk


class AutocompleteEntry(ttk.Entry):
    """Entry that shows a dropdown listbox of matching suggestions as the user types."""

    def __init__(self, master, fetch_candidates, on_select=None, **kwargs):
        self.var = tk.StringVar()
        super().__init__(master, textvariable=self.var, **kwargs)
        self.fetch_candidates = fetch_candidates  # callable(prefix) -> list[str]
        self.on_select = on_select
        self.listbox = None
        self.var.trace_add("write", self._on_change)
        self.bind("<FocusOut>", lambda e: self.after(150, self._hide_list))
        self.bind("<Down>", self._focus_list)

    def _on_change(self, *_):
        text = self.var.get().strip()
        if not text:
            self._hide_list()
            return
        matches = self.fetch_candidates(text)
        if matches:
            self._show_list(matches)
        else:
            self._hide_list()

    def _show_list(self, matches):
        if self.listbox is None:
            self.listbox = tk.Listbox(self.master, height=min(5, len(matches)))
            self.listbox.bind("<<ListboxSelect>>", self._pick)
        self.listbox.delete(0, tk.END)
        for m in matches:
            self.listbox.insert(tk.END, m)
        x = self.winfo_x()
        y = self.winfo_y() + self.winfo_height()
        self.listbox.place(x=x, y=y, width=self.winfo_width())
        self.listbox.lift()

    def _hide_list(self):
        if self.listbox is not None:
            self.listbox.place_forget()

    def _focus_list(self, _event):
        if self.listbox is not None:
            self.listbox.focus_set()
            self.listbox.selection_set(0)

    def _pick(self, _event):
        if not self.listbox.curselection():
            return
        value = self.listbox.get(self.listbox.curselection()[0])
        self.var.set(value)
        self._hide_list()
        if self.on_select:
            self.on_select(value)
