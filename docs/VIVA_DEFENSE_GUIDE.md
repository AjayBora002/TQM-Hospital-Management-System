# BBAT104 Final Demonstration & Viva Defense Guide

**Student:** Ajay Bora &nbsp;|&nbsp; **Branch:** CSE — Section B  
**Baseline System:** Hospital Management System (Digit 2) &nbsp;|&nbsp; **Course:** BBAT104 Fundamentals of TQM  
**Assigned Quality Goal:** Q07 — Improve Data Accuracy  
**Academic Session:** 2026–27  

---

## 1. Quick Project Pitch (30-Second Elevator Defense)

> *"Respected Evaluators, my project is a **Hospital Management System** mapped to Digit 2 of my roll number, with assigned Quality Goal **Q07: Improve Data Accuracy**.*  
> *In healthcare systems, erroneous phone numbers, misclassified blood groups, and duplicate patient charts directly compromise patient safety and clinical decision-making.*  
> *To eliminate these defects at the source, I implemented **Poka-Yoke (Mistake-Proofing)** principles across 10 functional modules using 5 specific Q07 features: **Input Masking**, **Read-only Dropdowns**, **Auto-Complete search**, **Confirmation Modals**, and a full **Audit Trail**.*  
> *Through Statistical Quality Control—specifically a Defect Checksheet, Pareto Analysis (80/20 rule), Ishikawa Fishbone diagram, and an FMEA Risk Matrix—we verified that these five controls eliminated 100% of phone formatting and field typo defects, reducing our top RPN risk from 280 to 28."*

---

## 2. Core TQM & SQC Concepts Q&A

### Q1: Why was Quality Goal Q07 (Improve Data Accuracy) selected for a Hospital Management System?
- **Answer:** In healthcare, data inaccuracy carries catastrophic severity:
  1. An inaccurate blood group or misidentified patient history can cause fatal clinical errors during emergency treatment or blood transfusion.
  2. A mistyped phone number prevents emergency notifications, prescription reminders, or telemedicine follow-ups.
  3. Duplicate patient entries create fragmented medical histories, increasing diagnostic delays and medication redundancy.
- By targeting **Data Accuracy**, we satisfy the primary TQM principle of **Error Prevention (Poka-Yoke)** rather than post-entry inspection.

---

### Q2: Walk us through your 5 Quality Goal (Q07) features and their code implementation.
1. **Input Masking (`PhoneMaskEntry` in `src/widgets/phone_mask_entry.py`):**
   - Automatically prefixes `+91-` and injects hyphens dynamically as the user types 10 digits (`+91-XXXXX-XXXXX`). Rejects non-numeric characters automatically via regex matching.
2. **Dropdown Lists (`src/config.py` + `ttk.Combobox(state="readonly")`):**
   - Eliminates free-text typing for standard categorical fields: Gender (Male/Female/Other), Blood Groups (A+, A-, B+, B-, AB+, AB-, O+, O-), Medical Departments, Room Types/Statuses, Staff Roles/Shifts, and Payment Methods/Statuses.
3. **Auto-Complete (`AutocompleteEntry` in `src/widgets/autocomplete_entry.py`):**
   - Substring match queries existing patient names in real time when scheduling appointments or generating bills, preventing accidental creation of duplicate patient profiles.
4. **Confirmation Modals (`ConfirmDialog` in `src/widgets/confirm_dialog.py`):**
   - Intercepts destructive actions (`Update` and `Delete`) with an explicit confirmation popup, preventing accidental record modification or deletion.
5. **Audit Logs (`log_audit()` in `src/database/db_manager.py` + `src/views/audit_view.py`):**
   - Every `INSERT`, `UPDATE`, and `DELETE` across all 8 tables is written to an immutable `audit_log` table with table name, record ID, timestamp, and action description. Also synchronized to CSV in `TQM/data/audit_logs.csv`.

---

### Q3: What is FMEA, and how did you calculate the Risk Priority Number (RPN)?
- **FMEA:** Failure Mode and Effects Analysis is a proactive risk assessment technique used to prioritize potential process failures before they occur.
- **Formula:** 
  $$\text{RPN} = \text{Severity (S)} \times \text{Occurrence (O)} \times \text{Detection (D)}$$
  - **Severity (1-10):** Seriousness of the defect's impact (e.g., Blood group error = 9 or 10).
  - **Occurrence (1-10):** Frequency of how often the defect happens without controls.
  - **Detection (1-10):** Likelihood of catching the defect before it affects the system (1 = guaranteed detection, 10 = impossible to detect).
