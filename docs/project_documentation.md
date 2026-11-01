# SentinelX: Security Incident Detection and Analysis
## Academic Project-Based Learning (PBL) Forensic Report & Engineering Documentation

---

### Project Metadata
- **Project Title:** SentinelX – Security Incident Detection and Analysis
- **Domain:** Cybersecurity, Security Operations Center (SOC), Threat Intelligence & Incident Response
- **Application Version:** 2.4.0 (Enterprise PBL Edition)
- **Author / Developer:** Sanket Singhal
- **Architecture Model:** Full-Stack Decoupled Client-Server (REST API + Reactive SPA)

---

## 1. Introduction

Modern enterprises face an unprecedented volume and sophistication of cyberattacks, ranging from automated credential brute forcing and port scanning sweeps to covert data exfiltration, ransomware staging, and spear-phishing campaigns. Traditional static perimeter defenses are no longer sufficient; organizations rely on Security Operations Centers (SOC) equipped with Security Information and Event Management (SIEM) systems and automated detection pipelines to achieve situational awareness and rapid threat containment.

**SentinelX** is an enterprise-grade, end-to-end cybersecurity platform engineered as a comprehensive Project-Based Learning (PBL) project. It demonstrates how a modern security team detects, analyzes, classifies, prioritizes, investigates, mitigates, and reports cybersecurity incidents through a working Python Flask backend, SQLite relational database, rule-based detection engine, interactive React + Tailwind CSS dashboard, and ReportLab forensic PDF generation.

---

## 2. Project Objectives

The primary engineering and educational objectives of the SentinelX platform are:
1. **Automated Incident Detection**: Ingest heterogeneous security telemetry across six categories (Authentication, Network, Firewall, System, Application, and Endpoint) and execute rule-based detection algorithms.
2. **Classification & Prioritization**: Automatically classify incidents into recognized attack categories (Brute Force, Port Scanning, Suspicious Login, Malware, Data Exfiltration, Unauthorized Access, DDoS, Phishing) and assign risk-based severity scores (Low, Medium, High, Critical).
3. **Forensic Investigation**: Provide analysts with a dedicated Incident Investigation Room featuring a 6-stage lifecycle timeline, correlated raw logs, root-cause deductions, business impact assessments, and an interactive analyst notes thread.
4. **Containment & Response**: Supply actionable mitigation playbooks tailored to each attack vector, allowing simulated containment (e.g., firewall block simulation, endpoint quarantine, credential revocation).
5. **Threat Intelligence Integration**: Track known malicious IP addresses, provide reputation scoring (0–100 risk scale), and catalog autonomous system indicators.
6. **Executive Reporting**: Produce professional, publication-quality PDF reports using ReportLab with multi-page headers, executive summaries, timeline matrices, evidence logs, and analyst sign-offs.
7. **Simulation & Demonstration**: Offer an integrated 8-scenario attack simulation center with real-time console telemetry and 1-click test evaluation.

---

## 3. Problem Statement

Enterprise SOC teams grapple with critical operational bottlenecks:
- **Alert Fatigue**: Thousands of disjointed log events obscure true indicators of compromise (IoCs).
- **Delayed MTTR (Mean Time to Resolution)**: Manual correlation between perimeter firewall logs, identity providers, and endpoint telemetry delays threat containment.
- **Inconsistent Documentation**: Incident post-mortems and compliance documentation often lack unified structure, missing crucial forensic evidence and response timestamps.
- **Educational Gap**: Academic learners often lack access to an actual operational SOC environment where raw logs directly trigger detection rules, generate alerts, link to incidents, and execute mitigation playbooks.

SentinelX solves these challenges by providing a transparent, functional, and fully automated SOC pipeline.

---

## 4. System Architecture

SentinelX employs a decoupled modular architecture:

