# Hospital Management System (HMS) - Role & Module RBAC Matrix

## 1. Overview & Architectural Principles

The Hospital Management System operates on a strict, server-enforced **Role-Based Access Control (RBAC)** model combined with **Row-Level & Field-Level Security** guards:

1. **Server-Side Enforcement**: Permissions are evaluated on every REST endpoint via the `@require_permission(module, action)` decorator. Client-side navigation hiding is strictly for user experience; invoking any restricted API directly returns `HTTP 403 Forbidden` and records an immutable entry into the system audit trail.
2. **Clinical Data Isolation**: Administrative and billing roles (`Admin`, `Hospital Manager`, `Cashier`, `Receptionist`) cannot create, edit, or tamper with clinical patient charts, diagnoses, or prescriptions.
3. **Patient Privacy & Break-Glass**: Patients have zero access to administrative, financial backend, or other patients' records; they access their personal health records via the dedicated Patient Health Portal. Doctors only access assigned encounters, with an auditable break-glass override.
4. **Synthetic Data Policy**: All patient demographic records, UHIDs (`UHID-2026-XXXXXX`), ABHA IDs, contact numbers (`+91-XXXXX-XXXXX`), and clinical encounters are 100% synthetic for education, testing, and compliance.

---

## 2. Complete 28-Role Permission & Navigation Matrix

| # | Role | Domain / Group | Default Landing Screen | Permitted Modules & Capabilities | Hard Restrictions / Forbidden Areas |
|---|------|----------------|------------------------|-----------------------------------|--------------------------------------|
| 1 | **Admin** | Administration | Dashboard (`#dashboard`) | Full administration, user management, audit trail inspection, system backup/restore, departments configuration, all operational view access. | **CANNOT edit or create clinical notes/prescriptions** (`clinical:create/edit/delete` hard-blocked). |
| 2 | **Hospital Manager** | Executive Leadership | Dashboard (`#dashboard`) | Executive KPI dashboard, operational oversight across all 59 departments, quality metrics, audit trail inspection, purchase order approval. | Cannot alter medical charts or prescribe medications. |
| 3 | **Doctor** | Clinical Care | EMR / SOAP Notes (`#emr`) | Outpatient encounters, clinical SOAP notes, electronic prescriptions, lab order entry, triage review, telemedicine, dialysis, maternity delivery records, vaccination. | Cannot modify validated lab reports, pharmacy inventory pricing, or hospital billing invoices. |
| 4 | **Nurse** | Inpatient Care | Nursing & MAR (`#nursing`) | Medication Administration Record (MAR), vitals entry, shift handover reports, bed availability board, housekeeping requests, maternity nursing care. | Cannot create/edit doctor prescriptions or discharge billing invoices. |
| 5 | **Ward Manager** | Inpatient Care | Bed Board Matrix (`#bedboard`) | Ward bed allocation, inter-ward bed transfers, consumable indents, ward maintenance ticketing, nursing roster oversight. | Cannot edit doctor clinical diagnoses or discharge patient financial accounts. |
| 6 | **Receptionist** | Front Office | OPD Queue & Tokens (`#queue`) | Patient UHID registration, appointment booking, OPD queue token issuance, visitor badge generation, health packages, referrals desk. | Cannot view clinical SOAP notes, lab test values, or pharmacy stock purchase costs. |
| 7 | **Lab Technician** | Diagnostics | Laboratory LIS (`#lab`) | Specimen intake, barcode verification, lab test result entry, turnaround time (TAT) monitoring, LIS report release. | Cannot edit prescriptions, change bed allocations, or process patient bills. |
| 8 | **Pharmacist** | Pharmacy & Supply | Rx Dispensing (`#dispensing`) | Prescription dispensing, medicine stock batches, expiration tracking, purchase orders, pharmacy returns & refund credits. | Cannot edit doctor diagnoses, alter room charges, or modify lab values. |
| 9 | **Cashier** | Finance | Invoices & Billing (`#billing`) | Inpatient/outpatient invoice generation, advance deposit receipts, payment reconciliation, financial reports. | Cannot view clinical notes, diagnosis text, or patient medical histories. |
| 10 | **Patient** | Patient Portal | My Health Portal (`#portal`) | View own appointments, personal e-prescriptions, released diagnostic lab reports, and billing statements. | Strictly limited to self-service portal; zero access to hospital backend or other patient data. |
| 11 | **Quality Manager** | Quality & Governance | Incidents & CAPA (`#capa`) | NABH clinical audits, defect checksheets, SPC/Six Sigma control charts, HAI infection surveillance, patient CSAT feedback, M&M reviews. | Cannot create/edit doctor prescriptions or invoice financial ledger entries. |
| 12 | **Radiologist** | Diagnostics | Radiology & PACS (`#radiology`) | Imaging order review, X-Ray / CT / MRI / USG report generation, PACS image viewer integration. | Cannot edit pharmacy inventory or clinical prescriptions. |
| 13 | **OT Manager** | Inpatient / Surgery | Operation Theatre (`#ot`) | Surgical suite scheduling, WHO surgical safety checklist verification, pre-op clearance tracking, PAC clearance. | Cannot write general outpatient prescriptions. |
| 14 | **Blood Bank Technician** | Diagnostics | Blood Bank (`#bloodbank`) | Donor intake registry, ABO/Rh grouping, cross-matching, blood component inventory (PRBC, FFP, Platelets). | Cannot modify patient hospital bills or pharmacy stock. |
| 15 | **Housekeeping Supervisor** | Support Services | Housekeeping (`#housekeeping`) | Room/bed terminal cleaning schedules, biohazard waste disposal tasks, sanitation checklists. | Zero access to clinical records, lab investigations, or billing data. |
| 16 | **Biomedical Engineer** | Support Services | Biomedical Assets (`#biomedical`) | Medical equipment asset tagging, planned preventive maintenance (PPM), calibration logs, breakdown repair tickets. | Cannot alter medical charts or patient billing. |
| 17 | **HR Manager** | People & HR | Staff Directory (`#staff`) | Staff employee profiles, duty shift rosters, staff leave applications, credentialing verification. | Cannot view clinical health records or modify patient accounts. |
| 18 | **Store/Inventory Manager** | Pharmacy & Supply | Central Stores (`#store`) | General stores consumables, purchase requisitions, stock bin management, ward distribution indents. | Cannot alter clinical prescriptions or patient bills. |
| 19 | **Insurance/TPA Desk** | Finance | Insurance / TPA (`#insurance`) | Cashless insurance pre-authorizations, claim document submission, TPA queries, claim settlement reconciliation. | Cannot edit clinical medical notes or write doctor orders. |
| 20 | **Ambulance Dispatcher** | Support Services | Ambulance Fleet (`#ambulance`) | Emergency ALS/BLS fleet tracking, vehicle trip dispatch, driver/paramedic roster, GPS telemetry monitoring. | Cannot access clinical records or patient billing accounts. |
| 21 | **Dietitian** | Support Services | Diet & Nutrition (`#dietetics`) | Clinical nutrition assessment, therapeutic diet prescribing (diabetic, renal, soft, NPO), kitchen meal production. | Cannot edit doctor drug prescriptions or billing ledgers. |
| 22 | **MRD Officer** | Clinical Support | Medical Records (`#mrd`) | Physical medical file archiving, ICD-10 coding classification, file loan & return tracking, statutory records preservation. | Cannot edit prescriptions, create hospital bills, or modify system users. |
| 23 | **Mortuary Attendant** | Support Services | Mortuary Register (`#mortuary`) | Decedent intake log, cold chamber cabinet assignment, forensic documentation, body release to authorized next-of-kin. | Cannot access clinical EMR or patient billing systems. |
| 24 | **CSSD Technician** | Support Services | CSSD Sterilization (`#cssd`) | Autoclave sterilization cycles, Bowie-Dick tests, Class 5/6 chemical indicators, sterile pack release to OT/wards. | Cannot edit patient medical records or billing accounts. |
| 25 | **Infection Control Nurse** | Quality & Governance | Infection Control (`#infection-control`) | Healthcare-Associated Infection (HAI) surveillance (CAUTI, CLABSI, VAP, SSI), isolation protocol flags, antimicrobial stewardship. | Cannot create patient bills or administrative user credentials. |
| 26 | **Physiotherapist** | Clinical Care | Physiotherapy (`#physiotherapy`) | Rehabilitation protocols, physical therapy session logs, functional mobility assessments, exercise scheduling. | Cannot edit doctor medication orders or process hospital invoices. |
| 27 | **Security Officer** | Support Services | Campus Security (`#security-log`) | Campus gate entry passes, visitor badge tracking, vehicle parking log, security incidents monitoring. | Zero access to clinical records, billing, or pharmacy stock. |
| 28 | **Telemedicine Doctor** | Clinical Care | Telemedicine (`#telemedicine`) | Virtual video consultations, tele-triage, digital e-prescriptions, remote patient follow-ups. | Cannot access financial billing management or database backups. |

