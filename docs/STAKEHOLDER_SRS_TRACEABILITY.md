# Stakeholder Analysis & Requirements Traceability Matrix (RTM)
**Course:** BBAT104 — Fundamentals of Total Quality Management  
**Project:** Hospital Management System (HMS) — TQM-Driven Healthcare Informatics  
**Student:** Ajay Bora | **Roll No:** 2410302008 | **Branch:** CSE — Section B  
**Academic Session:** 2026–27  
**Official Guideline Identifier:** `BBAT104_TQM_2410302008`  

---

## 1. Introduction & Methodology

A foundational principle of Total Quality Management (TQM) in software engineering is that **every line of code and database schema must trace directly to a verified customer need**, and conversely, every stakeholder requirement must be verified by automated objective evidence. 

In strict adherence to **Section 7 and Section 8 of the Base Project Guideline**, this document establishes:
1. **The Comprehensive 10-Role Stakeholder Register:** Mapping the complete socio-technical ecosystem of the hospital.
2. **The Software Requirements Specification (SRS):** Formulated as atomic, testable, numbered statements (`SR-XXX-NNN`).
3. **The 6-Way Requirements Traceability Matrix (RTM):** Explicitly linking:
   $$\text{Stakeholder Need} \longleftrightarrow \text{SRS Requirement} \longleftrightarrow \text{Process Step} \longleftrightarrow \text{Database Object} \longleftrightarrow \text{UI Component} \longleftrightarrow \text{Automated Test Case}$$

---

## 2. Comprehensive 10-Role Stakeholder Register

| # | Stakeholder Role | Primary Operational Need / Problem Addressed | Critical Information Required | System Interaction Touchpoint | Success Measure & KPI |
|:---:|---|---|---|---|---|
| **1** | **Patient** | Minimized waiting time, transparent billing, and zero repeat registrations. | Doctor availability, appointment token, itemized bill, diagnosis timeline. | Patient Intake Screen / Reception Desk / Patient 360° Portal | Waiting time < 15 mins; Zero billing disputes |
| **2** | **Receptionist / Front Desk** | Fast, error-free intake; prevention of duplicate patient charts. | Master patient index, current phone number, doctor specialty roster. | Patients Tab / Appointments Tab / Dynamic Autocomplete Search | Registration cycle time < 90 secs; 0% duplicate UHIDs |
| **3** | **Attending Doctor / Clinician** | Immediate access to historical clinical context, vitals, and safe prescribing. | Longitudinal encounter history, physiological vitals, recorded allergies, lab reports. | Doctor Dashboard / Patient 360° View / Prescription Module | Zero Adverse Drug Reactions (ADR); Consultation cycle time tracking |
| **4** | **Triage & Ward Nurse** | Rapid acuity sorting; clear visibility of vital thresholds and doctor orders. | Patient blood pressure, pulse, SpO2, temperature, assigned bed status. | Emergency Triage Queue / Vitals Entry Dialog | Triage classification time < 60 secs; Zero missed Code Red alerts |
| **5** | **Billing Officer / Cashier** | Automated tariff calculations, transparent receipts, and zero financial leakage. | Room days, doctor consultation charges, dispensed pharmacy items, payment method. | Billing & Invoicing Module / Printable HTML Tax Invoices | Billing error rate = 0.0%; Instant reconciliation |
| **6** | **Laboratory Technician** | Traceable test requisitions, unambiguous specimen tracking, and critical flags. | Test name, clinical category, patient ID, biological reference intervals. | Diagnostic Lab Diagnostics Tab / Result Verification View | Lab turnaround time (TAT) < 4 hours; 100% abnormal flags highlighted |
| **7** | **Bed / Ward Manager** | Real-time bed visibility, instant sanitization tracking, and zero double-allocations. | Ward type, room number, occupancy state (`Available`, `Occupied`, `Cleaning`). | Ward & Bed Management Grid / Inpatient Admissions Tab | Bed turnaround time < 30 mins; Zero double-occupancies |
| **8** | **Hospital Quality Manager** | Objective, continuous evidence of operational stability and compliance. | Daily defect logs, Shewhart control limits, compliance audit scores, FMEA RPN. | Defect Checksheet / SQC Analytics / NABH Quality Audit Checklist | Process Capability $C_p > 1.33$; DPMO < 3,400 (4.5+ Sigma) |
| **9** | **Medical Superintendent / Hospital Manager** | High-level operational throughput, resource bottlenecks, and financial health. | Departmental patient footfall, room utilization rates, revenue collections. | Executive Summary Dashboard / Live Analytics Counters | Operational decision turnaround < 5 mins; Full bed utilization |
| **10** | **IT & Systems Administrator** | Data integrity, role enforcement, immutable auditing, and zero unrecoverable crashes. | User authentication hashes, access roles, mutation logs, snapshot backups. | Admin Console / Dual-Tier Audit Log Viewer / Automated Backup Engine | System uptime > 99.9%; 100% audit trail coverage |

---