```
+-----------------------------------------------------------------------------------+
|                              REACT FRONTEND (Vite SPA)                            |
|  +--------------------+  +----------------------+  +---------------------------+  |
|  |   SOC Dashboard    |  | Log Ingestion & Feed |  | Incidents & Triage Queue  |  |
|  +--------------------+  +----------------------+  +---------------------------+  |
|  +--------------------+  +----------------------+  +---------------------------+  |
|  | Investigation Room |  |  Simulation Center   |  | Threat Intel & Analytics  |  |
|  +--------------------+  +----------------------+  +---------------------------+  |
+------------------------------------------+----------------------------------------+
                                           | HTTP / REST API (Axios + JWT)
                                           v
+-----------------------------------------------------------------------------------+
|                              PYTHON FLASK BACKEND                                 |
|  +-------------------+  +---------------------+  +-----------------------------+  |
|  | Flask Blueprints  |  | Auth (JWT / Scrypt) |  |   ReportLab PDF Service     |  |
|  +-------------------+  +---------------------+  +-----------------------------+  |
|  +-----------------------------------------------------------------------------+  |
|  |                  SENTINELX DETECTION ENGINE & RULE ORCHESTRATOR             |  |
|  |    [Brute Force] [Port Scan] [Suspicious Login] [Malware] [Data Exfil]       |  |
|  |             [Unauthorized Access] [DDoS Flood] [Phishing Link]              |  |
|  +-----------------------------------------------------------------------------+  |
|  +-----------------------------------------------------------------------------+  |
|  |                       SERVICES & SIMULATION GENERATOR                       |  |
|  |       Pandas Trend Engine | Threat Intelligence Service | Data Seeder       |  |
|  +-----------------------------------------------------------------------------+  |
+------------------------------------------+----------------------------------------+
                                           | SQLAlchemy ORM
                                           v
+-----------------------------------------------------------------------------------+
|                              SQLITE RELATIONAL DATABASE                           |
|   [users]   [security_logs]   [alerts]   [incidents]   [investigation_notes]      |
|             [response_actions]   [threat_intelligence]   [simulation_history]     |
+-----------------------------------------------------------------------------------+
```

---

## 5. Methodology & Incident Response Lifecycle

SentinelX models the industry-standard NIST SP 800-61 Rev. 2 Computer Security Incident Handling Guide:

```
+----------------+      +-------------------+      +---------------------+
| 1. Ingestion   | ---> | 2. Detection      | ---> | 3. Classification   |
| CSV/JSON/Sim   |      | Rules Engine 01-08|      | Triage & Prioritize |
+----------------+      +-------------------+      +---------------------+
                                                              |
                                                              v
+----------------+      +-------------------+      +---------------------+
| 6. Reporting   | <--- | 5. Containment    | <--- | 4. Investigation    |
| PDF & CSV Dumps|      | Playbook Action   |      | Correlate Evidence  |
+----------------+      +-------------------+      +---------------------+
```

1. **Ingestion**: Telemetry arrives via CSV/JSON file upload, continuous monitoring, or the Attack Simulation Center.
2. **Detection**: Logs pass through all 8 rules in `DetectionEngine`. Matches produce `Alert` entities.
3. **Classification**: High and Critical alerts automatically synthesize or correlate to an `Incident` entity with categorized severity, title, attack vector, root cause, and business impact.
4. **Investigation**: Analysts open the Incident Investigation Room to review correlated raw logs, inspect payload commands, and review geolocation threat scores.
5. **Containment & Response**: Analysts execute mitigation checklists (e.g. firewall drop, credential revocation, host quarantine) and record notes.
6. **Reporting**: The platform generates formal PDF dossiers for compliance archiving and leadership post-mortems.

---

## 6. Database Design & Schema

The relational database is implemented using SQLite via SQLAlchemy ORM.

### Tables Specification

#### 1. `users`
- `id` (INTEGER, PK): Unique analyst identifier.
- `username` (VARCHAR(80), UNIQUE): Login username.
- `email` (VARCHAR(120), UNIQUE): Corporate email.
- `password_hash` (VARCHAR(255)): Cryptographic hash generated using `scrypt`.
- `full_name` (VARCHAR(120)): Analyst name.
- `role` (VARCHAR(50)): Role (`Security Analyst`, `SOC Lead`).
- `created_at` (DATETIME): Account creation timestamp.

