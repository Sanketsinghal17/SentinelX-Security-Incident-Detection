from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from app.models.models import (
    User, SecurityLog, Alert, Incident, InvestigationNote,
    ResponseAction, ThreatIntelligence, SimulationHistory
)
from app.detection_engine.engine import DetectionEngine

def seed_database(db_session):
    """
    Seeds initial realistic SOC dataset if the database is unpopulated.
    """
    # 1. Seed Users if not present
    existing_user = db_session.query(User).filter_by(username="analyst@sentinelx.io").first()
    if not existing_user:
        analyst = User(
            username="analyst@sentinelx.io",
            email="analyst@sentinelx.io",
            password_hash=generate_password_hash("Sentinel@2025"),
            full_name="Alex Vance (Lead Analyst)",
            role="Security Analyst",
            created_at=datetime.utcnow()
        )
        admin = User(
            username="admin",
            email="admin@sentinelx.io",
            password_hash=generate_password_hash("SentinelPass123!"),
            full_name="Morgan Reed (SOC Manager)",
            role="SOC Lead",
            created_at=datetime.utcnow()
        )
        db_session.add_all([analyst, admin])
        db_session.commit()

    # 2. Seed Threat Intelligence
    if db_session.query(ThreatIntelligence).count() == 0:
        threat_seeds = [
            ThreatIntelligence(
                ip_address="185.220.101.45",
                reputation_score=94,
                threat_type="Tor Exit Node / Credential Stuffing",
                country="Netherlands",
                isp="Zwiebelfreunde e.V.",
                is_known_attacker=True,
                reports_count=42,
                notes="Observed across multi-tenant SSH brute force campaigns."
            ),
            ThreatIntelligence(
                ip_address="91.240.118.88",
                reputation_score=98,
                threat_type="Botnet Command & Control (C2)",
                country="Russia",
                isp="HostKey B.V.",
                is_known_attacker=True,
                reports_count=118,
                notes="Active beacon host for Cobalt Strike / RedLine infostealer."
            ),
            ThreatIntelligence(
                ip_address="194.26.29.112",
                reputation_score=88,
                threat_type="DDoS Amplification Reflector",
                country="Bulgaria",
                isp="DDoS-Guard Corp",
                is_known_attacker=True,
                reports_count=65,
                notes="Origin of NTP/SSDP reflection bursts."
            ),
            ThreatIntelligence(
                ip_address="198.51.100.42",
                reputation_score=75,
                threat_type="Automated Vulnerability Scanner",
                country="United States",
                isp="DigitalOcean LLC",
                is_known_attacker=True,
                reports_count=19,
                notes="Repetitive masscan and nuclei probing activity."
            ),
            ThreatIntelligence(
                ip_address="10.0.1.15",
                reputation_score=5,
                threat_type="Internal Trusted Domain Controller",
                country="Local Subnet",
                isp="Internal Intranet",
                is_known_attacker=False,
                reports_count=0,
                notes="Primary Active Directory Domain Controller."
            ),
        ]
        db_session.add_all(threat_seeds)
        db_session.commit()

    # 3. Seed Baseline Security Logs & Incidents if empty
    if db_session.query(SecurityLog).count() == 0:
        now = datetime.utcnow()
        logs_to_add = []

        # Normal benign background traffic
        for i in range(15):
            t = now - timedelta(hours=3, minutes=i * 10)
            logs_to_add.append(SecurityLog(
                timestamp=t,
                source_ip=f"10.0.1.{20 + i}",
                destination_ip="10.0.1.15",
                username=f"user_{i:02d}",
                event_type="Authentication",
                action="LOGIN_SUCCESS",
                protocol="Kerberos",
                status="SUCCESS",
                description="Standard domain user workstation authentication",
                hostname=f"corp-desktop-{i:02d}",
                port=88,
                bytes_sent=450,
                bytes_received=1200
            ))

        # Baseline Brute Force Attack
        bf_attacker = "198.51.100.42"
        for i in range(6):
            t = now - timedelta(hours=1, minutes=20, seconds=i * 15)
            logs_to_add.append(SecurityLog(
                timestamp=t,
                source_ip=bf_attacker,
                destination_ip="10.0.1.15",
                username="administrator",
                event_type="Authentication",
                action="LOGIN_FAILED",
                protocol="RDP",
                status="FAILED",
                description="Repeated failed NTLM authentication attempt over port 3389",
                hostname="auth-gateway-prod",
                port=3389,
                bytes_sent=180,
                bytes_received=320,
                raw_payload="NTLMSSP_AUTH_REJECTED"
            ))

        # Baseline Port Scan
        scan_ip = "185.220.101.45"
        for i, p in enumerate([21, 22, 80, 443, 3389, 8080]):
            t = now - timedelta(hours=2, minutes=i * 2)
            logs_to_add.append(SecurityLog(
                timestamp=t,
                source_ip=scan_ip,
                destination_ip="10.0.1.1",
                username="anonymous",
                event_type="Network",
                action="PORT_SWEEP_SYN",
                protocol="TCP",
                status="BLOCKED",
                description=f"Perimeter firewall dropped unrequested probe on port {p}",
                hostname="perimeter-firewall-01",
                port=p,
                bytes_sent=64,
                bytes_received=0
            ))

        # Baseline Malware Execution
        logs_to_add.append(SecurityLog(
            timestamp=now - timedelta(minutes=45),
            source_ip="10.0.2.88",
            destination_ip="91.240.118.88",
            username="analyst_dev",
            event_type="Endpoint",
            action="MALWARE_DETECTED",
            protocol="HOST_OS",
            status="ALERT",
            description="Antivirus real-time guard flagged mimikatz.exe in temp directory.",
            hostname="workstation-finance-02",
            port=0,
            bytes_sent=0,
            bytes_received=0,
            raw_payload="ThreatName: HackTool:Win32/Mimikatz!dha Path: C:\\Windows\\Temp\\mimikatz.exe"
        ))

        db_session.add_all(logs_to_add)
        db_session.commit()

        # Run detection engine to populate baseline alerts & incidents
        DetectionEngine.process_logs(db_session, logs_to_add)

        # Add initial sample investigation note
        first_incident = db_session.query(Incident).first()
        if first_incident:
            note = InvestigationNote(
                incident_id=first_incident.id,
                author="Alex Vance (Lead Analyst)",
                note="Initial triage complete. Source IP correlates with known threat telemetry feed. Containment playbooks initiated.",
                created_at=datetime.utcnow()
            )
            db_session.add(note)
            db_session.commit()
