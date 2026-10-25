# Project Evaluation & Defense Dossier (Review-1 & Review-2)
**Course:** BBAT104 — Fundamentals of Total Quality Management  
**Project:** Hospital Management System (HMS) — TQM-Driven Healthcare Informatics  
**Student:** Ajay Bora | **Roll No:** 2410302008 | **Branch:** CSE — Section B  
**Academic Session:** 2026–27  
**Official Guideline Identifier:** `BBAT104_TQM_2410302008`  

---

## 1. Executive Purpose

This document serves as the master defense and evaluation dossier for **Review-1** (System Design & Requirements Engineering) and **Review-2** (Software Demonstration & Quality Evidence) in strict alignment with **Sections 20, 21, and 25 of the Base Project Guideline**.

The objective is to equip the student with an airtight presentation script, live demonstration steps, and verifiable evidence proving that this project is not a generic CRUD database, but a disciplined, TQM-engineered healthcare informatics system.

---

## 2. Review-1 Evaluation Dossier: System Design & Requirements

### 2.1 Review-1 Deliverables Checklist

| Guideline Requirement (Section 20) | Implementation Evidence in Repository | Document / Source Reference | Status |
|---|---|---|:---:|
| **Specific Hospital Process & Problem Statement** | Outpatient Department (OPD) & Emergency Triage Journey; Elimination of duplicate records, double-booking, and medication errors. | `docs/LITERATURE_REVIEW.md` (Sec 6) | **READY** |
| **Literature Review** | NABH 6th Edition (all 10 chapters analyzed) + ABDM national digital health framework + 3 system benchmarks. | `docs/LITERATURE_REVIEW.md` (Sec 2–5) | **READY** |
| **Stakeholder Map & Needs** | 10 hospital roles analyzed with explicit information needs, interaction touchpoints, and KPIs. | `docs/STAKEHOLDER_SRS_TRACEABILITY.md` (Sec 2) | **READY** |
| **Numbered, Testable SRS** | 24 atomic specifications (`SR-PAT-001` through `SR-SEC-003`) categorized by clinical domains. | `docs/STAKEHOLDER_SRS_TRACEABILITY.md` (Sec 3) | **READY** |
| **Traceability Matrix** | 6-way matrix linking Stakeholder $\leftrightarrow$ SRS $\leftrightarrow$ Process $\leftrightarrow$ Schema $\leftrightarrow$ UI $\leftrightarrow$ Test. | `docs/STAKEHOLDER_SRS_TRACEABILITY.md` (Sec 4) | **READY** |
| **Process Maps (As-Is / To-Be)** | Waste/delay analysis; multi-role swimlane sequence; finite state machines for Appointments, Lab, Beds. | `docs/PROCESS_WORKFLOW_MAPS.md` | **READY** |
| **Role-Permission Matrix** | Server-side enforced matrix for Admin, Doctor, Receptionist, Nurse, Lab Tech, Cashier. | `docs/architecture.md` (Sec 5) | **READY** |
| **Initial ERD & Data Dictionary** | 14 relational tables with primary keys, foreign keys, constraints, and audit entities. | `docs/ER_Diagram.md`, `src/database/db_manager.py` | **READY** |
| **Layered Architecture Rationale** | Strict multi-tier separation (Presentation $\rightarrow$ REST Blueprints $\rightarrow$ Business Rules $\rightarrow$ SQL Models $\rightarrow$ DB). | `docs/architecture.md` | **READY** |
| **FMEA Risk Prioritization** | 12 failure modes evaluated with Pre/Post RPN calculations demonstrating >90% risk reduction. | `TQM/FMEA.md`, `docs/FMEA_RiskAudit.xlsx` | **READY** |
| **P0 / P1 / P2 Prioritization** | Coherent scope boundaries: P0 Core Intake, P1 Connected Clinical Care, P2 TQM Analytics. | `docs/SRS.md`, `docs/STAKEHOLDER_SRS_TRACEABILITY.md` | **READY** |

---