---

## 3. Simplified, Simulated & Educational Implementations

To ensure high performance, security, and portability for academic review without external cloud dependencies:

1. **Synthetic Identifiers (Poka-Yoke)**:
   - Patient UHIDs strictly follow `UHID-2026-XXXXXX`.
   - Contact numbers auto-format via input masking to `+91-XXXXX-XXXXX`.
   - No real Aadhaar, social security, or personal identifying numbers are ever stored.
2. **Telemedicine Video**:
   - Simulated via WebRTC link generation (`https://meet.jit.si/Apex-HMS-...`) and Google Meet links with instant launch capability.
3. **Ambulance Telemetry**:
   - Simulated GPS fleet coordinates and dispatch status tracking with one-click route monitoring.
4. **Biomedical & Life-Safety Rounds**:
   - Digital life-safety inspections for nominal oxygen manifold pressures (55–65 PSI), medical vacuum (-18 to -22 PSI), fire alarm panel loops, and diesel generator emergency power reserves.
5. **Statistical Process Control (SPC)**:
   - Automated 3-Sigma calculation for OPD patient waiting time (X-bar chart) and Lab Turnaround Time (p-chart), with control limit evaluation (UCL, LCL, Centerline).

---

## 4. Multi-Device Responsive Verification

All screens and navigation drawers have been verified in real headless Chromium browser sessions with Playwright across standard device viewports:

- **Desktop Monitor (1440 × 900 px)**: Full collapsible accordion sidebar with search filter, persistent patient banner, multi-column clinical cards.
- **Tablet / iPad (820 × 900 px)**: Responsive adaptive sidebar, touch-friendly tab targets, condensed tabular views.
- **Mobile Handset (390 × 844 px)**: Off-canvas navigation drawer with backdrop overlay, floating hamburger toggle button, full-width cards.
