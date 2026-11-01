# SentinelX SOC – Application Screenshots & Visual Walkthrough Guidance

This document provides a visual walkthrough and reference layout for each major module of **SentinelX – Security Incident Detection and Analysis**. Use this guide during academic presentations, Project-Based Learning (PBL) evaluations, and faculty viva demonstrations.

---

## 1. Authentication & Analyst Console Access
**Route:** `/login`

### Visual Composition:
- **Cyber Aesthetic**: Deep navy/black background (`#070b14`) accented by cyan glows and a subtle radial grid matrix.
- **Brand Identity**: Floating SentinelX SOC shield icon with version indicator (`v2.4 Enterprise`).
- **Input Fields**: Analyst Identifier (`analyst@sentinelx.io`) and Access Token password field.
- **1-Click Demonstration Fillers**: Two dedicated interactive quick-fill buttons allowing evaluators to immediately log in as either:
  1. `Alex Vance (Lead Analyst)`
  2. `Morgan Reed (SOC Manager / Admin)`

---

## 2. Executive SOC Dashboard
**Route:** `/`

### Visual Composition:
- **Top Threat Posture Banner**: Live DEFCON status indicator pill displaying real-time threat posture (`CRITICAL ELEVATED`, `ACTIVE THREATS`, or `OPERATIONAL NORMAL`) with a pulsing LED indicator.
- **Summary KPI Metric Cards**:
  1. *Total Telemetry Events* (Cyan glow)
  2. *Total Incidents* (Purple indicator)
  3. *Critical Threats* (Pulsing Red LED)
  4. *High Severity Incidents* (Amber / Orange indicator)
  5. *Open Incidents* (Under active response)
  6. *Resolved Incidents* (Emerald / Green indicator)
- **Telemetry & Incidents Timeline Chart**: 7-day dual Recharts area graph tracking ingested log volume against correlated incident outbreaks.
- **Incidents by Severity Donut**: Multi-colored donut visualization with interactive tooltips showing Critical, High, Medium, and Low risk distributions.
- **Attack Category Bar Chart**: Breakdown of incidents across the 8 detection vectors.
- **Top Targeted Enterprise Assets**: Horizontal bar chart identifying targeted servers (`auth-gateway-prod`, `db-production-vault`, `perimeter-firewall-01`).
- **Live Security Alerts Feed**: Scrolling event feed with severity badges, detection rule matches, and 1-click links to deep-dive into the incident investigation room.
- **Top Threat Indicators Matrix**: Geolocation flags, ISP details, and risk scores (0–100) for active suspicious IP addresses.

---

## 3. Security Log Ingestion & Management
**Route:** `/logs`

### Visual Composition:
- **Downloadable Sample Telemetry**: Download buttons for `sentinelx_sample_security_logs.csv` and `sentinelx_sample_security_logs.json`.
- **Drag & Drop / File Uploader**: Validates `.csv` and `.json` structured logs up to 16MB.
- **Real-Time Pipeline Feedback**: Status banner displaying total parsed records, duplicate records prevented, alerts fired by the detection engine, and newly linked incidents.
- **Multi-Vector Search Toolbar**: Real-time search across IP address, username, hostname, and description keywords.
- **Category Filter Dropdown**: Fast switching between all 6 log categories:
  - *Authentication*
  - *Network*
  - *Firewall*
  - *System*
  - *Application*
  - *Endpoint*
- **Structured Log Table**: Displays timestamp (UTC), source IP, destination IP, user, category, action, status pill (`SUCCESS`, `FAILED`, `BLOCKED`, `ALERT`), and device port.
- **Pagination Controls**: Responsive bottom pagination with page count and total records.

---

## 4. Incident Classification & Prioritization Queue
**Route:** `/incidents`

### Visual Composition:
- **Incident Matrix Header**: Triage counter and CSV export shortcut (`Export Incidents CSV`).
- **Multi-Dimensional Triage Filters**: Filter incidents by Severity (`Critical`, `High`, `Medium`, `Low`), Category (8 attack types), or Status (`Open`, `Investigating`, `Contained`, `Resolved`, `Closed`).
- **Interactive Status Dropdown**: Analysts can change incident status on the fly directly from the table.
- **Incident Docket Rows**:
  - Unique Incident ID (`INC-202611-XXXXX`)
  - Glowing severity badge
  - Attack category tag
  - Incident title & target asset
  - Attacker source IP
  - Assigned SOC Owner
  - Quick launch icon navigating to the dedicated Investigation Room.