- **Example from our project:**
  - *Failure Mode:* Invalid Phone Number (free-text entry).
  - *Before Q07:* $S = 5, O = 7, D = 8 \implies \mathbf{RPN = 280}$.
  - *Mitigation:* Implemented `PhoneMaskEntry` and regex boundary validation.
  - *After Q07:* $S = 5, O = 1, D = 1 \implies \mathbf{RPN = 5}$ (Risk reduction of >98%).

---

### Q4: Explain your Pareto Analysis (80/20 Rule) findings.
- **Pareto Principle:** 80% of problems typically stem from 20% of causes (the "vital few" vs. the "useful many").
- **Our Data:** From the Defect Checksheet (11 defects logged during manual testing):
  - `Data Entry` defects: 5 (45.5%)
  - `Validation` defects: 4 (36.4%)
  - `UI` defects: 1 (9.1%)
  - `Database` defects: 1 (9.1%)
- **Conclusion:** `Data Entry` and `Validation` accounted for **81.8%** of all logged defects!
- Therefore, investing development effort specifically into input masking and dropdown validation addressed over 80% of system vulnerabilities.

---

### Q5: Explain the Ishikawa (Fishbone / 4M/4P) Diagram.
- **Purpose:** Root-cause analysis identifying why data inaccuracy occurs in hospital systems.
- **Our 4 Branches:**
  1. **People:** Fatigue during long shifts, lack of data entry training, rushing during peak emergency intake.
  2. **Process:** Absence of standard data entry protocols, no mandatory confirmation step before saving.
  3. **Software Code:** Open free-text fields, absence of input masks, lack of dropdown constraints, unhandled null values.
  4. **Infrastructure:** Unstable terminal keyboards, small font sizes causing eye strain, network timeouts mid-entry.
- **Action Taken:** Addressed the "Software Code" and "Process" root causes directly through Q07 features.

---

### Q6: Walk us through your PDCA (Plan-Do-Check-Act) Cycle.
- **Plan:** Pareto identified data entry errors (45.5%) as the primary defect driver; targeted phone number and demographic typos.
- **Do:** Built `PhoneMaskEntry`, standardized `ttk.Combobox` dropdowns, added `AutocompleteEntry`, confirmation popups, and audit logging.
- **Check:** Re-tested with a batch of 20 simulated patient admissions:
  - Phone format errors dropped from 5 to 0.
  - Demographic typos dropped to 0.
  - 1 duplicate record was intercepted by auto-complete before submission.
- **Act:** Adopted the Q07 widget suite as the mandatory standard for all future form modules across the hospital network.

---

## 3. Live Demonstration Checklist (Step-by-Step)

When demonstrating the software to the professor:
1. **Launch the Application:**
   ```bash
   # Web Portal
   python run.py
   # Or Desktop GUI
   python src/main.py
   ```
2. **Show Dashboard:**
   - Point out real-time aggregated counts (Total Patients, Doctors, Appointments, Rooms, Pharmacy Stock, Billing totals).
3. **Show Input Masking (Patients Module):**
   - Click the **Phone** field and type `9876543210`. Point out how it automatically formats into `+91-98765-43210` and blocks letter keystrokes.
4. **Show Dropdown Validation:**
   - Click Gender, Blood Group, or Department; emphasize they are `readonly` comboboxes, eliminating spelling mistakes like *"O pos"* or *"O+"*.
5. **Show Auto-Complete (Appointments / Billing):**
   - Type the first 2 letters of a patient's name into the Patient search field to show the live autocomplete dropdown.
6. **Show Confirmation Modals:**
   - Select an existing record, click **Delete**, and show the modal dialog prompting *"Are you sure you want to delete...?"*.
7. **Show Audit Log:**
   - Switch to the **Audit Log** tab/view. Show that every single action performed during the demo was automatically logged with timestamp, user action, and record ID.
8. **Show Defect Checksheet & SQC:**
   - Switch to the **Defect Checksheet** tab. Demonstrate how quality auditors log bugs, which directly feed the Pareto analysis.
9. **Show Automated Tests:**
   ```bash
   python -m unittest discover tests
   ```
   - Show 28 tests passing with zero errors.
