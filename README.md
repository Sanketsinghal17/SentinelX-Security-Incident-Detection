# SentinelX – Security Incident Detection and Analysis SOC

[![License](https://img.shields.io/badge/License-MIT-blue.svg)]()
[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)]()
[![Flask](https://img.shields.io/badge/Flask-3.1.2-green?logo=flask)]()
[![React](https://img.shields.io/badge/React-18-cyan?logo=react)]()
[![TailwindCSS](https://img.shields.io/badge/Tailwind-3.4-38bdf8?logo=tailwind-css)]()
[![Status](https://img.shields.io/badge/SOC%20Engine-Operational-emerald)]()

**SentinelX** is an enterprise-grade, end-to-end Security Operations Center (SOC) platform designed for academic Project-Based Learning (PBL). It demonstrates how enterprise security teams detect, analyze, classify, investigate, respond to, and mitigate cybersecurity incidents.

---

## Table of Contents
1. [Project Introduction](#project-introduction)
2. [Problem Statement & Objectives](#problem-statement--objectives)
3. [Technology Stack](#technology-stack)
4. [System Architecture](#system-architecture)
5. [Core Features & Modules](#core-features--modules)
6. [Database Structure](#database-structure)
7. [Detection Algorithms (8 Rules)](#detection-algorithms-8-rules)
8. [Demo Login Credentials](#demo-login-credentials)
9. [Installation & Setup Instructions](#installation--setup-instructions)
10. [How to Run the Application](#how-to-run-the-application)
11. [How to Simulate Security Incidents](#how-to-simulate-security-incidents)
12. [How to Upload & Ingest Logs](#how-to-upload--ingest-logs)
13. [How to Generate Forensic PDF Reports](#how-to-generate-forensic-pdf-reports)
14. [Screenshots Guidance](#screenshots-guidance)
15. [Automated Verification & Testing](#automated-verification--testing)
16. [Future Enhancements](#future-enhancements)

---

## 1. Project Introduction

In high-consequence enterprise environments, cyber threats develop in seconds. **SentinelX** simulates a production-grade Security Operations Center (SOC) equipped with automated log ingestion, a deterministic rule-based threat correlation engine, interactive investigative playbooks, and ReportLab-generated forensic PDF dossiers.

---

## 2. Problem Statement & Objectives

### Problem Statement
Enterprise cybersecurity teams face massive log telemetry volumes, high rates of false positives, and fragmented investigation tools that delay containment and post-incident documentation.

### Objectives
- **Ingest** raw telemetry across 6 categories: Authentication, Network, Firewall, System, Application, and Endpoint.
- **Evaluate** all 8 detection rules automatically on newly uploaded or simulated events.
- **Correlate** alerts into prioritized security incidents (`Critical`, `High`, `Medium`, `Low`).
- **Investigate** threats using a 6-stage lifecycle timeline, root cause analysis, and correlated raw evidence logs.
- **Respond** with interactive mitigation playbooks and recorded analyst notes.
- **Generate** executive summaries and incident investigation reports in PDF and CSV formats.

---

## 3. Technology Stack

### Frontend:
- **React.js (Vite)** – High-performance component-driven SPA
- **Tailwind CSS** – Custom dark cybersecurity SOC design theme
- **Recharts** – Interactive telemetry, severity, and risk visualizations
- **Lucide React** – Security and infrastructure icon suite
- **Axios** – HTTP client with JWT interceptor

### Backend:
- **Python Flask** – Modular REST API microframework
- **Pandas** – Statistical aggregations, MTTR calculations, and risk modeling
- **SQLite & SQLAlchemy** – Relational persistence layer
- **ReportLab** – Enterprise PDF generation with two-pass canvas page counting
- **PyJWT & Werkzeug** – Authentication and password hashing

---

## 4. System Architecture

```
[ Frontend: React + Vite + Tailwind ] <--- HTTP / REST API ---> [ Backend: Python Flask ]
               |                                                        |
  +-- Dashboard & KPIs                                     +-- 8-Rule Detection Engine
  +-- Log Ingestion (CSV/JSON)                             +-- ReportLab PDF Engine
  +-- Incident Investigation Room                          +-- Threat Intelligence
  +-- Simulation Center (8 Attacks)                        +-- SQLite Database
```

---

## 5. Core Features & Modules

1. **Executive SOC Dashboard**: KPI summary cards, Defcon threat posture indicator, 7-day telemetry area charts, severity donut, attack distribution, top targeted enterprise assets, and live alert stream.
2. **Security Log Ingestion**: Support for CSV and JSON logs across 6 categories (Authentication, Network, Firewall, System, Application, Endpoint). Duplicate record suppression and sample file downloads.
3. **Incident Classification & Triage**: Prioritization queue with multi-vector filters, severity badges, and quick status updates.
4. **Incident Investigation Room**: Correlated raw evidence logs, root cause analysis, business impact assessment, 6-stage incident lifecycle timeline, interactive containment playbook, and analyst notes.
5. **Attack Simulation Center**: 8 one-click realistic synthetic attack triggers, live command console, and a safe demo reset button.
6. **Threat Intelligence & IP Reputation**: IPv4 reputation query, 0–100 risk score meter, and known attacker catalog.
7. **Trend & Impact Analytics**: Pandas-powered statistical modeling, Mean Time to Resolution (MTTR), and asset vulnerability index.
8. **Forensic Report Generation**: ReportLab PDF incident reports, executive security summaries, and CSV exports.

---

## 6. Database Structure

The SQLite database (`sentinelx.db`) contains 8 relational tables:
- `users`: Analyst credentials and roles.
- `security_logs`: Ingested telemetry records.
- `alerts`: Rule-generated security alerts.
- `incidents`: Triaged incidents with root cause and impact analysis.
- `investigation_notes`: Chronological analyst collaboration logs.
- `response_actions`: Containment checklist items.
- `threat_intelligence`: Local reputation database.
- `simulation_history`: Audit record of simulation runs.

---

## 7. Detection Algorithms (8 Rules)

| Rule ID | Rule Name | Detection Trigger Condition | Severity |
| :--- | :--- | :--- | :--- |
| **RULE_001** | Brute Force Detection | $>5$ failed logins from same source IP in 5 minutes | Critical / High |
| **RULE_002** | Port Scanning Sweep | Single IP querying $\ge 5$ distinct destination ports | High / Medium |
| **RULE_003** | Suspicious Login Pattern | $\ge 3$ consecutive failed logins followed by success | High |
| **RULE_004** | Malware Indicators | Matches `mimikatz`, `powershell -enc`, `vssadmin` | Critical |
| **RULE_005** | Data Exfiltration | Outbound egress $>15\text{MB}$ or exfiltration keywords | Critical |
| **RULE_006** | Unauthorized Access | Restricted paths (`/etc/shadow`), path traversal, SQLi | High |
| **RULE_007** | Denial of Service (DDoS) | Rapid request flood ($\ge 15$ requests in batch window) | Critical / High |
| **RULE_008** | Phishing Indicators | Deceptive domains (`login-verify-corp.xyz`), macro `.xlsm` | High |

---

## 8. Demo Login Credentials

Use either of the following accounts to access the platform:

| Role | Username / Email | Password |
| :--- | :--- | :--- |
| **Lead Security Analyst** | `analyst@sentinelx.io` | `Sentinel@2025` |
| **SOC Manager / Admin** | `admin` | `SentinelPass123!` |

*Tip: The login page includes 1-click autofill buttons for instant evaluation.*

---

## 9. Installation & Setup Instructions

### Prerequisites
- Python 3.10+ (Tested on Python 3.12)
- Node.js 18+ & npm (Tested on Node v22)

### 1. Clone & Enter Directory
```bash
git clone <repo-url>
cd security-incident-detection
```

### 2. Backend Dependencies
```bash
pip install -r backend/requirements.txt
```

### 3. Frontend Dependencies
```bash
cd frontend
npm install
npm run build
cd ..
```

---

## 10. How to Run the Application

### Option A: Unified Full-Stack Launch (Recommended)
You can run the entire platform with a single command from the `backend/` folder:
```bash
cd backend
python app.py
```
- Open your browser to: **http://localhost:5000**
- Flask automatically serves the REST API and the compiled React SPA.

### Option B: Development Mode (Hot-Reloading)
Run backend and frontend in separate terminals:

**Terminal 1 (Backend):**
```bash
cd backend
python app.py
```
*(Runs on http://localhost:5000)*

**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev
```
*(Runs on http://localhost:5173 with automated proxy to backend)*

---

## 11. How to Simulate Security Incidents

1. Log into the console and navigate to **Simulation Center** (`/simulation`).
2. Click any of the **8 Attack Simulation buttons**:
   - *Simulate Brute Force Attack*
   - *Simulate Port Scanning*
   - *Simulate Suspicious Login*
   - *Simulate Malware Indicator*
   - *Simulate Data Exfiltration*
   - *Simulate Unauthorized Access*
   - *Simulate Denial of Service (DDoS)*
   - *Simulate Phishing Attack*
3. Watch the **SOC Terminal Console** generate synthetic telemetry, persist records, evaluate detection rules, and generate alerts.
4. Click **Investigate Incident** in the banner to jump straight to the forensic investigation room!
5. To reset the environment to clean baseline conditions at any time, click **Reset Demo Data**.

---

## 12. How to Upload & Ingest Logs

1. Navigate to **Security Logs** (`/logs`).
2. Download sample test data using the **Sample CSV** or **Sample JSON** buttons in the header.
3. Select the file in the **Ingest New Security Logs** card.
4. Click **Upload & Run Engine**.
5. The system will report total records imported, duplicate entries suppressed, and newly triggered incidents.

---

## 13. How to Generate Forensic PDF Reports

1. Navigate to **Report Center** (`/reports`).
2. To download an overall briefing, click **Download Executive Summary PDF**.
3. To generate an individual investigation report, select an incident from the dropdown and click **Generate Incident Forensic PDF**.
4. To export database tables into spreadsheets, click **Export Incidents CSV** or **Export Security Logs CSV**.

---

## 14. Screenshots Guidance

Refer to [docs/screenshots/README.md](file:///docs/screenshots/README.md) for a comprehensive breakdown and visual layouts of every major screen in the SentinelX platform.

---

## 15. Automated Verification & Testing

SentinelX includes automated test suites covering all detection rules and API endpoints:

```bash
# 1. Run independent rule test suite (All 8 rules)
python backend/tests/test_detection_engine.py

# 2. Run API integration test suite (All endpoints & PDF exports)
python backend/tests/test_api.py
```

All 17 automated unit and integration tests pass with a 100% success rate.

---

## 16. Future Enhancements

- Integration with real-time packet capturing tools (Scapy / Zeek).
- Machine learning anomaly detection with Isolation Forests.
- Direct STIX / TAXII threat feed synchronization.
- Automated SOAR webhook integrations with Jira and Slack.