#### 2. `security_logs`
- `id` (INTEGER, PK): Log entry identifier.
- `timestamp` (DATETIME): Event timestamp.
- `source_ip` (VARCHAR(45)): Origin IPv4 address.
- `destination_ip` (VARCHAR(45)): Destination IPv4 address.
- `username` (VARCHAR(80)): Associated username.
- `event_type` (VARCHAR(50)): Category (`Authentication`, `Network`, `Firewall`, `System`, `Application`, `Endpoint`).
- `action` (VARCHAR(50)): Operational verb (`LOGIN_FAILED`, `PORT_SWEEP_SYN`, `PROCESS_EXECUTION`).
- `protocol` (VARCHAR(20)): Network protocol (`TCP`, `UDP`, `SSH`, `HTTPS`).
- `status` (VARCHAR(30)): Outcome status (`SUCCESS`, `FAILED`, `BLOCKED`, `ALERT`).
- `description` (TEXT): Log message description.
- `hostname` (VARCHAR(100)): Target asset hostname.
- `port` (INTEGER): Destination port number.
- `bytes_sent` (INTEGER): Egress transfer bytes.
- `bytes_received` (INTEGER): Ingress transfer bytes.
- `raw_payload` (TEXT): Raw command execution or packet payload.

#### 3. `alerts`
- `id` (INTEGER, PK): Primary key.
- `alert_id` (VARCHAR(50), UNIQUE): Reference string (e.g. `ALT-261101-A1B2C3`).
- `detection_timestamp` (DATETIME): Alert generation time.
- `attack_type` (VARCHAR(80)): Attack classification.
- `source_ip` (VARCHAR(45)): Offending IP address.
- `destination_ip` (VARCHAR(45)): Target IP address.
- `target_system` (VARCHAR(100)): Targeted asset.
- `severity` (VARCHAR(20)): `Low`, `Medium`, `High`, `Critical`.
- `description` (TEXT): Rule match deduction.
- `detection_rule` (VARCHAR(100)): Name of detection rule triggered.
- `recommended_action` (TEXT): SOC triage recommendation.
- `investigation_status` (VARCHAR(30)): Status (`New`, `Incident Created`).
- `log_ids` (TEXT): Comma-separated IDs of evidence logs.
- `incident_id` (INTEGER, FK -> incidents.id): Linked incident.

#### 4. `incidents`
- `id` (INTEGER, PK): Internal identifier.
- `incident_id` (VARCHAR(50), UNIQUE): Public reference ID (`INC-202611-ABCDE`).
- `title` (VARCHAR(200)): Human-readable summary.
- `category` (VARCHAR(50)): Attack type category.
- `severity` (VARCHAR(20)): Severity rank.
- `status` (VARCHAR(30)): `Open`, `Investigating`, `Contained`, `Resolved`, `Closed`.
- `source_ip` (VARCHAR(45)): Attacker IP.
- `destination_ip` (VARCHAR(45)): Victim IP.
- `affected_asset` (VARCHAR(100)): Impacted host.
- `detection_timestamp` (DATETIME): Initial detection time.
- `description` (TEXT): Incident overview.
- `attack_vector` (VARCHAR(150)): Entry vector.
- `root_cause` (TEXT): Root cause forensic deduction.
- `business_impact` (TEXT): Impact analysis.
- `recommended_mitigation` (TEXT): Primary remediation.
- `owner` (VARCHAR(80)): Assigned analyst.
- `created_at` (DATETIME): Record creation time.
- `updated_at` (DATETIME): Last modification time.

#### 5. `investigation_notes`
- `id` (INTEGER, PK): Note identifier.
- `incident_id` (INTEGER, FK -> incidents.id): Parent incident.
- `author` (VARCHAR(80)): Analyst signature.
- `note` (TEXT): Forensic commentary.
- `created_at` (DATETIME): Post timestamp.

#### 6. `response_actions`
- `id` (INTEGER, PK): Primary key.
- `incident_id` (INTEGER, FK -> incidents.id): Parent incident.
- `action_title` (VARCHAR(150)): Action item name.
- `action_type` (VARCHAR(50)): Playbook category (`Firewall Block`, `Endpoint Isolation`).
- `status` (VARCHAR(30)): `Pending`, `In Progress`, `Completed`.
- `analyst_notes` (TEXT): Implementation notes.

#### 7. `threat_intelligence`
- `id` (INTEGER, PK): Record ID.
- `ip_address` (VARCHAR(45), UNIQUE): Tracked IP.
- `reputation_score` (INTEGER): Risk score (0 to 100).
- `threat_type` (VARCHAR(80)): Category (`Tor Exit Node`, `Botnet C2`).
- `country` (VARCHAR(60)): Geolocation.
- `isp` (VARCHAR(120)): Network carrier.
- `is_known_attacker` (BOOLEAN): Threat flag.
- `reports_count` (INTEGER): Telemetry report count.

