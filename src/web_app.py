"""
web_app.py -- Local Web Application for Hospital Management System (HMS)
BBAT104 Course Project | Quality Goal: Q07 - Improve Data Accuracy
Student: Ajay Bora | Branch: CSE | Section: B

Serves an interactive modern web UI on http://127.0.0.1:5000 with:
- All 10 System Modules (Dashboard, Patients, Doctors, Appointments, Rooms, Staff, Pharmacy, Billing, Audit Log, Defect Checksheet)
- All 5 Q07 TQM Features:
    1. Input Masking (Phone +91-XXXXX-XXXXX)
    2. Dropdown Lists (Enforced fixed sets)
    3. Auto-Complete (Instant suggestions)
    4. Confirmation Modals (Interactive safeguards)
    5. Audit Logs (Immutable action history)
"""
import os
import sys
import json
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string

# Ensure src directory is in Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (
    APP_TITLE, GENDERS, BLOOD_GROUPS, DEPARTMENTS, APPT_STATUS,
    ROOM_TYPES, ROOM_STATUS, STAFF_ROLES, SHIFTS, PAYMENT_METHODS,
    PAYMENT_STATUS, MEDICINE_CATEGORIES, DEFECT_CATEGORIES,
    DEFECT_SEVERITY, DEFECT_STATUS, DB_PATH
)
from database.db_manager import init_db, get_connection, log_audit
import models.patient as patient_model
import models.doctor as doctor_model
import models.appointment as appointment_model
import models.room as room_model
import models.staff as staff_model
import models.medicine as medicine_model
import models.bill as bill_model
import models.audit as audit_model

app = Flask(__name__)
init_db()

# --- Helper to convert sqlite3.Row to dict ---
def row_to_dict(row):
    return dict(row) if row else None

def rows_to_list(rows):
    return [dict(r) for r in rows]

