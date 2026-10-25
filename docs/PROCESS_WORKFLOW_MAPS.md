# Process & Workflow Engineering: As-Is vs. To-Be Analysis
**Course:** BBAT104 — Fundamentals of Total Quality Management  
**Project:** Hospital Management System (HMS) — TQM-Driven Healthcare Informatics  
**Student:** Ajay Bora | **Roll No:** 2410302008 | **Branch:** CSE — Section B  
**Academic Session:** 2026–27  
**Official Guideline Identifier:** `BBAT104_TQM_2410302008`  

---

## 1. Executive Summary & Lean TQM Principles

In hospital operations, quality is defined not merely by clinical outcomes, but by the reliability, safety, and timeliness of the underlying administrative and clinical workflows. According to Lean Healthcare principles (Womack et al., 2005) and Total Quality Management (TQM), systemic inefficiencies stem from three core failure categories:
1. **Muda (Waste):** Unnecessary patient waiting, duplicate data entry across paper registers, physical transit of paper slips, and re-collecting demographic data.
2. **Muri (Overburden):** Overloaded doctors deciphering illegible handwriting without historical allergy context; receptionists managing chaotic physical queues.
3. **Mura (Unevenness):** Erratic patient queue distribution, unmanaged walk-in spikes, and volatile doctor scheduling collisions.

In accordance with **Section 10 of the Base Project Guideline**, this document maps:
- The **As-Is Workflow** of a conventional outpatient clinic and its points of failure.
- The **To-Be Workflow** engineered for our TQM Hospital Management System.
- A **Comprehensive Multi-Role Swimlane Process Diagram**.
- Formal **State Transition Machines** for Appointments, Laboratory Investigations, and Ward Bed Allocations.

---

## 2. As-Is Process Analysis & Failure Points

```mermaid
flowchart TD
    A[Patient Arrives at Clinic] --> B[Wait in Physical Queue at Reception]
    B --> C[Receptionist Searches Paper Register]
    C -->|Record Not Found / Illegible| D[Register New File: Duplicate UHID Risk]
    C -->|Record Found| E[Manual Token Issued on Paper Slip]
    D --> E
    E --> F[Patient Transits to OPD Waiting Hall]
    F --> G[Doctor Conducts Consultation]
    G --> H[Handwritten Prescription on Paper Pad]
    H -->|Illegible / No Allergy Check| I[Pharmacy: Dispensing Error / ADR Risk]
    H -->|Lab Test Ordered| J[Patient Transits to Cash Counter for Payment]
    J --> K[Cashier Manually Calculates Charges: Arithmetic Error Risk]
    K --> L[Patient Walks to Pathology Lab]
    L --> M[Manual Sample Phlebotomy & Paper Slip]
    M --> N[Results Typed Manually: Transcription Defect Risk]
    N --> O[Patient Returns to Doctor with Physical Report]
```

### 2.1 Critical Pain Points in the As-Is Workflow

| Process Step | Operational Waste (Muda) | Failure Mode & Clinical Risk | Root Cause in Legacy Workflow | TQM Poka-Yoke Solution in HMS |
|---|---|---|---|---|
| **Intake / Registration** | 15–20 min queue waiting; Repeated questioning of demographics. | Duplicate patient charts created; Fragmented medical history. | Free-text manual registers with zero search or indexing. | **Debounced Auto-Complete Search + Mandatory Input Masking (`+91-XXXXX-XXXXX`).** |
| **Doctor Scheduling** | Patients arriving when doctor is off-duty; Waiting room crowding. | Double-booking chaos; Excessive patient dissatisfaction. | Paper diaries and verbal doctor schedule handoffs. | **Automated Slot Engine (`has_conflict`) with HTTP 409 conflict blocking.** |
| **Emergency Triage** | Acutely ill patients waiting behind non-urgent routine consultations. | Delayed resuscitation in Code Red emergencies; Clinical morbidity. | First-come, first-served queueing without vital triage. | **Bounded Vital Signs Input + Real-Time Acuity-Sorted Emergency Queue.** |
| **Prescription Writing** | Pharmacists spending time phoning doctors to clarify dosage. | Fatal Adverse Drug Reactions (ADR); Expired drug dispensing. | Handwritten slips; No automated drug-allergy cross-referencing. | **Pre-flight Allergy Contraindication Checker + Batch Expiry Poka-Yoke.** |
| **Diagnostic Requisitions** | Patient walking between billing, lab, and doctor with paper slips. | Unpaid tests processed; Delayed critical lab reports. | Disconnected departmental ledgers with no shared state. | **Reference Range Poka-Yoke + Automated Abnormal Flag ($0$ or $1$) generation.** |
| **Financial Invoicing** | Patients disputing manual additions at discharge. | Revenue leakage; Overcharging or undercharging patients. | Manual arithmetic calculation on paper receipts. | **Automated Server-Side Charge Arithmetic + Instant HTML Print Receipts.** |

---