---

## 5. Incident Investigation Room & Forensic Docket
**Route:** `/incidents/:id`

### Visual Composition:
- **Top Investigation Header**: Back navigation button, Incident ID, severity badge, operational status badge, status transition dropdown, and **Generate PDF Report** button.
- **Forensic Overview Cards**: Six summary tiles displaying Category, Source IP, Destination IP, Target Asset, Assigned Analyst, and UTC Detection Timestamp.
- **Technical Analysis Cards**:
  1. *Identified Attack Vector* (Technical entry vector)
  2. *Root Cause Analysis* (Misconfiguration / unpatched CVE / permissive ACL)
  3. *Business Impact Assessment* (Compliance risk / data loss / latency)
- **6-Stage Incident Response Lifecycle Timeline**:
  1. Stage 1: Initial Suspicious Activity
  2. Stage 2: Detection Event Trigger
  3. Stage 3: Alert Generation
  4. Stage 4: Investigation Started
  5. Stage 5: Containment Action
  6. Stage 6: Resolution & Recovery
- **Correlated Raw Evidence Table**: Exact raw log entries, timestamps, and raw command payloads (e.g. `powershell -enc`, `mimikatz.exe`, `SELECT * FROM users`) linked directly to the incident.
- **Containment & Mitigation Playbook**: Interactive checklist allowing analysts to click and toggle response actions between `Pending`, `In Progress`, and `Completed`.
- **Analyst Investigation Notes Thread**: Real-time chronological discussion thread where analysts document forensic findings and hypothesis verification.

---

## 6. Cybersecurity Attack Simulation Center
**Route:** `/simulation`

### Visual Composition:
- **8 Attack Scenario Cards**: One-click synthetic attack triggers corresponding to all 8 detection rules:
  1. *Brute Force Attack* (SSH/RDP credential guessing)
  2. *Port Scanning Reconnaissance* (Perimeter TCP SYN sweep)
  3. *Suspicious Login / Credential Stuffing* (Post-failure login anomaly)
  4. *Malware & EDR Indicator* (Mimikatz / encoded PowerShell)
  5. *Data Exfiltration Surge* (High-bandwidth outbound dump)
  6. *Unauthorized Access & Traversal* (Path traversal & SQL injection)
  7. *Denial of Service (DDoS)* (Volumetric HTTP flood)
  8. *Phishing & Malicious Domain* (Credential harvester link & malicious attachment)
- **Interactive SOC Terminal Console**: Black command-line console showing animated real-time log injection, detection rule evaluation, alert creation, and incident linking.
- **Post-Simulation Direct Action**: Clickable button redirecting immediately into the newly generated incident.
- **Reset Demo Data Option**: Protected by confirmation modal dialog to restore the database to clean baseline conditions.
- **Simulation Audit Trail Table**: Chronological log of all simulated tests.

---

## 7. Threat Intelligence & IP Reputation
**Route:** `/threat-intel`

### Visual Composition:
- **Adversary IP Telemetry Lookup**: Search bar accepting any IPv4 address with instant scoring.
- **Reputation Gauge Card**: Dynamic color-coded threat score meter (0 to 100), classification badge, origin geolocation flag, autonomous system / ISP name, and telemetry notes.
- **Threat Indicator Catalog**: Full catalog table of known malicious Tor exit nodes, botnet C2 servers, vulnerability scanners, and reflection proxies.

---

## 8. Statistical Trend & Impact Analytics
**Route:** `/analytics`

### Visual Composition:
- **SLA & Efficiency KPIs**: Mean Time to Resolution (MTTR in hours), Resolution Success Rate (%), and Average Detection Latency (minutes).
- **24-Hour Attack Frequency Heat Pattern**: Hourly distribution bar chart highlighting adversary peak activity hours.
- **Enterprise Asset Risk Scoring Index**: Weighted calculation of asset vulnerability based on attack frequency and severity coefficients.
- **Organizational Business Impact Tier Assessment**: 4-tier risk classification cards summarizing high-impact vs low-impact incident exposure.

---

## 9. Report & Forensic Export Center
**Route:** `/reports`

### Visual Composition:
- **Executive Security Summary Report (PDF)**: 1-click download of high-level CISO overview report formatted with ReportLab.
- **Incident Forensic Dossier (PDF)**: Case selector dropdown allowing download of the complete 12-section PDF investigation report for any incident.
- **CSV Data Feeds**: Instant CSV export buttons for both the incidents table and raw security logs.