# --- HTML TEMPLATE (Single Page Application with Modern Responsive Healthcare UI) ---
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        :root {
            --primary: #0284c7;
            --primary-dark: #0369a1;
            --primary-light: #e0f2fe;
            --accent: #0d9488;
            --bg-main: #f8fafc;
            --card-bg: #ffffff;
            --text-dark: #0f172a;
            --text-muted: #64748b;
            --border-color: #e2e8f0;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --shadow-sm: 0 1px 3px rgba(0,0,0,0.06);
            --shadow-md: 0 4px 6px -1px rgba(0,0,0,0.08), 0 2px 4px -2px rgba(0,0,0,0.04);
            --shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.08), 0 4px 6px -4px rgba(0,0,0,0.03);
            --radius: 10px;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        }

        body {
            background-color: var(--bg-main);
            color: var(--text-dark);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }

        /* Top Header */
        header {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: #ffffff;
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: var(--shadow-md);
        }

        .header-title {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .brand-icon {
            background: #0284c7;
            color: #ffffff;
            width: 40px;
            height: 40px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
            font-size: 20px;
        }

        .brand-text h1 {
            font-size: 1.25rem;
            font-weight: 700;
            letter-spacing: -0.02em;
        }

        .brand-text p {
            font-size: 0.8rem;
            color: #94a3b8;
        }

        .header-badges {
            display: flex;
            gap: 10px;
        }

        .badge-tqm {
            background: rgba(13, 148, 136, 0.25);
            color: #2dd4bf;
            border: 1px solid rgba(45, 212, 191, 0.4);
            padding: 4px 12px;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
        }

        .badge-live {
            background: rgba(16, 185, 129, 0.2);
            color: #34d399;
            border: 1px solid rgba(52, 211, 153, 0.4);
            padding: 4px 12px;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .live-dot {
            width: 8px;
            height: 8px;
            background-color: #34d399;
            border-radius: 50%;
            display: inline-block;
            animation: pulse 1.5s infinite;
        }

        @keyframes pulse {
            0% { transform: scale(0.95); opacity: 0.7; }
            50% { transform: scale(1.2); opacity: 1; }
            100% { transform: scale(0.95); opacity: 0.7; }
        }

        /* Navigation Bar (Tabs) */
        nav {
            background: #ffffff;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            overflow-x: auto;
            padding: 0 1.5rem;
            box-shadow: var(--shadow-sm);
        }

        .nav-tab {
            padding: 1rem 1.25rem;
            font-size: 0.9rem;
            font-weight: 600;
            color: var(--text-muted);
            border: none;
            background: none;
            cursor: pointer;
            border-bottom: 3px solid transparent;
            transition: all 0.2s ease;
            white-space: nowrap;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .nav-tab:hover {
            color: var(--primary);
            background: #f1f5f9;
        }

        .nav-tab.active {
            color: var(--primary);
            border-bottom-color: var(--primary);
            background: var(--primary-light);
        }

        /* Main Container */
        main {
            flex: 1;
            padding: 1.5rem 2rem;
            max-width: 1400px;
            margin: 0 auto;
            width: 100%;
        }

        /* Tab Content Panels */
        .tab-panel {
            display: none;
            animation: fadeIn 0.2s ease-in-out;
        }

        .tab-panel.active {
            display: block;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(4px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* Cards & Grids */
        .grid-dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 1.25rem;
            margin-bottom: 1.5rem;
        }

        .stat-card {
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: var(--radius);
            padding: 1.25rem;
            box-shadow: var(--shadow-sm);
            display: flex;
            flex-direction: column;
            gap: 8px;
            border-left: 4px solid var(--primary);
        }

        .stat-card.green { border-left-color: var(--success); }
        .stat-card.amber { border-left-color: var(--warning); }
        .stat-card.teal { border-left-color: var(--accent); }

        .stat-label {
            font-size: 0.85rem;
            color: var(--text-muted);
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.03em;
        }

        .stat-value {
            font-size: 1.75rem;
            font-weight: 700;
            color: var(--text-dark);
        }

        /* Layout Container for Form + Table */
        .module-layout {
            display: grid;
            grid-template-columns: 360px 1fr;
            gap: 1.5rem;
            align-items: start;
        }

        @media (max-width: 1024px) {
            .module-layout {
                grid-template-columns: 1fr;
            }
        }

        .form-card {
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: var(--radius);
            padding: 1.5rem;
            box-shadow: var(--shadow-sm);
        }

        .form-card h3 {
            font-size: 1.1rem;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid var(--border-color);
            color: var(--text-dark);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .form-group {
            margin-bottom: 1rem;
            position: relative;
        }

        .form-group label {
            display: block;
            font-size: 0.82rem;
            font-weight: 600;
            color: var(--text-dark);
            margin-bottom: 0.35rem;
        }

        .form-control {
            width: 100%;
            padding: 0.6rem 0.75rem;
            border: 1px solid var(--border-color);
            border-radius: 6px;
            font-size: 0.9rem;
            background: #ffffff;
            transition: border-color 0.2s;
        }

        .form-control:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(2, 132, 199, 0.15);
        }

        .form-hint {
            font-size: 0.75rem;
            color: var(--text-muted);
            margin-top: 4px;
        }

        .btn-group {
            display: flex;
            gap: 10px;
            margin-top: 1.25rem;
        }

        .btn {
            padding: 0.6rem 1.25rem;
            font-size: 0.88rem;
            font-weight: 600;
            border-radius: 6px;
            cursor: pointer;
            border: none;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            transition: all 0.2s ease;
        }

        .btn-primary {
            background-color: var(--primary);
            color: #ffffff;
        }
        .btn-primary:hover {
            background-color: var(--primary-dark);
        }

        .btn-secondary {
            background-color: #f1f5f9;
            color: var(--text-dark);
            border: 1px solid var(--border-color);
        }
        .btn-secondary:hover {
            background-color: #e2e8f0;
        }

        .btn-danger {
            background-color: #fee2e2;
            color: var(--danger);
            border: 1px solid #fecaca;
        }
        .btn-danger:hover {
            background-color: var(--danger);
            color: #ffffff;
        }

        .btn-sm {
            padding: 0.35rem 0.7rem;
            font-size: 0.78rem;
        }

        /* Tables & Lists */
        .table-card {
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: var(--radius);
            box-shadow: var(--shadow-sm);
            overflow: hidden;
        }

        .table-header {
            padding: 1rem 1.5rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border-color);
            background: #ffffff;
        }

        .table-header h3 {
            font-size: 1.05rem;
            font-weight: 600;
        }

        .search-input {
            width: 260px;
            padding: 0.45rem 0.75rem;
            border: 1px solid var(--border-color);
            border-radius: 6px;
            font-size: 0.85rem;
        }

        .table-responsive {
            overflow-x: auto;
            max-height: 580px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            text-align: left;
            font-size: 0.875rem;
        }

        thead {
            background: #f8fafc;
            position: sticky;
            top: 0;
            z-index: 10;
        }

        th {
            padding: 0.75rem 1rem;
            font-weight: 600;
            color: var(--text-muted);
            border-bottom: 1px solid var(--border-color);
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }

        td {
            padding: 0.75rem 1rem;
            border-bottom: 1px solid var(--border-color);
            color: var(--text-dark);
        }

        tr:hover td {
            background: #f8fafc;
        }

        /* Badges */
        .badge {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 600;
        }

        .badge-success { background: #dcfce7; color: #15803d; }
        .badge-warning { background: #fef3c7; color: #b45309; }
        .badge-danger { background: #fee2e2; color: #b91c1c; }
        .badge-info { background: #e0f2fe; color: #0369a1; }
        .badge-purple { background: #f3e8ff; color: #7e22ce; }

        /* Auto-complete suggestions box */
        .autocomplete-items {
            position: absolute;
            border: 1px solid var(--border-color);
            border-top: none;
            z-index: 99;
            top: 100%;
            left: 0;
            right: 0;
            background: #ffffff;
            border-radius: 0 0 6px 6px;
            box-shadow: var(--shadow-md);
            max-height: 180px;
            overflow-y: auto;
        }

        .autocomplete-item {
            padding: 8px 12px;
            cursor: pointer;
            font-size: 0.85rem;
            border-bottom: 1px solid #f1f5f9;
        }

        .autocomplete-item:hover {
            background-color: var(--primary-light);
            color: var(--primary-dark);
        }

        /* Modal Popup (Confirmation Dialog - Q07 Feature) */
        .modal-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(15, 23, 42, 0.6);
            backdrop-filter: blur(2px);
            z-index: 1000;
            align-items: center;
            justify-content: center;
        }

        .modal-overlay.show {
            display: flex;
        }

        .modal-card {
            background: #ffffff;
            border-radius: var(--radius);
            width: 90%;
            max-width: 440px;
            padding: 1.5rem;
            box-shadow: var(--shadow-lg);
            animation: modalPop 0.2s cubic-bezier(0.16, 1, 0.3, 1);
        }

        @keyframes modalPop {
            from { transform: scale(0.92); opacity: 0; }
            to { transform: scale(1); opacity: 1; }
        }

        .modal-header {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 1rem;
        }

        .modal-icon-danger {
            background: #fee2e2;
            color: var(--danger);
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.25rem;
            flex-shrink: 0;
        }

        .modal-title {
            font-size: 1.15rem;
            font-weight: 700;
            color: var(--text-dark);
        }

        .modal-body {
            color: var(--text-muted);
            font-size: 0.9rem;
            line-height: 1.5;
            margin-bottom: 1.5rem;
        }

        .modal-actions {
            display: flex;
            justify-content: flex-end;
            gap: 10px;
        }

        /* Notification Toast */
        #toast {
            visibility: hidden;
            min-width: 250px;
            background-color: #1e293b;
            color: #fff;
            text-align: center;
            border-radius: 8px;
            padding: 12px 18px;
            position: fixed;
            z-index: 1100;
            right: 25px;
            bottom: 25px;
            font-size: 0.88rem;
            box-shadow: var(--shadow-lg);
            display: flex;
            align-items: center;
            gap: 10px;
            transition: all 0.3s ease;
            transform: translateY(20px);
            opacity: 0;
        }

        #toast.show {
            visibility: visible;
            transform: translateY(0);
            opacity: 1;
        }

        #toast.toast-success { background: #065f46; border-left: 4px solid #34d399; }
        #toast.toast-error { background: #991b1b; border-left: 4px solid #f87171; }

        /* Footer */
        footer {
            margin-top: auto;
            background: #ffffff;
            border-top: 1px solid var(--border-color);
            padding: 0.8rem 2rem;
            font-size: 0.78rem;
            color: var(--text-muted);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
    </style>
</head>
<body>

    <!-- Header -->
    <header>
        <div class="header-title">
            <div class="brand-icon">+</div>
            <div class="brand-text">
                <h1>Hospital Management System</h1>
                <p>Quality Goal: Q07 - Improve Data Accuracy | Student: Ajay Bora (Roll No. 2410302008)</p>
            </div>
        </div>
        <div class="header-badges">
            <span class="badge-tqm">BBAT104 TQM</span>
            <span class="badge-live"><span class="live-dot"></span> System Live</span>
        </div>
    </header>

    <!-- Navigation Tabs -->
    <nav id="navBar">
        <button class="nav-tab active" onclick="switchTab('dashboard')">📊 Dashboard</button>
        <button class="nav-tab" onclick="switchTab('patients')">👤 Patients</button>
        <button class="nav-tab" onclick="switchTab('doctors')">👨‍⚕️ Doctors</button>
        <button class="nav-tab" onclick="switchTab('appointments')">📅 Appointments</button>
        <button class="nav-tab" onclick="switchTab('rooms')">🏥 Rooms / Wards</button>
        <button class="nav-tab" onclick="switchTab('staff')">👥 Staff</button>
        <button class="nav-tab" onclick="switchTab('pharmacy')">💊 Pharmacy</button>
        <button class="nav-tab" onclick="switchTab('billing')">💳 Billing</button>
        <button class="nav-tab" onclick="switchTab('audit')">🛡️ Audit Log</button>
        <button class="nav-tab" onclick="switchTab('defects')">📋 Defect Checksheet</button>
    </nav>

    <!-- Main Content Area -->
    <main>

        <!-- ================= DASHBOARD TAB ================= -->
        <section id="tab-dashboard" class="tab-panel active">
            <div class="grid-dashboard">
                <div class="stat-card">
                    <span class="stat-label">Total Patients</span>
                    <span class="stat-value" id="stat-patients">0</span>
                </div>
                <div class="stat-card teal">
                    <span class="stat-label">Active Doctors</span>
                    <span class="stat-value" id="stat-doctors">0</span>
                </div>
                <div class="stat-card amber">
                    <span class="stat-label">Scheduled Appts</span>
                    <span class="stat-value" id="stat-appointments">0</span>
                </div>
                <div class="stat-card green">
                    <span class="stat-label">Available Rooms</span>
                    <span class="stat-value" id="stat-rooms">0</span>
                </div>
                <div class="stat-card">
                    <span class="stat-label">Low Stock Meds</span>
                    <span class="stat-value" id="stat-low-stock" style="color: var(--danger);">0</span>
                </div>
                <div class="stat-card green">
                    <span class="stat-label">Revenue Collected</span>
                    <span class="stat-value" id="stat-revenue">₹0</span>
                </div>
            </div>

            <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 1.5rem;">
                <div class="table-card">
                    <div class="table-header">
                        <h3>Recent Audit Log (Q07 Data Accuracy Verification)</h3>
                        <button class="btn btn-secondary btn-sm" onclick="loadAuditLogs()">Refresh Trail</button>
                    </div>
                    <div class="table-responsive">
                        <table>
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Timestamp</th>
                                    <th>Table</th>
                                    <th>Action</th>
                                    <th>Details</th>
                                    <th>User</th>
                                </tr>
                            </thead>
                            <tbody id="dashboard-audit-body">
                                <tr><td colspan="6" style="text-align: center; color: var(--text-muted);">Loading audit trail...</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                <div class="form-card">
                    <h3>Q07 Quality Features Active</h3>
                    <ul style="list-style: none; display: flex; flex-direction: column; gap: 12px; margin-top: 10px;">
                        <li style="display: flex; gap: 10px; font-size: 0.88rem;">
                            <span style="color: var(--success); font-weight: bold;">✓</span>
                            <div>
                                <strong>1. Input Masking</strong>
                                <p style="color: var(--text-muted); font-size: 0.78rem;">Phone numbers strictly formatted as +91-XXXXX-XXXXX.</p>
                            </div>
                        </li>
                        <li style="display: flex; gap: 10px; font-size: 0.88rem;">
                            <span style="color: var(--success); font-weight: bold;">✓</span>
                            <div>
                                <strong>2. Dropdown Lists</strong>
                                <p style="color: var(--text-muted); font-size: 0.78rem;">Enforced sets for Blood Groups, Shifts, Departments.</p>
                            </div>
                        </li>
                        <li style="display: flex; gap: 10px; font-size: 0.88rem;">
                            <span style="color: var(--success); font-weight: bold;">✓</span>
                            <div>
                                <strong>3. Auto-Complete</strong>
                                <p style="color: var(--text-muted); font-size: 0.78rem;">Real-time search suggestions in appointment bookings.</p>
                            </div>
                        </li>
                        <li style="display: flex; gap: 10px; font-size: 0.88rem;">
                            <span style="color: var(--success); font-weight: bold;">✓</span>
                            <div>
                                <strong>4. Confirmation Modals</strong>
                                <p style="color: var(--text-muted); font-size: 0.78rem;">Prevents accidental deletes and unauthorized updates.</p>
                            </div>
                        </li>
                        <li style="display: flex; gap: 10px; font-size: 0.88rem;">
                            <span style="color: var(--success); font-weight: bold;">✓</span>
                            <div>
                                <strong>5. Immutable Audit Trail</strong>
                                <p style="color: var(--text-muted); font-size: 0.78rem;">Every single INSERT, UPDATE, DELETE logged with timestamps.</p>
                            </div>
                        </li>
                    </ul>
                </div>
            </div>
        </section>

        <!-- ================= PATIENTS TAB ================= -->
        <section id="tab-patients" class="tab-panel">
            <div class="module-layout">
                <div class="form-card">
                    <h3 id="patient-form-title">Register Patient</h3>
                    <form id="patient-form" onsubmit="savePatient(event)">
                        <input type="hidden" id="patient-id">
                        <div class="form-group">
                            <label>Full Name *</label>
                            <input type="text" id="patient-name" class="form-control" required placeholder="e.g. Ramesh Kumar">
                        </div>
                        <div class="form-group">
                            <label>Gender (Q07 Dropdown) *</label>
                            <select id="patient-gender" class="form-control" required>
                                {% for g in genders %}<option value="{{ g }}">{{ g }}</option>{% endfor %}
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Date of Birth *</label>
                            <input type="date" id="patient-dob" class="form-control" required>
                        </div>
                        <div class="form-group">
                            <label>Blood Group (Q07 Dropdown) *</label>
                            <select id="patient-blood" class="form-control" required>
                                {% for b in blood_groups %}<option value="{{ b }}">{{ b }}</option>{% endfor %}
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Phone Number (Q07 Masking) *</label>
                            <input type="text" id="patient-phone" class="form-control phone-mask" required placeholder="+91-XXXXX-XXXXX">
                            <div class="form-hint">Auto-formats to +91-XXXXX-XXXXX</div>
                        </div>
                        <div class="form-group">
                            <label>Address</label>
                            <input type="text" id="patient-address" class="form-control" placeholder="City, Street">
                        </div>
                        <div class="form-group">
                            <label>Assign Ward / Room</label>
                            <select id="patient-room" class="form-control">
                                <option value="">-- None / Outpatient --</option>
                            </select>
                        </div>
                        <div class="btn-group">
                            <button type="submit" class="btn btn-primary" style="flex:1;">Save Patient</button>
                            <button type="button" class="btn btn-secondary" onclick="resetPatientForm()">Clear</button>
                        </div>
                    </form>
                </div>

                <div class="table-card">
                    <div class="table-header">
                        <h3>Registered Patients</h3>
                        <input type="text" class="search-input" id="search-patients" placeholder="Search by name..." oninput="loadPatients(this.value)">
                    </div>
                    <div class="table-responsive">
                        <table>
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Full Name</th>
                                    <th>Gender</th>
                                    <th>DOB</th>
                                    <th>Blood</th>
                                    <th>Phone</th>
                                    <th>Room</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody id="patients-table-body">
                                <tr><td colspan="8" style="text-align: center;">Loading patients...</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </section>

        <!-- ================= DOCTORS TAB ================= -->
        <section id="tab-doctors" class="tab-panel">
            <div class="module-layout">
                <div class="form-card">
                    <h3 id="doctor-form-title">Add Doctor</h3>
                    <form id="doctor-form" onsubmit="saveDoctor(event)">
                        <input type="hidden" id="doctor-id">
                        <div class="form-group">
                            <label>Full Name *</label>
                            <input type="text" id="doctor-name" class="form-control" required placeholder="e.g. Dr. Rajesh Sharma">
                        </div>
                        <div class="form-group">
                            <label>Department (Q07 Dropdown) *</label>
                            <select id="doctor-department" class="form-control" required>
                                {% for d in departments %}<option value="{{ d }}">{{ d }}</option>{% endfor %}
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Phone Number (Q07 Masking) *</label>
                            <input type="text" id="doctor-phone" class="form-control phone-mask" required placeholder="+91-XXXXX-XXXXX">
                        </div>
                        <div class="btn-group">
                            <button type="submit" class="btn btn-primary" style="flex:1;">Save Doctor</button>
                            <button type="button" class="btn btn-secondary" onclick="resetDoctorForm()">Clear</button>
                        </div>
                    </form>
                </div>

                <div class="table-card">
                    <div class="table-header">
                        <h3>Medical Staff & Doctors</h3>
                    </div>
                    <div class="table-responsive">
                        <table>
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Doctor Name</th>
                                    <th>Department</th>
                                    <th>Phone</th>
                                    <th>Created At</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody id="doctors-table-body">
                                <tr><td colspan="6" style="text-align: center;">Loading doctors...</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </section>

        <!-- ================= APPOINTMENTS TAB ================= -->
        <section id="tab-appointments" class="tab-panel">
            <div class="module-layout">
                <div class="form-card">
                    <h3 id="appt-form-title">Schedule Appointment</h3>
                    <form id="appt-form" onsubmit="saveAppointment(event)">
                        <input type="hidden" id="appt-id">
                        <input type="hidden" id="appt-patient-id">
                        <div class="form-group">
                            <label>Patient Name (Q07 Auto-Complete) *</label>
                            <input type="text" id="appt-patient-name" class="form-control" required placeholder="Type to search patient..." autocomplete="off">
                            <div id="patient-autocomplete-box" class="autocomplete-items" style="display:none;"></div>
                            <div class="form-hint">Type 1+ letters to see suggestions</div>
                        </div>
                        <div class="form-group">
                            <label>Doctor (Q07 Dropdown) *</label>
                            <select id="appt-doctor-id" class="form-control" required>
                                <option value="">-- Select Doctor --</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Date *</label>
                            <input type="date" id="appt-date" class="form-control" required>
                        </div>
                        <div class="form-group">
                            <label>Time (HH:MM) *</label>
                            <input type="time" id="appt-time" class="form-control" required>
                        </div>
                        <div class="form-group">
                            <label>Status (Q07 Dropdown) *</label>
                            <select id="appt-status" class="form-control" required>
                                {% for s in appt_statuses %}<option value="{{ s }}">{{ s }}</option>{% endfor %}
                            </select>
                        </div>
                        <div class="btn-group">
                            <button type="submit" class="btn btn-primary" style="flex:1;">Book Appointment</button>
                            <button type="button" class="btn btn-secondary" onclick="resetApptForm()">Clear</button>
                        </div>
                    </form>
                </div>

                <div class="table-card">
                    <div class="table-header">
                        <h3>Appointments Schedule</h3>
                    </div>
                    <div class="table-responsive">
                        <table>
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Patient</th>
                                    <th>Doctor</th>
                                    <th>Date</th>
                                    <th>Time</th>
                                    <th>Status</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody id="appts-table-body">
                                <tr><td colspan="7" style="text-align: center;">Loading appointments...</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </section>

        <!-- ================= ROOMS / WARDS TAB ================= -->
        <section id="tab-rooms" class="tab-panel">
            <div class="module-layout">
                <div class="form-card">
                    <h3 id="room-form-title">Add Room / Ward</h3>
                    <form id="room-form" onsubmit="saveRoom(event)">
                        <input type="hidden" id="room-id">
                        <div class="form-group">
                            <label>Room Number *</label>
                            <input type="text" id="room-number" class="form-control" required placeholder="e.g. 101, ICU-1">
                        </div>
                        <div class="form-group">
                            <label>Room Type (Q07 Dropdown) *</label>
                            <select id="room-type" class="form-control" required>
                                {% for t in room_types %}<option value="{{ t }}">{{ t }}</option>{% endfor %}
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Status (Q07 Dropdown) *</label>
                            <select id="room-status" class="form-control" required>
                                {% for s in room_statuses %}<option value="{{ s }}">{{ s }}</option>{% endfor %}
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Rate Per Day (₹) *</label>
                            <input type="number" step="0.01" id="room-rate" class="form-control" required placeholder="1500.00">
                        </div>
                        <div class="btn-group">
                            <button type="submit" class="btn btn-primary" style="flex:1;">Save Room</button>
                            <button type="button" class="btn btn-secondary" onclick="resetRoomForm()">Clear</button>
                        </div>
                    </form>
                </div>

                <div class="table-card">
                    <div class="table-header">
                        <h3>Rooms & Wards Availability</h3>
                    </div>
                    <div class="table-responsive">
                        <table>
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Room No.</th>
                                    <th>Type</th>
                                    <th>Status</th>
                                    <th>Rate / Day</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody id="rooms-table-body">
                                <tr><td colspan="6" style="text-align: center;">Loading rooms...</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </section>

        <!-- ================= STAFF TAB ================= -->
        <section id="tab-staff" class="tab-panel">
            <div class="module-layout">
                <div class="form-card">
                    <h3 id="staff-form-title">Add Staff Member</h3>
                    <form id="staff-form" onsubmit="saveStaff(event)">
                        <input type="hidden" id="staff-id">
                        <div class="form-group">
                            <label>Full Name *</label>
                            <input type="text" id="staff-name" class="form-control" required placeholder="e.g. Sunita Devi">
                        </div>
                        <div class="form-group">
                            <label>Role (Q07 Dropdown) *</label>
                            <select id="staff-role" class="form-control" required>
                                {% for r in staff_roles %}<option value="{{ r }}">{{ r }}</option>{% endfor %}
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Shift (Q07 Dropdown) *</label>
                            <select id="staff-shift" class="form-control" required>
                                {% for s in shifts %}<option value="{{ s }}">{{ s }}</option>{% endfor %}
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Phone Number (Q07 Masking) *</label>
                            <input type="text" id="staff-phone" class="form-control phone-mask" required placeholder="+91-XXXXX-XXXXX">
                        </div>
                        <div class="btn-group">
                            <button type="submit" class="btn btn-primary" style="flex:1;">Save Staff</button>
                            <button type="button" class="btn btn-secondary" onclick="resetStaffForm()">Clear</button>
                        </div>
                    </form>
                </div>

                <div class="table-card">
                    <div class="table-header">
                        <h3>Hospital Staff Directory</h3>
                    </div>
                    <div class="table-responsive">
                        <table>
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Full Name</th>
                                    <th>Role</th>
                                    <th>Shift</th>
                                    <th>Phone</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody id="staff-table-body">
                                <tr><td colspan="6" style="text-align: center;">Loading staff...</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </section>

        <!-- ================= PHARMACY TAB ================= -->
        <section id="tab-pharmacy" class="tab-panel">
            <div class="module-layout">
                <div class="form-card">
                    <h3 id="med-form-title">Add Medicine</h3>
                    <form id="med-form" onsubmit="saveMedicine(event)">
                        <input type="hidden" id="med-id">
                        <div class="form-group">
                            <label>Medicine Name *</label>
                            <input type="text" id="med-name" class="form-control" required placeholder="e.g. Paracetamol 500mg">
                        </div>
                        <div class="form-group">
                            <label>Category (Q07 Dropdown) *</label>
                            <select id="med-category" class="form-control" required>
                                {% for c in medicine_categories %}<option value="{{ c }}">{{ c }}</option>{% endfor %}
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Stock Quantity *</label>
                            <input type="number" id="med-stock" class="form-control" required placeholder="100">
                        </div>
                        <div class="form-group">
                            <label>Unit Price (₹) *</label>
                            <input type="number" step="0.01" id="med-price" class="form-control" required placeholder="15.50">
                        </div>
                        <div class="form-group">
                            <label>Reorder Level *</label>
                            <input type="number" id="med-reorder" class="form-control" required value="10">
                        </div>
                        <div class="btn-group">
                            <button type="submit" class="btn btn-primary" style="flex:1;">Save Medicine</button>
                            <button type="button" class="btn btn-secondary" onclick="resetMedForm()">Clear</button>
                        </div>
                    </form>
                </div>

                <div class="table-card">
                    <div class="table-header">
                        <h3>Pharmacy Inventory</h3>
                        <button class="btn btn-secondary btn-sm" onclick="filterLowStock()">Toggle Low Stock Warning</button>
                    </div>
                    <div class="table-responsive">
                        <table>
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Name</th>
                                    <th>Category</th>
                                    <th>Stock</th>
                                    <th>Unit Price</th>
                                    <th>Reorder Lvl</th>
                                    <th>Status</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody id="meds-table-body">
                                <tr><td colspan="8" style="text-align: center;">Loading medicines...</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </section>

        <!-- ================= BILLING TAB ================= -->
        <section id="tab-billing" class="tab-panel">
            <div class="module-layout">
                <div class="form-card">
                    <h3 id="bill-form-title">Generate Patient Invoice</h3>
                    <form id="bill-form" onsubmit="saveBill(event)">
                        <input type="hidden" id="bill-id">
                        <input type="hidden" id="bill-patient-id">
                        <div class="form-group">
                            <label>Patient (Q07 Auto-Complete) *</label>
                            <input type="text" id="bill-patient-name" class="form-control" required placeholder="Search patient..." autocomplete="off">
                            <div id="bill-patient-autocomplete" class="autocomplete-items" style="display:none;"></div>
                        </div>
                        <div class="form-group">
                            <label>Room Charges (₹) *</label>
                            <input type="number" step="0.01" id="bill-room" class="form-control calc-total" required value="0">
                        </div>
                        <div class="form-group">
                            <label>Consultation Fee (₹) *</label>
                            <input type="number" step="0.01" id="bill-consult" class="form-control calc-total" required value="500">
                        </div>
                        <div class="form-group">
                            <label>Medicine Charges (₹) *</label>
                            <input type="number" step="0.01" id="bill-med" class="form-control calc-total" required value="0">
                        </div>
                        <div class="form-group">
                            <label>Payment Method (Q07 Dropdown) *</label>
                            <select id="bill-method" class="form-control" required>
                                {% for m in payment_methods %}<option value="{{ m }}">{{ m }}</option>{% endfor %}
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Payment Status (Q07 Dropdown) *</label>
                            <select id="bill-status" class="form-control" required>
                                {% for s in payment_statuses %}<option value="{{ s }}">{{ s }}</option>{% endfor %}
                            </select>
                        </div>
                        <div style="background: #f1f5f9; padding: 12px; border-radius: 6px; margin-bottom: 1rem;">
                            <span style="font-size: 0.85rem; color: var(--text-muted);">Calculated Grand Total:</span>
                            <div id="bill-calculated-total" style="font-size: 1.4rem; font-weight: 700; color: var(--primary);">₹500.00</div>
                        </div>
                        <div class="btn-group">
                            <button type="submit" class="btn btn-primary" style="flex:1;">Generate Bill</button>
                            <button type="button" class="btn btn-secondary" onclick="resetBillForm()">Clear</button>
                        </div>
                    </form>
                </div>

                <div class="table-card">
                    <div class="table-header">
                        <h3>Patient Invoices</h3>
                    </div>
                    <div class="table-responsive">
                        <table>
                            <thead>
                                <tr>
                                    <th>Bill ID</th>
                                    <th>Patient</th>
                                    <th>Room (₹)</th>
                                    <th>Consult (₹)</th>
                                    <th>Meds (₹)</th>
                                    <th>Total (₹)</th>
                                    <th>Method</th>
                                    <th>Status</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody id="bills-table-body">
                                <tr><td colspan="9" style="text-align: center;">Loading bills...</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </section>

        <!-- ================= AUDIT LOG TAB ================= -->
        <section id="tab-audit" class="tab-panel">
            <div class="table-card">
                <div class="table-header">
                    <div>
                        <h3>Immutable Audit Trail (Q07 Core Quality Feature)</h3>
                        <p style="font-size: 0.8rem; color: var(--text-muted);">Captures user, timestamp, table, record_id, and mutation action for complete regulatory accuracy.</p>
                    </div>
                    <button class="btn btn-secondary btn-sm" onclick="loadAuditLogs()">Refresh Trail</button>
                </div>
                <div class="table-responsive">
                    <table>
                        <thead>
                            <tr>
                                <th>Log ID</th>
                                <th>Timestamp</th>
                                <th>Table</th>
                                <th>Record ID</th>
                                <th>Action</th>
                                <th>Details</th>
                                <th>User</th>
                            </tr>
                        </thead>
                        <tbody id="audit-table-body">
                            <tr><td colspan="7" style="text-align: center;">Loading audit logs...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </section>

        <!-- ================= DEFECT CHECKSHEET TAB ================= -->
        <section id="tab-defects" class="tab-panel">
            <div class="module-layout">
                <div class="form-card">
                    <h3>Log Defect / Data Error</h3>
                    <p style="font-size: 0.8rem; color: var(--text-muted); margin-bottom: 1rem;">Feeds the SQC Pareto Analysis checksheet to monitor and minimize data accuracy errors.</p>
                    <form id="defect-form" onsubmit="saveDefect(event)">
                        <div class="form-group">
                            <label>Category (Q07 Dropdown) *</label>
                            <select id="defect-category" class="form-control" required>
                                {% for c in defect_categories %}<option value="{{ c }}">{{ c }}</option>{% endfor %}
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Severity (Q07 Dropdown) *</label>
                            <select id="defect-severity" class="form-control" required>
                                {% for s in defect_severities %}<option value="{{ s }}">{{ s }}</option>{% endfor %}
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Description of Incident *</label>
                            <textarea id="defect-desc" class="form-control" rows="3" required placeholder="Details of the discrepancy or data validation catch..."></textarea>
                        </div>
                        <div class="btn-group">
                            <button type="submit" class="btn btn-primary" style="flex:1;">Log Defect</button>
                            <button type="reset" class="btn btn-secondary">Clear</button>
                        </div>
                    </form>
                </div>

                <div class="table-card">
                    <div class="table-header">
                        <h3>SQC Defect Checksheet</h3>
                    </div>
                    <div class="table-responsive">
                        <table>
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Logged At</th>
                                    <th>Category</th>
                                    <th>Severity</th>
                                    <th>Status</th>
                                    <th>Description</th>
                                </tr>
                            </thead>
                            <tbody id="defects-table-body">
                                <tr><td colspan="6" style="text-align: center;">Loading defects...</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </section>

    </main>

    <!-- Confirmation Modal (Q07 Safeguard) -->
    <div id="confirmModal" class="modal-overlay">
        <div class="modal-card">
            <div class="modal-header">
                <div class="modal-icon-danger">⚠️</div>
                <div class="modal-title" id="modalTitle">Confirm Action</div>
            </div>
            <div class="modal-body" id="modalMessage">
                Are you sure you want to proceed?
            </div>
            <div class="modal-actions">
                <button type="button" class="btn btn-secondary" onclick="closeModal()">Cancel</button>
                <button type="button" class="btn btn-danger" id="modalConfirmBtn">Yes, Confirm</button>
            </div>
        </div>
    </div>

    <!-- Notification Toast -->
    <div id="toast">
        <span id="toastIcon">✓</span>
        <span id="toastMsg">Action completed successfully</span>
    </div>

    <!-- Footer -->
    <footer>
        <div>Hospital Management System | BBAT104 Course Project 2026-27 | Baseline: HMS | Quality Goal: Q07 Improve Data Accuracy</div>
        <div>Ajay Bora (CSE-B) | Single Source of Truth: SQLite Database</div>
    </footer>

    <!-- ================= CLIENT JAVASCRIPT ================= -->
    <script>
        let currentTab = 'dashboard';
        let pendingModalAction = null;

        // Toast notification handler
        function showToast(msg, isError = false) {
            const toast = document.getElementById('toast');
            const toastMsg = document.getElementById('toastMsg');
            const toastIcon = document.getElementById('toastIcon');
            toastMsg.innerText = msg;
            toastIcon.innerText = isError ? '✕' : '✓';
            toast.className = isError ? 'show toast-error' : 'show toast-success';
            setTimeout(() => { toast.className = ''; }, 3200);
        }

        // Q07 Modal Dialog Trigger
        function openConfirmModal(title, message, onConfirm) {
            document.getElementById('modalTitle').innerText = title;
            document.getElementById('modalMessage').innerText = message;
            pendingModalAction = onConfirm;
            document.getElementById('confirmModal').classList.add('show');
        }

        function closeModal() {
            document.getElementById('confirmModal').classList.remove('show');
            pendingModalAction = null;
        }

        document.getElementById('modalConfirmBtn').addEventListener('click', () => {
            if (pendingModalAction) {
                pendingModalAction();
            }
            closeModal();
        });

        // Tab Switching
        function switchTab(tabId) {
            currentTab = tabId;
            document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
            document.querySelectorAll('.nav-tab').forEach(b => b.classList.remove('active'));
            
            const targetPanel = document.getElementById(`tab-${tabId}`);
            if (targetPanel) targetPanel.classList.add('active');

            const navTabs = document.querySelectorAll('.nav-tab');
            navTabs.forEach(b => {
                if (b.getAttribute('onclick').includes(tabId)) {
                    b.classList.add('active');
                }
            });

            // Lazy data refreshes
            if (tabId === 'dashboard') loadDashboardData();
            if (tabId === 'patients') { loadPatients(); loadRoomChoices(); }
            if (tabId === 'doctors') loadDoctors();
            if (tabId === 'appointments') { loadAppointments(); loadDoctorChoices(); }
            if (tabId === 'rooms') loadRooms();
            if (tabId === 'staff') loadStaff();
            if (tabId === 'pharmacy') loadMedicines();
            if (tabId === 'billing') loadBills();
            if (tabId === 'audit') loadAuditLogs();
            if (tabId === 'defects') loadDefects();
        }

        // Q07 Feature: Input Masking for Phone (+91-XXXXX-XXXXX)
        function setupPhoneMasking() {
            document.querySelectorAll('.phone-mask').forEach(input => {
                input.addEventListener('input', (e) => {
                    let digits = e.target.value.replace(/\\D/g, '');
                    if (digits.startsWith('91')) {
                        digits = digits.substring(2);
                    }
                    digits = digits.substring(0, 10);
                    if (digits.length === 0) {
                        e.target.value = '';
                    } else if (digits.length <= 5) {
                        e.target.value = `+91-${digits}`;
                    } else {
                        e.target.value = `+91-${digits.substring(0, 5)}-${digits.substring(5)}`;
                    }
                });
            });
        }

        // Q07 Feature: Auto-Complete helper
        function setupAutocomplete(inputEl, boxEl, fetchUrl, onSelect) {
            inputEl.addEventListener('input', async (e) => {
                const val = e.target.value.trim();
                if (val.length < 1) {
                    boxEl.style.display = 'none';
                    return;
                }
                try {
                    const res = await fetch(`${fetchUrl}?prefix=${encodeURIComponent(val)}`);
                    const items = await res.json();
                    if (!items || items.length === 0) {
                        boxEl.style.display = 'none';
                        return;
                    }
                    boxEl.innerHTML = '';
                    items.forEach(it => {
                        const div = document.createElement('div');
                        div.className = 'autocomplete-item';
                        div.innerText = it.label || it;
                        div.addEventListener('click', () => {
                            inputEl.value = it.label || it;
                            boxEl.style.display = 'none';
                            onSelect(it);
                        });
                        boxEl.appendChild(div);
                    });
                    boxEl.style.display = 'block';
                } catch (err) {
                    boxEl.style.display = 'none';
                }
            });

            document.addEventListener('click', (e) => {
                if (e.target !== inputEl && e.target !== boxEl) {
                    boxEl.style.display = 'none';
                }
            });
        }

        // --- DASHBOARD API ---
        async function loadDashboardData() {
            try {
                const res = await fetch('/api/dashboard/stats');
                const stats = await res.json();
                document.getElementById('stat-patients').innerText = stats.total_patients;
                document.getElementById('stat-doctors').innerText = stats.total_doctors;
                document.getElementById('stat-appointments').innerText = stats.scheduled_appts;
                document.getElementById('stat-rooms').innerText = stats.available_rooms;
                document.getElementById('stat-low-stock').innerText = stats.low_stock_meds;
                document.getElementById('stat-revenue').innerText = `₹${stats.total_revenue.toLocaleString('en-IN')}`;

                const tbody = document.getElementById('dashboard-audit-body');
                if (stats.recent_audit.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;">No audit records found</td></tr>';
                } else {
                    tbody.innerHTML = stats.recent_audit.slice(0, 8).map(a => `
                        <tr>
                            <td>#${a.log_id}</td>
                            <td>${a.timestamp}</td>
                            <td><code>${a.table_name}</code></td>
                            <td><span class="badge ${a.action === 'INSERT' ? 'badge-success' : a.action === 'UPDATE' ? 'badge-warning' : 'badge-danger'}">${a.action}</span></td>
                            <td>${a.details || '-'}</td>
                            <td>${a.performed_by}</td>
                        </tr>
                    `).join('');
                }
            } catch (err) {
                console.error(err);
            }
        }

        // --- PATIENTS API ---
        async function loadPatients(query = '') {
            try {
                const res = await fetch(`/api/patients?q=${encodeURIComponent(query)}`);
                const data = await res.json();
                const tbody = document.getElementById('patients-table-body');
                if (data.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="8" style="text-align: center;">No patients found.</td></tr>';
                    return;
                }
                tbody.innerHTML = data.map(p => `
                    <tr>
                        <td><strong>#${p.patient_id}</strong></td>
                        <td>${p.full_name}</td>
                        <td>${p.gender}</td>
                        <td>${p.dob}</td>
                        <td><span class="badge badge-info">${p.blood_group}</span></td>
                        <td>${p.phone}</td>
                        <td>${p.room_id ? 'Room #' + p.room_id : '<span style="color:var(--text-muted);">-</span>'}</td>
                        <td>
                            <button class="btn btn-secondary btn-sm" onclick='editPatient(${JSON.stringify(p)})'>Edit</button>
                            <button class="btn btn-danger btn-sm" onclick="confirmDeletePatient(${p.patient_id}, '${p.full_name}')">Del</button>
                        </td>
                    </tr>
                `).join('');
            } catch (err) {
                showToast('Failed to load patients', true);
            }
        }

        async function loadRoomChoices() {
            const res = await fetch('/api/rooms/choices?available_only=1');
            const choices = await res.json();
            const sel = document.getElementById('patient-room');
            sel.innerHTML = '<option value="">-- None / Outpatient --</option>' +
                choices.map(c => `<option value="${c.id}">${c.label}</option>`).join('');
        }

        async function savePatient(e) {
            e.preventDefault();
            const id = document.getElementById('patient-id').value;
            const payload = {
                full_name: document.getElementById('patient-name').value,
                gender: document.getElementById('patient-gender').value,
                dob: document.getElementById('patient-dob').value,
                blood_group: document.getElementById('patient-blood').value,
                phone: document.getElementById('patient-phone').value,
                address: document.getElementById('patient-address').value,
                room_id: document.getElementById('patient-room').value || null
            };

            const url = id ? `/api/patients/${id}` : '/api/patients';
            const method = id ? 'PUT' : 'POST';

            const res = await fetch(url, {
                method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (res.ok) {
                showToast(id ? 'Patient updated successfully' : 'Patient registered successfully');
                resetPatientForm();
                loadPatients();
                loadDashboardData();
            } else {
                const err = await res.json();
                showToast(err.error || 'Validation error', true);
            }
        }

        function editPatient(p) {
            document.getElementById('patient-id').value = p.patient_id;
            document.getElementById('patient-name').value = p.full_name;
            document.getElementById('patient-gender').value = p.gender;
            document.getElementById('patient-dob').value = p.dob;
            document.getElementById('patient-blood').value = p.blood_group;
            document.getElementById('patient-phone').value = p.phone;
            document.getElementById('patient-address').value = p.address || '';
            document.getElementById('patient-room').value = p.room_id || '';
            document.getElementById('patient-form-title').innerText = `Edit Patient #${p.patient_id}`;
        }

        function resetPatientForm() {
            document.getElementById('patient-form').reset();
            document.getElementById('patient-id').value = '';
            document.getElementById('patient-form-title').innerText = 'Register Patient';
        }

        function confirmDeletePatient(id, name) {
            openConfirmModal('Delete Patient Record', `Are you sure you want to permanently remove patient '${name}'? This action is audited.`, async () => {
                const res = await fetch(`/api/patients/${id}`, { method: 'DELETE' });
                if (res.ok) {
                    showToast('Patient deleted');
                    loadPatients();
                    loadDashboardData();
                } else {
                    showToast('Failed to delete patient', true);
                }
            });
        }

        // --- DOCTORS API ---
        async function loadDoctors() {
            const res = await fetch('/api/doctors');
            const data = await res.json();
            const tbody = document.getElementById('doctors-table-body');
            tbody.innerHTML = data.map(d => `
                <tr>
                    <td><strong>#${d.doctor_id}</strong></td>
                    <td>${d.full_name}</td>
                    <td><span class="badge badge-purple">${d.department}</span></td>
                    <td>${d.phone}</td>
                    <td>${d.created_at}</td>
                    <td>
                        <button class="btn btn-secondary btn-sm" onclick='editDoctor(${JSON.stringify(d)})'>Edit</button>
                        <button class="btn btn-danger btn-sm" onclick="confirmDeleteDoctor(${d.doctor_id}, '${d.full_name}')">Del</button>
                    </td>
                </tr>
            `).join('');
        }

        async function saveDoctor(e) {
            e.preventDefault();
            const id = document.getElementById('doctor-id').value;
            const payload = {
                full_name: document.getElementById('doctor-name').value,
                department: document.getElementById('doctor-department').value,
                phone: document.getElementById('doctor-phone').value
            };
            const url = id ? `/api/doctors/${id}` : '/api/doctors';
            const method = id ? 'PUT' : 'POST';
            const res = await fetch(url, { method, headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload)});
            if (res.ok) {
                showToast(id ? 'Doctor record updated' : 'Doctor registered successfully');
                resetDoctorForm();
                loadDoctors();
                loadDashboardData();
            } else {
                showToast('Failed to save doctor', true);
            }
        }

        function editDoctor(d) {
            document.getElementById('doctor-id').value = d.doctor_id;
            document.getElementById('doctor-name').value = d.full_name;
            document.getElementById('doctor-department').value = d.department;
            document.getElementById('doctor-phone').value = d.phone;
            document.getElementById('doctor-form-title').innerText = `Edit Doctor #${d.doctor_id}`;
        }

        function resetDoctorForm() {
            document.getElementById('doctor-form').reset();
            document.getElementById('doctor-id').value = '';
            document.getElementById('doctor-form-title').innerText = 'Add Doctor';
        }

        function confirmDeleteDoctor(id, name) {
            openConfirmModal('Delete Doctor Record', `Are you sure you want to delete '${name}'?`, async () => {
                await fetch(`/api/doctors/${id}`, { method: 'DELETE' });
                showToast('Doctor deleted');
                loadDoctors();
                loadDashboardData();
            });
        }

        // --- APPOINTMENTS API ---
        async function loadDoctorChoices() {
            const res = await fetch('/api/doctors/choices');
            const choices = await res.json();
            const sel = document.getElementById('appt-doctor-id');
            sel.innerHTML = '<option value="">-- Select Doctor --</option>' +
                choices.map(c => `<option value="${c.id}">${c.label}</option>`).join('');
        }

        async function loadAppointments() {
            const res = await fetch('/api/appointments');
            const data = await res.json();
            const tbody = document.getElementById('appts-table-body');
            tbody.innerHTML = data.map(a => `
                <tr>
                    <td><strong>#${a.appointment_id}</strong></td>
                    <td>${a.patient}</td>
                    <td>${a.doctor}</td>
                    <td>${a.appt_date}</td>
                    <td>${a.appt_time}</td>
                    <td><span class="badge ${a.status === 'Completed' ? 'badge-success' : a.status === 'Cancelled' ? 'badge-danger' : 'badge-warning'}">${a.status}</span></td>
                    <td>
                        <button class="btn btn-secondary btn-sm" onclick='editAppt(${JSON.stringify(a)})'>Edit</button>
                        <button class="btn btn-danger btn-sm" onclick="confirmDeleteAppt(${a.appointment_id})">Del</button>
                    </td>
                </tr>
            `).join('');
        }

        async function saveAppointment(e) {
            e.preventDefault();
            const id = document.getElementById('appt-id').value;
            const patientId = document.getElementById('appt-patient-id').value;
            if (!patientId) {
                showToast('Please select a valid patient using auto-complete suggestions', true);
                return;
            }
            const payload = {
                patient_id: patientId,
                doctor_id: document.getElementById('appt-doctor-id').value,
                appt_date: document.getElementById('appt-date').value,
                appt_time: document.getElementById('appt-time').value,
                status: document.getElementById('appt-status').value
            };
            const url = id ? `/api/appointments/${id}` : '/api/appointments';
            const method = id ? 'PUT' : 'POST';
            const res = await fetch(url, { method, headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload)});
            if (res.ok) {
                showToast('Appointment saved');
                resetApptForm();
                loadAppointments();
                loadDashboardData();
            } else {
                showToast('Error booking appointment', true);
            }
        }

        function editAppt(a) {
            document.getElementById('appt-id').value = a.appointment_id;
            document.getElementById('appt-patient-name').value = a.patient;
            document.getElementById('appt-date').value = a.appt_date;
            document.getElementById('appt-time').value = a.appt_time;
            document.getElementById('appt-status').value = a.status;
            document.getElementById('appt-form-title').innerText = `Edit Appointment #${a.appointment_id}`;
        }

        function resetApptForm() {
            document.getElementById('appt-form').reset();
            document.getElementById('appt-id').value = '';
            document.getElementById('appt-patient-id').value = '';
            document.getElementById('appt-form-title').innerText = 'Schedule Appointment';
        }

        function confirmDeleteAppt(id) {
            openConfirmModal('Cancel Appointment', `Delete appointment #${id}?`, async () => {
                await fetch(`/api/appointments/${id}`, { method: 'DELETE' });
                showToast('Appointment deleted');
                loadAppointments();
                loadDashboardData();
            });
        }

        // --- ROOMS API ---
        async function loadRooms() {
            const res = await fetch('/api/rooms');
            const data = await res.json();
            const tbody = document.getElementById('rooms-table-body');
            tbody.innerHTML = data.map(r => `
                <tr>
                    <td><strong>#${r.room_id}</strong></td>
                    <td>Room ${r.room_number}</td>
                    <td>${r.room_type}</td>
                    <td><span class="badge ${r.status === 'Available' ? 'badge-success' : r.status === 'Occupied' ? 'badge-danger' : 'badge-warning'}">${r.status}</span></td>
                    <td>₹${parseFloat(r.rate_per_day).toFixed(2)}</td>
                    <td>
                        <button class="btn btn-secondary btn-sm" onclick='editRoom(${JSON.stringify(r)})'>Edit</button>
                        <button class="btn btn-danger btn-sm" onclick="confirmDeleteRoom(${r.room_id})">Del</button>
                    </td>
                </tr>
            `).join('');
        }

        async function saveRoom(e) {
            e.preventDefault();
            const id = document.getElementById('room-id').value;
            const payload = {
                room_number: document.getElementById('room-number').value,
                room_type: document.getElementById('room-type').value,
                status: document.getElementById('room-status').value,
                rate_per_day: parseFloat(document.getElementById('room-rate').value)
            };
            const url = id ? `/api/rooms/${id}` : '/api/rooms';
            const method = id ? 'PUT' : 'POST';
            const res = await fetch(url, { method, headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload)});
            if (res.ok) {
                showToast('Room saved');
                resetRoomForm();
                loadRooms();
                loadDashboardData();
            } else {
                showToast('Failed to save room', true);
            }
        }

        function editRoom(r) {
            document.getElementById('room-id').value = r.room_id;
            document.getElementById('room-number').value = r.room_number;
            document.getElementById('room-type').value = r.room_type;
            document.getElementById('room-status').value = r.status;
            document.getElementById('room-rate').value = r.rate_per_day;
            document.getElementById('room-form-title').innerText = `Edit Room #${r.room_number}`;
        }

        function resetRoomForm() {
            document.getElementById('room-form').reset();
            document.getElementById('room-id').value = '';
            document.getElementById('room-form-title').innerText = 'Add Room / Ward';
        }

        function confirmDeleteRoom(id) {
            openConfirmModal('Delete Room', `Delete room #${id}?`, async () => {
                await fetch(`/api/rooms/${id}`, { method: 'DELETE' });
                showToast('Room deleted');
                loadRooms();
                loadDashboardData();
            });
        }

        // --- STAFF API ---
        async function loadStaff() {
            const res = await fetch('/api/staff');
            const data = await res.json();
            const tbody = document.getElementById('staff-table-body');
            tbody.innerHTML = data.map(s => `
                <tr>
                    <td><strong>#${s.staff_id}</strong></td>
                    <td>${s.full_name}</td>
                    <td><span class="badge badge-info">${s.role}</span></td>
                    <td>${s.shift}</td>
                    <td>${s.phone}</td>
                    <td>
                        <button class="btn btn-secondary btn-sm" onclick='editStaff(${JSON.stringify(s)})'>Edit</button>
                        <button class="btn btn-danger btn-sm" onclick="confirmDeleteStaff(${s.staff_id})">Del</button>
                    </td>
                </tr>
            `).join('');
        }

        async function saveStaff(e) {
            e.preventDefault();
            const id = document.getElementById('staff-id').value;
            const payload = {
                full_name: document.getElementById('staff-name').value,
                role: document.getElementById('staff-role').value,
                shift: document.getElementById('staff-shift').value,
                phone: document.getElementById('staff-phone').value
            };
            const url = id ? `/api/staff/${id}` : '/api/staff';
            const method = id ? 'PUT' : 'POST';
            const res = await fetch(url, { method, headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload)});
            if (res.ok) {
                showToast('Staff saved');
                resetStaffForm();
                loadStaff();
            } else {
                showToast('Failed to save staff', true);
            }
        }

        function editStaff(s) {
            document.getElementById('staff-id').value = s.staff_id;
            document.getElementById('staff-name').value = s.full_name;
            document.getElementById('staff-role').value = s.role;
            document.getElementById('staff-shift').value = s.shift;
            document.getElementById('staff-phone').value = s.phone;
            document.getElementById('staff-form-title').innerText = `Edit Staff #${s.staff_id}`;
        }

        function resetStaffForm() {
            document.getElementById('staff-form').reset();
            document.getElementById('staff-id').value = '';
            document.getElementById('staff-form-title').innerText = 'Add Staff Member';
        }

        function confirmDeleteStaff(id) {
            openConfirmModal('Delete Staff Record', `Delete staff member #${id}?`, async () => {
                await fetch(`/api/staff/${id}`, { method: 'DELETE' });
                showToast('Staff member deleted');
                loadStaff();
            });
        }

        // --- PHARMACY API ---
        let lowStockOnly = false;
        async function loadMedicines() {
            const url = lowStockOnly ? '/api/medicines?low_stock=1' : '/api/medicines';
            const res = await fetch(url);
            const data = await res.json();
            const tbody = document.getElementById('meds-table-body');
            tbody.innerHTML = data.map(m => {
                const isLow = m.stock_qty <= m.reorder_level;
                return `
                    <tr style="${isLow ? 'background-color: #fff1f2;' : ''}">
                        <td><strong>#${m.medicine_id}</strong></td>
                        <td>${m.name}</td>
                        <td><span class="badge badge-purple">${m.category}</span></td>
                        <td><strong>${m.stock_qty}</strong></td>
                        <td>₹${parseFloat(m.unit_price).toFixed(2)}</td>
                        <td>${m.reorder_level}</td>
                        <td><span class="badge ${isLow ? 'badge-danger' : 'badge-success'}">${isLow ? 'LOW STOCK' : 'Adequate'}</span></td>
                        <td>
                            <button class="btn btn-secondary btn-sm" onclick='editMed(${JSON.stringify(m)})'>Edit</button>
                            <button class="btn btn-danger btn-sm" onclick="confirmDeleteMed(${m.medicine_id})">Del</button>
                        </td>
                    </tr>
                `;
            }).join('');
        }

        function filterLowStock() {
            lowStockOnly = !lowStockOnly;
            loadMedicines();
            showToast(lowStockOnly ? 'Showing LOW STOCK medicines only' : 'Showing all medicines');
        }

        async function saveMedicine(e) {
            e.preventDefault();
            const id = document.getElementById('med-id').value;
            const payload = {
                name: document.getElementById('med-name').value,
                category: document.getElementById('med-category').value,
                stock_qty: parseInt(document.getElementById('med-stock').value),
                unit_price: parseFloat(document.getElementById('med-price').value),
                reorder_level: parseInt(document.getElementById('med-reorder').value)
            };
            const url = id ? `/api/medicines/${id}` : '/api/medicines';
            const method = id ? 'PUT' : 'POST';
            const res = await fetch(url, { method, headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload)});
            if (res.ok) {
                showToast('Medicine inventory updated');
                resetMedForm();
                loadMedicines();
                loadDashboardData();
            } else {
                showToast('Failed to save medicine', true);
            }
        }

        function editMed(m) {
            document.getElementById('med-id').value = m.medicine_id;
            document.getElementById('med-name').value = m.name;
            document.getElementById('med-category').value = m.category;
            document.getElementById('med-stock').value = m.stock_qty;
            document.getElementById('med-price').value = m.unit_price;
            document.getElementById('med-reorder').value = m.reorder_level;
            document.getElementById('med-form-title').innerText = `Edit Medicine #${m.medicine_id}`;
        }

        function resetMedForm() {
            document.getElementById('med-form').reset();
            document.getElementById('med-id').value = '';
            document.getElementById('med-reorder').value = '10';
            document.getElementById('med-form-title').innerText = 'Add Medicine';
        }

        function confirmDeleteMed(id) {
            openConfirmModal('Delete Medicine', `Delete medicine #${id} from pharmacy?`, async () => {
                await fetch(`/api/medicines/${id}`, { method: 'DELETE' });
                showToast('Medicine deleted');
                loadMedicines();
                loadDashboardData();
            });
        }

        // --- BILLING API ---
        function updateBillCalculatedTotal() {
            const room = parseFloat(document.getElementById('bill-room').value) || 0;
            const consult = parseFloat(document.getElementById('bill-consult').value) || 0;
            const med = parseFloat(document.getElementById('bill-med').value) || 0;
            const total = room + consult + med;
            document.getElementById('bill-calculated-total').innerText = `₹${total.toFixed(2)}`;
        }

        document.querySelectorAll('.calc-total').forEach(input => {
            input.addEventListener('input', updateBillCalculatedTotal);
        });

        async function loadBills() {
            const res = await fetch('/api/bills');
            const data = await res.json();
            const tbody = document.getElementById('bills-table-body');
            tbody.innerHTML = data.map(b => `
                <tr>
                    <td><strong>#${b.bill_id}</strong></td>
                    <td>${b.patient_name}</td>
                    <td>₹${parseFloat(b.room_charges).toFixed(2)}</td>
                    <td>₹${parseFloat(b.consultation_charges).toFixed(2)}</td>
                    <td>₹${parseFloat(b.medicine_charges).toFixed(2)}</td>
                    <td><strong>₹${parseFloat(b.total_amount).toFixed(2)}</strong></td>
                    <td><span class="badge badge-info">${b.payment_method}</span></td>
                    <td><span class="badge ${b.payment_status === 'Paid' ? 'badge-success' : 'badge-warning'}">${b.payment_status}</span></td>
                    <td>
                        <button class="btn btn-secondary btn-sm" onclick="togglePaymentStatus(${b.bill_id}, '${b.payment_status}')">${b.payment_status === 'Paid' ? 'Mark Pending' : 'Mark Paid'}</button>
                        <button class="btn btn-danger btn-sm" onclick="confirmDeleteBill(${b.bill_id})">Del</button>
                    </td>
                </tr>
            `).join('');
        }

        async function togglePaymentStatus(id, currentStatus) {
            const newStatus = currentStatus === 'Paid' ? 'Pending' : 'Paid';
            await fetch(`/api/bills/${id}/status`, {
                method: 'PUT',
                headers: {'Content-Type':'application/json'},
                body: JSON.stringify({ payment_status: newStatus })
            });
            showToast(`Bill marked as ${newStatus}`);
            loadBills();
            loadDashboardData();
        }

        async function saveBill(e) {
            e.preventDefault();
            const patientId = document.getElementById('bill-patient-id').value;
            if (!patientId) {
                showToast('Please select a valid patient using auto-complete', true);
                return;
            }
            const payload = {
                patient_id: patientId,
                room_charges: parseFloat(document.getElementById('bill-room').value) || 0,
                consultation_charges: parseFloat(document.getElementById('bill-consult').value) || 0,
                medicine_charges: parseFloat(document.getElementById('bill-med').value) || 0,
                payment_method: document.getElementById('bill-method').value,
                payment_status: document.getElementById('bill-status').value
            };
            const res = await fetch('/api/bills', {
                method: 'POST',
                headers: {'Content-Type':'application/json'},
                body: JSON.stringify(payload)
            });
            if (res.ok) {
                showToast('Invoice generated successfully');
                resetBillForm();
                loadBills();
                loadDashboardData();
            } else {
                showToast('Failed to generate invoice', true);
            }
        }

        function resetBillForm() {
            document.getElementById('bill-form').reset();
            document.getElementById('bill-patient-id').value = '';
            document.getElementById('bill-consult').value = '500';
            updateBillCalculatedTotal();
        }

        function confirmDeleteBill(id) {
            openConfirmModal('Delete Invoice', `Are you sure you want to delete invoice #${id}?`, async () => {
                await fetch(`/api/bills/${id}`, { method: 'DELETE' });
                showToast('Invoice deleted');
                loadBills();
                loadDashboardData();
            });
        }

        // --- AUDIT LOG API ---
        async function loadAuditLogs() {
            const res = await fetch('/api/audit');
            const data = await res.json();
            const tbody = document.getElementById('audit-table-body');
            tbody.innerHTML = data.map(a => `
                <tr>
                    <td><strong>#${a.log_id}</strong></td>
                    <td>${a.timestamp}</td>
                    <td><code>${a.table_name}</code></td>
                    <td>${a.record_id || '-'}</td>
                    <td><span class="badge ${a.action === 'INSERT' ? 'badge-success' : a.action === 'UPDATE' ? 'badge-warning' : 'badge-danger'}">${a.action}</span></td>
                    <td>${a.details || '-'}</td>
                    <td>${a.performed_by}</td>
                </tr>
            `).join('');
        }

        // --- DEFECT CHECKSHEET API ---
        async function loadDefects() {
            const res = await fetch('/api/defects');
            const data = await res.json();
            const tbody = document.getElementById('defects-table-body');
            tbody.innerHTML = data.map(d => `
                <tr>
                    <td><strong>#${d.defect_id}</strong></td>
                    <td>${d.logged_at}</td>
                    <td><span class="badge badge-purple">${d.category}</span></td>
                    <td><span class="badge ${d.severity === 'Critical' ? 'badge-danger' : d.severity === 'High' ? 'badge-warning' : 'badge-info'}">${d.severity}</span></td>
                    <td><span class="badge badge-warning">${d.status}</span></td>
                    <td>${d.description}</td>
                </tr>
            `).join('');
        }

        async function saveDefect(e) {
            e.preventDefault();
            const payload = {
                category: document.getElementById('defect-category').value,
                severity: document.getElementById('defect-severity').value,
                description: document.getElementById('defect-desc').value
            };
            const res = await fetch('/api/defects', {
                method: 'POST',
                headers: {'Content-Type':'application/json'},
                body: JSON.stringify(payload)
            });
            if (res.ok) {
                showToast('Defect logged on SQC checksheet');
                document.getElementById('defect-form').reset();
                loadDefects();
            } else {
                showToast('Failed to log defect', true);
            }
        }

        // Initial setup on window load
        window.addEventListener('DOMContentLoaded', () => {
            setupPhoneMasking();
            
            // Setup patient auto-complete for appointment tab
            setupAutocomplete(
                document.getElementById('appt-patient-name'),
                document.getElementById('patient-autocomplete-box'),
                '/api/patients/autocomplete',
                (item) => {
                    document.getElementById('appt-patient-id').value = item.id;
                }
            );

            // Setup patient auto-complete for billing tab
            setupAutocomplete(
                document.getElementById('bill-patient-name'),
                document.getElementById('bill-patient-autocomplete'),
                '/api/patients/autocomplete',
                (item) => {
                    document.getElementById('bill-patient-id').value = item.id;
                }
            );

            // Load initial view
            loadDashboardData();
        });
    </script>
</body>
</html>
"""

# ================= FLASK ROUTES & REST APIS =================

@app.route("/")
def index():
    return render_template_string(
        HTML_TEMPLATE,
        title=APP_TITLE,
        genders=GENDERS,
        blood_groups=BLOOD_GROUPS,
        departments=DEPARTMENTS,
        appt_statuses=APPT_STATUS,
        room_types=ROOM_TYPES,
        room_statuses=ROOM_STATUS,
        staff_roles=STAFF_ROLES,
        shifts=SHIFTS,
        payment_methods=PAYMENT_METHODS,
        payment_statuses=PAYMENT_STATUS,
        medicine_categories=MEDICINE_CATEGORIES,
        defect_categories=DEFECT_CATEGORIES,
        defect_severities=DEFECT_SEVERITY,
        defect_statuses=DEFECT_STATUS
    )

# --- DASHBOARD STATS ---
@app.route("/api/dashboard/stats")
def dashboard_stats():
    conn = get_connection()
    tot_patients = conn.execute("SELECT COUNT(*) AS c FROM patients").fetchone()["c"]
    tot_doctors = conn.execute("SELECT COUNT(*) AS c FROM doctors").fetchone()["c"]
    scheduled_appts = conn.execute("SELECT COUNT(*) AS c FROM appointments WHERE status='Scheduled'").fetchone()["c"]
    avail_rooms = conn.execute("SELECT COUNT(*) AS c FROM rooms WHERE status='Available'").fetchone()["c"]
    low_stock_meds = conn.execute("SELECT COUNT(*) AS c FROM medicines WHERE stock_qty <= reorder_level").fetchone()["c"]
    rev_row = conn.execute("SELECT SUM(total_amount) AS rev FROM bills WHERE payment_status='Paid'").fetchone()
    total_rev = rev_row["rev"] if rev_row["rev"] else 0.0
    recent_audit = conn.execute("SELECT * FROM audit_log ORDER BY log_id DESC LIMIT 10").fetchall()
    conn.close()

    return jsonify({
        "total_patients": tot_patients,
        "total_doctors": tot_doctors,
        "scheduled_appts": scheduled_appts,
        "available_rooms": avail_rooms,
        "low_stock_meds": low_stock_meds,
        "total_revenue": total_rev,
        "recent_audit": rows_to_list(recent_audit)
    })

# --- PATIENTS ENDPOINTS ---
@app.route("/api/patients", methods=["GET"])
def get_patients():
    q = request.args.get("q", "").strip()
    return jsonify(rows_to_list(patient_model.list_all(q)))

@app.route("/api/patients/autocomplete", methods=["GET"])
def autocomplete_patients():
    prefix = request.args.get("prefix", "").strip()
    conn = get_connection()
    rows = conn.execute("SELECT patient_id, full_name, phone FROM patients WHERE full_name LIKE ? LIMIT 8", (f"{prefix}%",)).fetchall()
    conn.close()
    return jsonify([{"id": r["patient_id"], "label": f"{r['full_name']} ({r['phone']})"} for r in rows])

@app.route("/api/patients", methods=["POST"])
def create_patient():
    data = request.json or {}
    name = data.get("full_name", "").strip()
    if not name:
        return jsonify({"error": "Full name is required"}), 400
    
    room_id = data.get("room_id")
    if room_id:
        room_id = int(room_id)
        # Update room status to Occupied
        conn = get_connection()
        conn.execute("UPDATE rooms SET status='Occupied' WHERE room_id=?", (room_id,))
        conn.commit()
        conn.close()

    new_id = patient_model.add(
        full_name=name,
        gender=data.get("gender", "Other"),
        dob=data.get("dob", ""),
        blood_group=data.get("blood_group", "O+"),
        phone=data.get("phone", ""),
        address=data.get("address", ""),
        room_id=room_id
    )
    return jsonify({"patient_id": new_id, "status": "created"}), 201

@app.route("/api/patients/<int:patient_id>", methods=["PUT"])
def update_patient(patient_id):
    data = request.json or {}
    room_id = data.get("room_id")
    room_id = int(room_id) if room_id else None
    
    patient_model.update(
        patient_id=patient_id,
        full_name=data.get("full_name"),
        gender=data.get("gender"),
        dob=data.get("dob"),
        blood_group=data.get("blood_group"),
        phone=data.get("phone"),
        address=data.get("address"),
        room_id=room_id
    )
    return jsonify({"status": "updated"})

@app.route("/api/patients/<int:patient_id>", methods=["DELETE"])
def delete_patient(patient_id):
    patient_model.delete(patient_id)
    return jsonify({"status": "deleted"})

# --- DOCTORS ENDPOINTS ---
@app.route("/api/doctors", methods=["GET"])
def get_doctors():
    return jsonify(rows_to_list(doctor_model.list_all()))

@app.route("/api/doctors/choices", methods=["GET"])
def get_doctor_choices():
    cmap = doctor_model.choices_map()
    return jsonify([{"id": v, "label": k} for k, v in cmap.items()])

@app.route("/api/doctors", methods=["POST"])
def create_doctor():
    data = request.json or {}
    new_id = doctor_model.add(
        full_name=data.get("full_name"),
        department=data.get("department"),
        phone=data.get("phone")
    )
    return jsonify({"doctor_id": new_id, "status": "created"}), 201

@app.route("/api/doctors/<int:doctor_id>", methods=["PUT"])
def update_doctor(doctor_id):
    data = request.json or {}
    doctor_model.update(
        doctor_id=doctor_id,
        full_name=data.get("full_name"),
        department=data.get("department"),
        phone=data.get("phone")
    )
    return jsonify({"status": "updated"})

@app.route("/api/doctors/<int:doctor_id>", methods=["DELETE"])
def delete_doctor(doctor_id):
    doctor_model.delete(doctor_id)
    return jsonify({"status": "deleted"})

# --- APPOINTMENTS ENDPOINTS ---
@app.route("/api/appointments", methods=["GET"])
def get_appointments():
    return jsonify(rows_to_list(appointment_model.list_all()))

@app.route("/api/appointments", methods=["POST"])
def create_appointment():
    data = request.json or {}
    new_id = appointment_model.add(
        patient_id=int(data.get("patient_id")),
        doctor_id=int(data.get("doctor_id")),
        appt_date=data.get("appt_date"),
        appt_time=data.get("appt_time"),
        status=data.get("status", "Scheduled")
    )
    return jsonify({"appointment_id": new_id, "status": "created"}), 201

@app.route("/api/appointments/<int:appointment_id>", methods=["PUT"])
def update_appointment(appointment_id):
    data = request.json or {}
    appointment_model.update(
        appointment_id=appointment_id,
        patient_id=int(data.get("patient_id")),
        doctor_id=int(data.get("doctor_id")),
        appt_date=data.get("appt_date"),
        appt_time=data.get("appt_time"),
        status=data.get("status")
    )
    return jsonify({"status": "updated"})

@app.route("/api/appointments/<int:appointment_id>", methods=["DELETE"])
def delete_appointment(appointment_id):
    appointment_model.delete(appointment_id)
    return jsonify({"status": "deleted"})

# --- ROOMS ENDPOINTS ---
@app.route("/api/rooms", methods=["GET"])
def get_rooms():
    return jsonify(rows_to_list(room_model.list_all()))

@app.route("/api/rooms/choices", methods=["GET"])
def get_room_choices():
    avail_only = request.args.get("available_only", "0") == "1"
    cmap = room_model.choices_map(only_available=avail_only)
    return jsonify([{"id": v, "label": k} for k, v in cmap.items()])

@app.route("/api/rooms", methods=["POST"])
def create_room():
    data = request.json or {}
    new_id = room_model.add(
        room_number=data.get("room_number"),
        room_type=data.get("room_type"),
        status=data.get("status", "Available"),
        rate_per_day=float(data.get("rate_per_day", 0))
    )
    return jsonify({"room_id": new_id, "status": "created"}), 201

@app.route("/api/rooms/<int:room_id>", methods=["PUT"])
def update_room(room_id):
    data = request.json or {}
    room_model.update(
        room_id=room_id,
        room_number=data.get("room_number"),
        room_type=data.get("room_type"),
        status=data.get("status"),
        rate_per_day=float(data.get("rate_per_day", 0))
    )
    return jsonify({"status": "updated"})

@app.route("/api/rooms/<int:room_id>", methods=["DELETE"])
def delete_room(room_id):
    room_model.delete(room_id)
    return jsonify({"status": "deleted"})

# --- STAFF ENDPOINTS ---
@app.route("/api/staff", methods=["GET"])
def get_staff():
    return jsonify(rows_to_list(staff_model.list_all()))

@app.route("/api/staff", methods=["POST"])
def create_staff():
    data = request.json or {}
    new_id = staff_model.add(
        full_name=data.get("full_name"),
        role=data.get("role"),
        shift=data.get("shift"),
        phone=data.get("phone")
    )
    return jsonify({"staff_id": new_id, "status": "created"}), 201

@app.route("/api/staff/<int:staff_id>", methods=["PUT"])
def update_staff(staff_id):
    data = request.json or {}
    staff_model.update(
        staff_id=staff_id,
        full_name=data.get("full_name"),
        role=data.get("role"),
        shift=data.get("shift"),
        phone=data.get("phone")
    )
    return jsonify({"status": "updated"})

@app.route("/api/staff/<int:staff_id>", methods=["DELETE"])
def delete_staff(staff_id):
    staff_model.delete(staff_id)
    return jsonify({"status": "deleted"})

# --- MEDICINES / PHARMACY ENDPOINTS ---
@app.route("/api/medicines", methods=["GET"])
def get_medicines():
    low_stock = request.args.get("low_stock", "0") == "1"
    if low_stock:
        rows = medicine_model.low_stock()
    else:
        rows = medicine_model.list_all()
    return jsonify(rows_to_list(rows))

@app.route("/api/medicines", methods=["POST"])
def create_medicine():
    data = request.json or {}
    new_id = medicine_model.add(
        name=data.get("name"),
        category=data.get("category"),
        stock_qty=int(data.get("stock_qty", 0)),
        unit_price=float(data.get("unit_price", 0)),
        reorder_level=int(data.get("reorder_level", 10))
    )
    return jsonify({"medicine_id": new_id, "status": "created"}), 201

@app.route("/api/medicines/<int:medicine_id>", methods=["PUT"])
def update_medicine(medicine_id):
    data = request.json or {}
    medicine_model.update(
        medicine_id=medicine_id,
        name=data.get("name"),
        category=data.get("category"),
        stock_qty=int(data.get("stock_qty", 0)),
        unit_price=float(data.get("unit_price", 0)),
        reorder_level=int(data.get("reorder_level", 10))
    )
    return jsonify({"status": "updated"})

@app.route("/api/medicines/<int:medicine_id>", methods=["DELETE"])
def delete_medicine(medicine_id):
    medicine_model.delete(medicine_id)
    return jsonify({"status": "deleted"})

# --- BILLS ENDPOINTS ---
@app.route("/api/bills", methods=["GET"])
def get_bills():
    return jsonify(rows_to_list(bill_model.list_all()))

@app.route("/api/bills", methods=["POST"])
def create_bill():
    data = request.json or {}
    new_id, total = bill_model.add(
        patient_id=int(data.get("patient_id")),
        room_charges=float(data.get("room_charges", 0)),
        consultation_charges=float(data.get("consultation_charges", 0)),
        medicine_charges=float(data.get("medicine_charges", 0)),
        payment_method=data.get("payment_method", "Cash"),
        payment_status=data.get("payment_status", "Paid")
    )
    return jsonify({"bill_id": new_id, "total": total, "status": "created"}), 201

@app.route("/api/bills/<int:bill_id>/status", methods=["PUT"])
def update_bill_status(bill_id):
    data = request.json or {}
    bill_model.update_status(bill_id, data.get("payment_status", "Paid"))
    return jsonify({"status": "updated"})

@app.route("/api/bills/<int:bill_id>", methods=["DELETE"])
def delete_bill(bill_id):
    bill_model.delete(bill_id)
    return jsonify({"status": "deleted"})

# --- AUDIT ENDPOINTS ---
@app.route("/api/audit", methods=["GET"])
def get_audit():
    return jsonify(rows_to_list(audit_model.list_audit(limit=200)))

# --- DEFECTS ENDPOINTS ---
@app.route("/api/defects", methods=["GET"])
def get_defects():
    return jsonify(rows_to_list(audit_model.list_defects()))

@app.route("/api/defects", methods=["POST"])
def create_defect():
    data = request.json or {}
    audit_model.add_defect(
        category=data.get("category"),
        description=data.get("description"),
        severity=data.get("severity")
    )
    return jsonify({"status": "created"}), 201


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
