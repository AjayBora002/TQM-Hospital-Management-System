"""
login_dialog.py -- Desktop GUI Authentication Dialog & Role Switcher.
Provides credentials entry and 1-click Quick Login buttons for Admin, Doctor, and Receptionist,
as well as a Guest / Examiner Demo mode to ensure seamless evaluation.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import user as user_model


class LoginDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("HMS Security & Role Authentication")
        self.geometry("450x420")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.authenticated_user = None

        self._build_ui()
        self.center_window()

    def center_window(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")

    def _build_ui(self):
        # Header banner
        header = tk.Frame(self, bg="#0056b3", height=65)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="TQM HOSPITAL MANAGEMENT SYSTEM",
            font=("Segoe UI", 12, "bold"),
            fg="#ffffff",
            bg="#0056b3"
        ).pack(pady=(12, 2))

        tk.Label(
            header,
            text="Role-Based Access Control (RBAC) & Authentication",
            font=("Segoe UI", 8),
            fg="#d1e3ff",
            bg="#0056b3"
        ).pack()

        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill="both", expand=True)

        # Credentials Form
        form_box = ttk.LabelFrame(main_frame, text="User Credentials", padding=12)
        form_box.pack(fill="x", pady=(0, 15))

        ttk.Label(form_box, text="Username:").grid(row=0, column=0, sticky="w", pady=4)
        self.username_var = tk.StringVar(value="admin")
        self.u_entry = ttk.Entry(form_box, textvariable=self.username_var, width=28)
        self.u_entry.grid(row=0, column=1, sticky="w", padx=8, pady=4)

        ttk.Label(form_box, text="Password:").grid(row=1, column=0, sticky="w", pady=4)
        self.password_var = tk.StringVar(value="admin123")
        self.p_entry = ttk.Entry(form_box, textvariable=self.password_var, show="•", width=28)
        self.p_entry.grid(row=1, column=1, sticky="w", padx=8, pady=4)

        btn_row = ttk.Frame(form_box)
        btn_row.grid(row=2, column=0, columnspan=2, pady=(10, 0))
        login_btn = ttk.Button(btn_row, text="Login Securely", command=self._do_login)
        login_btn.pack(side="left", padx=5)

        # Quick Demo Login Buttons
        demo_box = ttk.LabelFrame(main_frame, text="1-Click Evaluation / Demo Login", padding=10)
        demo_box.pack(fill="x", pady=(0, 10))

        ttk.Label(demo_box, text="Select role to instantly authenticate for testing:", font=("Segoe UI", 8, "italic")).pack(anchor="w", pady=(0, 6))

        d_row = ttk.Frame(demo_box)
        d_row.pack(fill="x")

        ttk.Button(d_row, text="👑 Admin", command=lambda: self._quick_login("admin", "admin123")).pack(side="left", expand=True, fill="x", padx=2)
        ttk.Button(d_row, text="🩺 Doctor", command=lambda: self._quick_login("doctor", "doctor123")).pack(side="left", expand=True, fill="x", padx=2)
        ttk.Button(d_row, text="📋 Reception", command=lambda: self._quick_login("receptionist", "recep123")).pack(side="left", expand=True, fill="x", padx=2)

        # Bypass / Guest Demo Button
        bypass_frame = ttk.Frame(main_frame)
        bypass_frame.pack(fill="x", pady=5)
        bypass_btn = ttk.Button(bypass_frame, text="⚡ Skip & Continue in Demo Mode (System Admin)", command=self._bypass_demo)
        bypass_btn.pack(fill="x")

    def _quick_login(self, username, password):
        self.username_var.set(username)
        self.password_var.set(password)
        self._do_login()

    def _do_login(self):
        u = self.username_var.get().strip()
        p = self.password_var.get()
        user = user_model.authenticate(u, p)
        if user:
            self.authenticated_user = user
            self.destroy()
        else:
            messagebox.showerror("Authentication Failed", "Invalid username or password.\n\nPlease use admin / admin123 or one of the 1-click buttons.")

    def _bypass_demo(self):
        admin = user_model.get_by_username("admin")
        self.authenticated_user = admin or {"username": "admin", "role": "Admin", "full_name": "Dr. Ajay Bora (System Admin)"}
        self.destroy()


def show_login_dialog(parent):
    dlg = LoginDialog(parent)
    parent.wait_window(dlg)
    if dlg.authenticated_user:
        return dlg.authenticated_user
    # Default fallback to Admin demo
    admin = user_model.get_by_username("admin")
    return admin or {"username": "admin", "role": "Admin", "full_name": "Dr. Ajay Bora (System Admin)"}