#### 8. `simulation_history`
- `id` (INTEGER, PK): Audit record ID.
- `simulation_name` (VARCHAR(100)): Test title.
- `attack_type` (VARCHAR(80)): Vector type.
- `logs_generated` (INTEGER): Injected event count.
- `alerts_generated` (INTEGER): Generated alerts.
- `incidents_created` (INTEGER): Linked incidents.
- `status` (VARCHAR(30)): Execution status.
- `timestamp` (DATETIME): Run time.

---

## 7. Detection Algorithms & Technical Logic

The SentinelX Detection Engine implements 8 independent rule algorithms:

### Rule 1: Brute Force Authentication Detection
- **Objective**: Detect distributed or single-source password guessing attempts.
- **Algorithm**:
  - Filter logs where `action` contains `LOGIN` or `AUTH`, and `status` in `[FAILED, FAILURE, BLOCKED]`.
  - Group events by `source_ip`.
  - Apply a sliding time-window of 300 seconds (5 minutes).
  - If $\text{count}(\text{events}) \ge 5$, trigger Alert.
  - Severity: $\text{count} \ge 10 \implies \text{Critical}$, else $\text{High}$.

### Rule 2: Reconnaissance Port Scanning
- **Objective**: Detect perimeter reconnaissance and service enumeration.
- **Algorithm**:
  - Extract network logs where `action` matches `PORT_SWEEP_SYN`, `SCAN`, or connection probes on distinct destination ports.
  - Compute $\text{DistinctPorts}(src\_ip) = \{port_1, port_2, \dots, port_k\}$.
  - If $|\text{DistinctPorts}| \ge 5$, trigger Alert.
  - Severity: $|\text{DistinctPorts}| \ge 15 \implies \text{High}$, else $\text{Medium}$.

### Rule 3: Suspicious Login Pattern (Credential Stuffing)
- **Objective**: Identify password cracking success after repeated authentication failures.
- **Algorithm**:
  - Track ordered authentication sequence per `username`.
  - Identify patterns where $\ge 3$ consecutive failed logins are followed immediately by an event with `status == SUCCESS`.
  - Assign Severity: `High`.

### Rule 4: Malware & EDR Process Indicators
- **Objective**: Identify known adversarial binaries, credential dumpers, and living-off-the-land techniques.
- **Algorithm**:
  - Compile regex patterns matching `mimikatz`, `powershell\s+(-enc|-encodedcommand)`, `vssadmin\s+delete\s+shadows`, `certutil\s+-urlcache`, `.locked`, and `eicar`.
  - Scan log fields: `description`, `raw_payload`, and `action`.
  - Match trigger produces `Critical` alert and suggests endpoint isolation.

### Rule 5: Data Exfiltration Surge
- **Objective**: Identify massive single or burst egress transfer to external IP addresses.
- **Algorithm**:
  - Accumulate outbound bytes: $\sum \text{bytes\_sent}(src\_ip \to dest\_ip)$.
  - If $\text{TotalBytes} \ge 15\text{ MB}$ or `description` matches exfiltration keywords, trigger `Critical` alert.

### Rule 6: Unauthorized Access & Traversal Probes
- **Objective**: Detect privilege escalation, directory traversal, and SQL injection probes.
- **Algorithm**:
  - Regex inspection against `/etc/passwd`, `/etc/shadow`, `/admin/secrets`, `../../`, and `UNION SELECT`.
  - Flags HTTP 403 / Forbidden anomalies.
  - Assign Severity: `High`.

### Rule 7: Denial of Service (DDoS) Volumetric Flood
- **Objective**: Detect rapid request flooding intended to exhaust system capacity.
- **Algorithm**:
  - Compute request rate: $\text{requests}(src\_ip) \ge 15$ in batch window.
  - Severity: $\ge 30 \implies \text{Critical}$, else $\text{High}$.

### Rule 8: Phishing Indicators & Deceptive Domains
- **Objective**: Detect user interaction with deceptive domains or malicious macros.
- **Algorithm**:
  - Match domains with keywords: `login-verify`, `paypa1`, `secure-bank-update`, or attachments ending in `.xlsm`.
  - Flag events with action `MALICIOUS_LINK_CLICKED`.
  - Assign Severity: `High`.

---

## 8. Implementation Details

