# Comprehensive Literature Review & Industry Benchmarking
**Course:** BBAT104 — Fundamentals of Total Quality Management  
**Project:** Hospital Management System (HMS) — TQM-Driven Healthcare Informatics  
**Student:** Ajay Bora | **Roll No:** 2410302008 | **Branch:** CSE — Section B  
**Academic Session:** 2026–27  
**Official Guideline Identifier:** `BBAT104_TQM_2410302008`  

---

## 1. Executive Summary & Purpose of Literature Review

Healthcare Information Systems (HIS) and Electronic Medical Records (EMR) are mission-critical socio-technical infrastructures where software failures directly translate into clinical morbidity, diagnostic delays, medication misadventures, and patient dissatisfaction. The primary objective of this literature review is to ground the software engineering and Total Quality Management (TQM) design of our **Hospital Management System (HMS)** in empirical healthcare operations, national digital health architectures, and statutory quality standards.

Rather than developing features based on anecdotal assumptions or producing a superficial CRUD database, this study systematically analyzes:
1. **Hospital Quality & Accreditation Standards:** National Accreditation Board for Hospitals & Healthcare Providers (NABH 6th Edition, January 2025).
2. **National Digital Health Ecosystem:** Ayushman Bharat Digital Mission (ABDM), Ayushman Bharat Health Account (ABHA), and Fast Healthcare Interoperability Resources (FHIR).
3. **Clinical Process Workflows:** Outpatient Department (OPD) patient journeys, hand-off failures, and clinical bottlenecks.
4. **Software & Quality Engineering Benchmarks:** Mistake-proofing (Poka-Yoke), Failure Mode & Effects Analysis (FMEA), Statistical Process Control (SPC), and Deming's Plan-Do-Check-Act (PDCA) cycle.
5. **Existing Industry HIS Products:** Comparative analysis of enterprise hospital systems, commercial clinic software, and clinician-built digital hospitals.

---

## 2. Core Literature Review Buckets

| # | Literature Area | Primary Standard / Academic Sources Studied | Key Takeaways & Testable Requirements Extracted |
|---|---|---|---|
| **1** | **Hospital Quality** | NABH Hospital Accreditation Programme (6th Edition, Jan 2025); Quality Council of India (QCI). | Patient identification protocols, prescription legibility, medication allergy cross-checks, laboratory critical limit alerts, and immutable medical audit trails. |
| **2** | **Digital HIS / EMR** | HIMSS Electronic Medical Record Adoption Model (EMRAM Stages 1–7); ISO/TS 18308: Health Informatics. | Transition from isolated departmental silos to integrated Patient 360° longitudinal health records with transactional atomicity. |
| **3** | **Indian Digital Health** | National Health Authority (NHA) ABDM Sandbox; ABHA Specification v2.0; Unified Health Interface (UHI). | Architectural separation between institutional permanent identifier (UHID) and national health identity (ABHA); consent-driven, federated data access. |
| **4** | **Clinical Workflow** | Institute of Medicine (IOM) "To Err Is Human"; Lean Healthcare (Muda, Muri, Mura); OPD Time-Motion Studies. | Queue management, triage prioritization (Code Red/Yellow/Green), doctor consultation cycle time, and diagnostic turn-around time (TAT). |
| **5** | **Software Engineering** | IEEE 830 / ISO/IEC/IEEE 29148 (Requirements Engineering); Martin Fowler (Layered Architecture); Role-Based Access Control (NIST RBAC). | Strict multi-tier separation (Presentation → REST API → Service/Business Rules → Data Access/Models → SQLite Database); server-side authorization enforcement. |
| **6** | **Quality Engineering** | Shigeo Shingo (Poka-Yoke Mistake-Proofing); AIAG & VDA FMEA Handbook; Walter Shewhart & W. Edwards Deming (SPC & PDCA). | Keystroke input masking, categorical dropdowns, schedule conflict pre-flight checks, batch expiry blocks, and Shewhart c-chart statistical process monitoring. |
| **7** | **Security & Privacy** | Digital Personal Data Protection Act (DPDP 2023, India); ISO/IEC 27001; DISHA (Digital Information Security in Healthcare Act). | Cryptographic password hashing (SHA-256), session timeouts, role-segregated API endpoints, zero-plaintext credential persistence, and synthetic evaluation data. |

---

