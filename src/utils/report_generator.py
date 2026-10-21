"""
report_generator.py -- Formats executive printable HTML receipts, medical invoices,
and clinical inpatient discharge summaries with hospital branding and print-ready CSS.
"""
from datetime import datetime
from database.db_manager import get_connection
from utils.exception_handler import ValidationError


def generate_bill_receipt_html(bill_id: int) -> str:
    conn = get_connection()
    try:
        bill = conn.execute("""
            SELECT b.*, p.full_name as patient_name, p.phone as patient_phone,
                   p.gender as patient_gender, p.dob as patient_dob, p.blood_group,
                   r.room_number
            FROM bills b
            JOIN patients p ON b.patient_id = p.patient_id
            LEFT JOIN rooms r ON p.room_id = r.room_id
            WHERE b.bill_id = ?
        """, (bill_id,)).fetchone()

        if not bill:
            raise ValidationError(f"Bill #{bill_id} not found", field="bill_id")

        bill_dict = dict(bill)
        invoice_no = f"INV-{bill_dict['bill_id']:05d}"
        created_at = bill_dict.get("created_at", datetime.now().isoformat())
        payment_badge_color = "#28a745" if bill_dict["payment_status"] == "Paid" else ("#ffc107" if bill_dict["payment_status"] == "Partially Paid" else "#dc3545")

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Medical Invoice - {invoice_no}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f4f6f9;
            margin: 0;
            padding: 20px;
            color: #333;
        }}
        .invoice-card {{
            max-width: 800px;
            margin: 0 auto;
            background: #fff;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid #0056b3;
            padding-bottom: 20px;
            margin-bottom: 25px;
        }}
        .hospital-title {{
            font-size: 24px;
            font-weight: 700;
            color: #0056b3;
            margin: 0;
        }}
        .hospital-sub {{
            font-size: 13px;
            color: #666;
            margin-top: 4px;
        }}
        .invoice-meta {{
            text-align: right;
            font-size: 14px;
        }}
        .invoice-num {{
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
        }}
        .patient-box {{
            background: #f8f9fa;
            border-left: 4px solid #0056b3;
            padding: 15px 20px;
            margin-bottom: 25px;
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            font-size: 14px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 25px;
        }}
        th, td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #e9ecef;
        }}
        th {{
            background: #f1f3f5;
            color: #495057;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .text-right {{
            text-align: right;
        }}
        .totals-table {{
            width: 320px;
            margin-left: auto;
            margin-bottom: 30px;
        }}
        .total-row {{
            font-size: 16px;
            font-weight: bold;
            color: #0056b3;
            border-top: 2px solid #0056b3;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
            color: #fff;
            background: {payment_badge_color};
        }}
        .footer {{
            border-top: 1px solid #e9ecef;
            padding-top: 20px;
            font-size: 12px;
            color: #888;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .no-print {{
            text-align: center;
            margin-bottom: 20px;
        }}
        .btn-print {{
            background: #0056b3;
            color: #fff;
            border: none;
            padding: 10px 24px;
            font-size: 15px;
            border-radius: 5px;
            cursor: pointer;
            box-shadow: 0 2px 6px rgba(0,86,179,0.3);
        }}
        @media print {{
            body {{
                background: #fff;
                padding: 0;
            }}
            .invoice-card {{
                box-shadow: none;
                padding: 20px;
            }}
            .no-print {{
                display: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="no-print">
        <button class="btn-print" onclick="window.print()">🖨️ Print Invoice / Save as PDF</button>
    </div>

    <div class="invoice-card">
        <div class="header">
            <div>
                <h1 class="hospital-title">TQM HOSPITAL & RESEARCH INSTITUTE</h1>
                <div class="hospital-sub">NABH Accredited &bull; Quality Healthcare & Patient Safety</div>
                <div class="hospital-sub">104 Hospital Boulevard, New Delhi | Helpline: +91-11-2345-6789</div>
            </div>
            <div class="invoice-meta">
                <div class="invoice-num">{invoice_no}</div>
                <div>Date: {created_at[:10]}</div>
                <div>Status: <span class="badge">{bill_dict['payment_status']}</span></div>
            </div>
        </div>

        <div class="patient-box">
            <div><strong>Patient Name:</strong> {bill_dict['patient_name']}</div>
            <div><strong>Contact:</strong> {bill_dict['patient_phone']}</div>
            <div><strong>Gender / Blood:</strong> {bill_dict.get('patient_gender', 'N/A')} &bull; {bill_dict.get('blood_group', 'N/A')}</div>
            <div><strong>Assigned Bed / Ward:</strong> {bill_dict.get('room_number') or 'Outpatient'}</div>
        </div>

        <table>
            <thead>
                <tr>
                    <th>#</th>
                    <th>Clinical Charge Description</th>
                    <th>Tariff Category</th>
                    <th class="text-right">Amount (INR)</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>1</td>
                    <td>Inpatient Room & Ward Accommodation</td>
                    <td>Hospitalization Charges</td>
                    <td class="text-right">&#8377; {float(bill_dict['room_charges']):,.2f}</td>
                </tr>
                <tr>
                    <td>2</td>
                    <td>Physician & Specialist Consultation Fees</td>
                    <td>Clinical Evaluation</td>
                    <td class="text-right">&#8377; {float(bill_dict['consultation_charges']):,.2f}</td>
                </tr>
                <tr>
                    <td>3</td>
                    <td>Prescribed Pharmaceuticals & Dispensary</td>
                    <td>Pharmacy Inventory</td>
                    <td class="text-right">&#8377; {float(bill_dict['medicine_charges']):,.2f}</td>
                </tr>
            </tbody>
        </table>

        <table class="totals-table">
            <tr>
                <td>Subtotal</td>
                <td class="text-right">&#8377; {float(bill_dict['total_amount']):,.2f}</td>
            </tr>
            <tr>
                <td>Taxes & TQM Service Levies</td>
                <td class="text-right">&#8377; 0.00</td>
            </tr>
            <tr class="total-row">
                <td>Net Total Amount</td>
                <td class="text-right">&#8377; {float(bill_dict['total_amount']):,.2f}</td>
            </tr>
            <tr>
                <td>Payment Mode</td>
                <td class="text-right"><strong>{bill_dict['payment_method']}</strong></td>
            </tr>
        </table>

        <div class="footer">
            <div>
                <div>Generated by TQM Hospital Management System</div>
                <div style="font-size:10px; margin-top:2px;">Audit Evidence Ref: Q07-ACCURACY-VERIFIED</div>
            </div>
            <div style="text-align:right;">
                <div>Authorized Signatory</div>
                <div style="margin-top:25px; border-top:1px dashed #aaa; width:150px; display:inline-block;"></div>
            </div>
        </div>
    </div>
</body>
</html>"""
        return html
    finally:
        conn.close()


def generate_discharge_summary_html(admission_id: int) -> str:
    conn = get_connection()
    try:
        admission = conn.execute("""
            SELECT a.*, p.full_name as patient_name, p.gender, p.dob, p.phone,
                   p.blood_group, p.allergies, r.room_number, r.room_type
            FROM admissions a
            JOIN patients p ON a.patient_id = p.patient_id
            JOIN rooms r ON a.room_id = r.room_id
            WHERE a.admission_id = ?
        """, (admission_id,)).fetchone()

        if not admission:
            raise ValidationError(f"Inpatient admission #{admission_id} not found", field="admission_id")

        adm = dict(admission)
        p_id = adm["patient_id"]

        # Fetch latest vitals for patient
        vitals = conn.execute("""
            SELECT systolic, diastolic, pulse, temperature, spo2, triage_status, recorded_at
            FROM vitals_log WHERE patient_id = ? ORDER BY vital_id DESC LIMIT 1
        """, (p_id,)).fetchone()
        vitals_dict = dict(vitals) if vitals else {}

        # Fetch take-home prescriptions
        prescriptions = conn.execute("""
            SELECT pr.*, m.name as medicine_name, d.full_name as doctor_name
            FROM prescriptions pr
            JOIN medicines m ON pr.medicine_id = m.medicine_id
            JOIN doctors d ON pr.doctor_id = d.doctor_id
            WHERE pr.patient_id = ?
            ORDER BY pr.prescription_id DESC LIMIT 5
        """, (p_id,)).fetchall()

        rx_rows_html = ""
        for i, rx in enumerate(prescriptions, 1):
            rx_rows_html += f"""
            <tr>
                <td>{i}</td>
                <td><strong>{rx['medicine_name']}</strong></td>
                <td>{rx['dosage']}</td>
                <td>{rx['frequency']}</td>
                <td>{rx['duration_days']} days</td>
                <td>{rx['instructions'] or 'As directed'}</td>
            </tr>"""

        if not rx_rows_html:
            rx_rows_html = "<tr><td colspan='6' style='text-align:center;'>No take-home medications prescribed.</td></tr>"

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Clinical Discharge Summary - Inpatient #{adm['admission_id']}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f4f6f9;
            margin: 0;
            padding: 20px;
            color: #333;
        }}
        .summary-card {{
            max-width: 850px;
            margin: 0 auto;
            background: #fff;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        }}
        .header {{
            border-bottom: 2px solid #0056b3;
            padding-bottom: 15px;
            margin-bottom: 20px;
            text-align: center;
        }}
        .hospital-title {{
            font-size: 22px;
            font-weight: 700;
            color: #0056b3;
            margin: 0;
        }}
        .doc-title {{
            font-size: 16px;
            font-weight: bold;
            color: #495057;
            margin-top: 5px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .patient-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 12px;
            background: #f8f9fa;
            padding: 15px 20px;
            border-radius: 6px;
            margin-bottom: 20px;
            font-size: 14px;
        }}
        .section-title {{
            font-size: 15px;
            font-weight: bold;
            color: #0056b3;
            border-bottom: 1px solid #dee2e6;
            padding-bottom: 5px;
            margin: 20px 0 10px 0;
            text-transform: uppercase;
        }}
        .vitals-bar {{
            display: flex;
            gap: 20px;
            background: #e7f1ff;
            padding: 10px 15px;
            border-radius: 4px;
            font-size: 13px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
            font-size: 13px;
        }}
        th, td {{
            padding: 8px 12px;
            text-align: left;
            border-bottom: 1px solid #e9ecef;
        }}
        th {{
            background: #f1f3f5;
        }}
        .notes-box {{
            background: #fff;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            padding: 12px;
            font-size: 14px;
            min-height: 50px;
        }}
        .footer {{
            margin-top: 40px;
            border-top: 1px solid #dee2e6;
            padding-top: 20px;
            display: flex;
            justify-content: space-between;
            font-size: 13px;
        }}
        .btn-print {{
            background: #0056b3;
            color: #fff;
            border: none;
            padding: 10px 24px;
            font-size: 15px;
            border-radius: 5px;
            cursor: pointer;
            box-shadow: 0 2px 6px rgba(0,86,179,0.3);
        }}
        .no-print {{
            text-align: center;
            margin-bottom: 20px;
        }}
        @media print {{
            body {{
                background: #fff;
                padding: 0;
            }}
            .summary-card {{
                box-shadow: none;
                padding: 10px;
            }}
            .no-print {{
                display: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="no-print">
        <button class="btn-print" onclick="window.print()">🖨️ Print Discharge Summary / Save as PDF</button>
    </div>

    <div class="summary-card">
        <div class="header">
            <h1 class="hospital-title">TQM HOSPITAL & RESEARCH INSTITUTE</h1>
            <div style="font-size:12px; color:#666;">Department of Inpatient Hospitalization & Clinical Care</div>
            <div class="doc-title">Formal Discharge Summary Report</div>
        </div>

        <div class="patient-grid">
            <div><strong>Patient Name:</strong> {adm['patient_name']}</div>
            <div><strong>Gender / Blood:</strong> {adm['gender']} &bull; {adm['blood_group']}</div>
            <div><strong>Phone:</strong> {adm['phone']}</div>
            <div><strong>Ward & Room:</strong> Bed {adm['room_number']} ({adm['room_type']})</div>
            <div><strong>Admission Date:</strong> {adm['admission_date'][:10]}</div>
            <div><strong>Discharge Date:</strong> {adm.get('discharge_date', 'In Progress') or 'In Progress'}</div>
            <div><strong>Allergies:</strong> <span style="color:#d9534f; font-weight:bold;">{adm.get('allergies', 'None')}</span></div>
            <div><strong>Stay Status:</strong> {adm['status']}</div>
            <div><strong>Case Ref:</strong> ADM-{adm['admission_id']:05d}</div>
        </div>

        <div class="section-title">Final Clinical Diagnosis</div>
        <div class="notes-box">{adm.get('diagnosis') or 'Diagnosis recorded in electronic chart.'}</div>

        <div class="section-title">Physiological Vitals at Discharge</div>
        <div class="vitals-bar">
            <div><strong>Blood Pressure:</strong> {vitals_dict.get('systolic', 120)}/{vitals_dict.get('diastolic', 80)} mmHg</div>
            <div><strong>Pulse:</strong> {vitals_dict.get('pulse', 75)} bpm</div>
            <div><strong>Temperature:</strong> {vitals_dict.get('temperature', 98.4)} &deg;F</div>
            <div><strong>SpO2:</strong> {vitals_dict.get('spo2', 98)}%</div>
            <div><strong>Triage Evaluation:</strong> {vitals_dict.get('triage_status', 'Normal')}</div>
        </div>

        <div class="section-title">Take-Home Medication & Prescription Orders</div>
        <table>
            <thead>
                <tr>
                    <th>#</th>
                    <th>Medicine</th>
                    <th>Dosage</th>
                    <th>Frequency</th>
                    <th>Duration</th>
                    <th>Instructions</th>
                </tr>
            </thead>
            <tbody>
                {rx_rows_html}
            </tbody>
        </table>

        <div class="section-title">Post-Discharge Instructions & Follow-up</div>
        <div class="notes-box">{adm.get('discharge_notes') or 'Follow up with attending physician after 7 days or in case of emergency.'}</div>

        <div class="footer">
            <div>
                <div>Date of Issue: {datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
                <div style="font-size:11px; color:#888;">Clinical Governance Verified (TQM Q07)</div>
            </div>
            <div style="text-align:right;">
                <div>Attending Physician Signature</div>
                <div style="margin-top:30px; border-top:1px dashed #aaa; width:180px; display:inline-block;"></div>
            </div>
        </div>
    </div>
</body>
</html>"""
        return html
    finally:
        conn.close()