- **Backend Framework**: Python 3.12 with Flask 3.1.2, SQLAlchemy 2.0.43, and Pandas 2.3.1.
- **Forensic PDF Engine**: ReportLab 5.1.0 using `SimpleDocTemplate` and custom `NumberedCanvas` for exact page budget calculation, dynamic tables, severity color coding, and executive signatures.
- **Frontend Framework**: React 18 with Vite, Tailwind CSS 3.4.17, Recharts, and Lucide React.
- **Real-Time State Flow**: Managed through `DashboardContext`, propagating instant re-fetching upon simulation triggers or log uploads without full browser reloads.

---

## 9. Testing & Quality Assurance

A rigorous two-tiered automated testing framework was implemented and executed:

### Test Suite 1: Independent Detection Engine Rule Tests (`backend/tests/test_detection_engine.py`)
- `test_01_brute_force_rule`: Verified sliding-window detection for 6 failed logins.
- `test_02_port_scanning_rule`: Verified detection of 7 distinct scanned ports.
- `test_03_suspicious_login_rule`: Verified detection of 3 failures followed by success.
- `test_04_malware_indicator_rule`: Verified regex matching of `mimikatz.exe` and `powershell -enc`.
- `test_05_data_exfiltration_rule`: Verified detection of 22MB outbound payload transfer.
- `test_06_unauthorized_access_rule`: Verified detection of `/etc/shadow` and `UNION SELECT`.
- `test_07_denial_of_service_rule`: Verified detection of 18 rapid requests.
- `test_08_phishing_indicator_rule`: Verified detection of `https://login-verify-corp.xyz`.
- **Result:** **8 out of 8 tests passed in 0.002s (100% pass rate).**

### Test Suite 2: Full API Integration & Forensic Tests (`backend/tests/test_api.py`)
- `test_01_health_check`: Verified backend service status and DB connection.
- `test_02_auth_login`: Verified JWT token issuance and user profile retrieval.
- `test_03_dashboard_summary_and_charts`: Verified KPI aggregations and Recharts data payloads.
- `test_04_logs_list_and_sample_download`: Verified log pagination and CSV sample download.
- `test_05_incidents_api`: Verified incident details, 6-stage timeline, and notes appending.
- `test_06_simulations_all_eight`: Verified all 8 attack scenarios trigger alerts and link to incidents.
- `test_07_threat_intelligence_lookup`: Verified IP reputation scoring.
- `test_08_analytics_trends`: Verified Pandas MTTR and risk index calculations.
- `test_09_pdf_and_csv_reports`: Verified binary ReportLab PDF generation (`%PDF` header) and CSV exports.
- **Result:** **9 out of 9 integration tests passed (100% pass rate).**

### Test Suite 3: Frontend Production Build
- Vite production build executed with zero JSX or syntax errors (`dist/` generated in 1.96s).

---

## 10. Results & Evaluation

The SentinelX platform demonstrates:
1. **Sub-Second Detection Latency**: Detection rules evaluate log batches in $<5\text{ms}$.
2. **Deterministic Attack Simulation**: Evaluators can trigger any of the 8 attack scenarios and immediately observe alerts and incidents on the dashboard.
3. **Comprehensive Investigation Docket**: Incidents clearly correlate raw telemetry evidence with recommended response actions.
4. **Forensic Grade PDF Generation**: Produces publication-ready PDF reports with headers, footers, metadata boxes, and sign-offs.

---

## 11. Conclusion

SentinelX successfully achieves all requirements of an enterprise-grade cybersecurity Project-Based Learning platform. It bridges the gap between theoretical security concepts and operational execution, illustrating how automated correlation rules, threat intelligence lookups, and standardized response workflows contain threats and safeguard modern digital enterprises.

---

## 12. Future Scope

Future engineering enhancements planned for SentinelX include:
1. **Machine Learning Anomaly Detection**: Implementing Isolation Forests or autoencoders to detect zero-day telemetry anomalies alongside deterministic rules.
2. **STIX/TAXII Threat Feed Consumption**: Ingesting live external threat feeds from AlienVault OTX or MISP.
3. **Automated SOAR Webhooks**: Disconnecting live test VMs or dispatching real Slack/Teams alerts via webhook integrations.
4. **MITRE ATT&CK Matrix Mapping**: Tagging each rule and incident with official MITRE ATT&CK technique IDs (e.g. T1110 for Brute Force, T1059 for PowerShell).
