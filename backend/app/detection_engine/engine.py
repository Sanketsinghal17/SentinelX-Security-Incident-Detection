import uuid
from datetime import datetime
from app.models.models import Alert, Incident, ResponseAction
from app.detection_engine.rules import ALL_RULES

class DetectionEngine:
    """
    Core security incident detection engine.
    Ingests security logs, runs rule evaluations, generates alerts,
    and automatically aggregates them into manageable security incidents.
    """

    @classmethod
    def process_logs(cls, db_session, logs):
        """
        Processes a list of SecurityLog instances or dicts.
        Saves alerts and incidents to the database session.
        """
        if not logs:
            return {"alerts_created": 0, "incidents_created": 0, "alerts": [], "incidents": []}

        # Convert ORM logs to dictionaries if needed
        dict_logs = []
        for l in logs:
            if hasattr(l, "to_dict"):
                dict_logs.append(l.to_dict())
            elif isinstance(l, dict):
                dict_logs.append(l)

        generated_alerts = []
        for rule in ALL_RULES:
            try:
                rule_alerts = rule.evaluate(dict_logs)
                generated_alerts.extend(rule_alerts)
            except Exception as e:
                print(f"[DetectionEngine] Error evaluating rule {rule.rule_id}: {e}")

        saved_alerts = []
        created_incidents = []

        for alert_data in generated_alerts:
            # Check for existing alert with identical log_ids to avoid duplicate processing of same logs
            log_ids_val = alert_data.get("log_ids", "")
            if log_ids_val:
                existing = db_session.query(Alert).filter_by(log_ids=log_ids_val).first()
                if existing:
                    continue

            unique_alert_id = f"ALT-{datetime.utcnow().strftime('%y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
            alert = Alert(
                alert_id=unique_alert_id,
                detection_timestamp=datetime.utcnow(),
                attack_type=alert_data["attack_type"],
                source_ip=alert_data["source_ip"],
                destination_ip=alert_data.get("destination_ip"),
                target_system=alert_data["target_system"],
                severity=alert_data["severity"],
                description=alert_data["description"],
                detection_rule=alert_data["detection_rule"],
                recommended_action=alert_data.get("recommended_action", "Investigate immediately."),
                investigation_status="New",
                log_ids=alert_data.get("log_ids", "")
            )
            db_session.add(alert)
            db_session.flush() # Populate alert.id

            # Incident Auto-Correlation / Creation
            incident = cls._correlate_or_create_incident(db_session, alert)
            alert.incident_id = incident.id
            alert.investigation_status = "Incident Created"

            saved_alerts.append(alert.to_dict())
            if incident not in [i for i in created_incidents]:
                created_incidents.append(incident)

        db_session.commit()

        return {
            "alerts_created": len(saved_alerts),
            "incidents_created": len(created_incidents),
            "alerts": saved_alerts,
            "incidents": [inc.to_dict() for inc in created_incidents]
        }

    @classmethod
    def _correlate_or_create_incident(cls, db_session, alert):
        """
        Correlates alert to an active open incident or creates a new incident.
        """
        active_incident = (
            db_session.query(Incident)
            .filter(
                Incident.category == alert.attack_type,
                Incident.source_ip == alert.source_ip,
                Incident.status.in_(["Open", "Investigating"])
            )
            .first()
        )

        if active_incident:
            # Upgrade severity if alert is higher
            severity_rank = {"Low": 1, "Medium": 2, "High": 3, "Critical": 4}
            if severity_rank.get(alert.severity, 1) > severity_rank.get(active_incident.severity, 1):
                active_incident.severity = alert.severity
            active_incident.updated_at = datetime.utcnow()
            return active_incident

        # Create new incident
        unique_inc_id = f"INC-{datetime.utcnow().strftime('%Y%m')}-{uuid.uuid4().hex[:5].upper()}"
        
        # Determine category, vectors, root cause, impact
        attack_type = alert.attack_type
        category = attack_type
        if attack_type == "Port Scanning":
            category = "Port Scanning"
            attack_vector = "External Network Reconnaissance / TCP SYN Sweeps"
            root_cause = "Exposed perimeter firewall ports or lack of IP rate-limiting."
            business_impact = "Potential intelligence gathering leading to targeted service exploitation."
        elif attack_type == "Brute Force":
            category = "Brute Force"
            attack_vector = "Credential Guessing / Distributed Dictionary Attack"
            root_cause = "Missing account lockout threshold and absence of mandatory multi-factor authentication (MFA)."
            business_impact = "High risk of unauthorized system compromise, data theft, and lateral movement."
        elif attack_type == "Suspicious Login":
            category = "Unauthorized Access"
            attack_vector = "Credential Stuffing / Stolen Session Hijacking"
            root_cause = "Compromised employee password or session token replay."
            business_impact = "Unauthorized internal access to confidential corporate databases."
        elif attack_type == "Malware":
            category = "Malware"
            attack_vector = "Malicious Payload Execution / Living-off-the-Land Binaries (LOLBins)"
            root_cause = "Drive-by download, unpatched vulnerability, or malicious attachment execution."
            business_impact = "Critical endpoint compromise, potential ransomware propagation or ransomware lockdown."
        elif attack_type in ["Data Breach", "Data Exfiltration"]:
            category = "Data Breach"
            attack_vector = "Covert Outbound Protocol Tunneling / High-Volume Data Egress"
            root_cause = "Lack of egress filtering and data loss prevention (DLP) inspection."
            business_impact = "Severe regulatory penalties (GDPR/HIPAA), loss of intellectual property, and reputational damage."
        elif attack_type == "Unauthorized Access":
            category = "Unauthorized Access"
            attack_vector = "Web Vulnerability (SQL Injection, Path Traversal) / Broken Access Control"
            root_cause = "Insufficient input validation in application layer and permissive file system permissions."
            business_impact = "Unauthorized data disclosure and elevation of privileges."
        elif attack_type == "DDoS":
            category = "DDoS"
            attack_vector = "Volumetric HTTP/TCP SYN Flooding"
            root_cause = "Direct exposed origin IP without distributed anti-DDoS proxy scrubbing."
            business_impact = "Downtime of critical web services and degraded customer experience."
        elif attack_type == "Phishing":
            category = "Phishing"
            attack_vector = "Spear-Phishing Email with Malicious Domain Link"
            root_cause = "Bypassed email gateway filters and user credential submission."
            business_impact = "Corporate identity compromise, unauthorized email access, and wire fraud risks."
        else:
            category = "Unauthorized Access"
            attack_vector = "Unknown Attack Pattern"
            root_cause = "Security anomaly detected in logs."
            business_impact = "Operational disruption."

        incident = Incident(
            incident_id=unique_inc_id,
            title=f"Detected {alert.attack_type} on {alert.target_system}",
            category=category,
            severity=alert.severity,
            status="Open",
            source_ip=alert.source_ip,
            destination_ip=alert.destination_ip,
            affected_asset=alert.target_system,
            detection_timestamp=alert.detection_timestamp,
            description=alert.description,
            attack_vector=attack_vector,
            root_cause=root_cause,
            business_impact=business_impact,
            recommended_mitigation=alert.recommended_action,
            owner="SOC Triage Analyst",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db_session.add(incident)
        db_session.flush()

        # Seed initial response action items (playbook)
        cls._create_playbook_actions(db_session, incident)

        return incident

    @classmethod
    def _create_playbook_actions(cls, db_session, incident):
        """
        Creates actionable containment checklist items for the incident response team.
        """
        cat = incident.category
        actions = []

        if cat == "Brute Force":
            actions = [
                ("Block Malicious Source IP", "Firewall Block", "Simulate adding IP to boundary firewall drop list."),
                ("Force Password Reset & MFA Challenge", "Credential Reset", "Invalidate active tokens and mandate 2FA re-enrollment."),
                ("Audit Authentication Logs", "Threat Hunting", "Check for any other affected corporate usernames.")
            ]
        elif cat == "Port Scanning":
            actions = [
                ("Apply Border ACL Drop Rule", "Firewall Block", "Drop incoming packets from scanning source IP."),
                ("Review Exposed Perimeter Ports", "Policy Update", "Verify whether sensitive management ports (RDP/SSH) are reachable."),
                ("Enable Dynamic Port Knocking", "Policy Update", "Protect internal administrative services.")
            ]
        elif cat == "Malware":
            actions = [
                ("Isolate Affected Endpoint", "Endpoint Isolation", "Sever network connection of the infected host."),
                ("Terminate Suspicious Process Trees", "Endpoint Remediation", "Kill malicious tasks and delete persistence keys."),
                ("Collect Memory & Forensic Image", "Threat Hunting", "Acquire volatile RAM artifacts for reverse engineering.")
            ]
        elif cat in ["Data Breach", "Data Exfiltration"]:
            actions = [
                ("Terminate High-Bandwidth Session", "Firewall Block", "Immediately drop TCP socket connection to external receiver."),
                ("Identify Exfiltrated Data Assets", "Threat Hunting", "Reconcile database query logs and sensitive file accesses."),
                ("Initiate Data Privacy Breach Protocol", "Policy Update", "Notify compliance officer and document scope.")
            ]
        elif cat == "DDoS":
            actions = [
                ("Enable Origin Rate Limiting", "Rate Limiting", "Enforce 50 requests/sec limit per IP subnet."),
                ("Engage Cloud Scrubbing Service", "Policy Update", "Route inbound traffic through DDoS mitigation proxy."),
                ("Inspect Web Server Health Metrics", "Threat Hunting", "Monitor CPU, RAM, and backlog queue capacity.")
            ]
        elif cat == "Phishing":
            actions = [
                ("Block Phishing URL at DNS Level", "DNS Sinkhole", "Sinkhole destination domain across corporate resolvers."),
                ("Purge Phishing Emails from Mailboxes", "Email Remediation", "Run global message purge query across Exchange/M365."),
                ("Reset Compromised User Credentials", "Credential Reset", "Mandate immediate password change for targeted victim.")
            ]
        else:
            actions = [
                ("Quarantine Source IP", "Firewall Block", "Temporarily restrict source IP address."),
                ("Audit Application Security Logs", "Threat Hunting", "Review related access events."),
                ("Deploy Remediation Hotfix", "Policy Update", "Harden affected resource permissions.")
            ]

        for title, act_type, notes in actions:
            action_record = ResponseAction(
                incident_id=incident.id,
                action_title=title,
                action_type=act_type,
                status="Pending",
                analyst_notes=notes,
                created_at=datetime.utcnow()
            )
            db_session.add(action_record)
