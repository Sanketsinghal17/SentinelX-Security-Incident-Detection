import hashlib
from datetime import datetime
from app.models.models import ThreatIntelligence

class ThreatService:
    """
    Threat Intelligence service for IP reputation lookup,
    malicious indicator tracking, and threat scoring.
    """

    @classmethod
    def lookup_ip(cls, db_session, ip_address):
        """
        Looks up an IP in the local threat intelligence database.
        If not found, synthesizes a deterministic simulated reputation
        and labels it clearly as simulated/locally maintained.
        """
        record = (
            db_session.query(ThreatIntelligence)
            .filter_by(ip_address=ip_address)
            .first()
        )

        if record:
            data = record.to_dict()
            data["data_source"] = "Local Threat DB (Verified)"
            return data

        # Deterministic simulation for demonstration
        # Hash IP to get consistent simulated score
        ip_hash = int(hashlib.md5(ip_address.encode()).hexdigest()[:6], 16)
        is_private = (
            ip_address.startswith("10.") or
            ip_address.startswith("192.168.") or
            ip_address.startswith("172.16.") or
            ip_address == "127.0.0.1"
        )

        if is_private:
            score = 5
            threat_type = "Internal / Private Network"
            country = "Local Subnet"
            isp = "Corporate Intranet Infrastructure"
            is_attacker = False
            notes = "RFC1918 Private Internal IP address. No external threat indicator."
        else:
            # Deterministic public IP threat classification
            score = 40 + (ip_hash % 58) # 40-97
            is_attacker = score >= 70
            countries = ["United States", "Netherlands", "Russia", "China", "Germany", "Brazil", "Bulgaria"]
            isps = ["HostKey B.V.", "DigitalOcean LLC", "Chinanet", "OVH SAS", "Amazon AWS", "M247 Europe", "Selectel"]
            threat_types = [
                "Botnet Command & Control (C2)",
                "Tor Exit Node / Bulletproof Hosting",
                "Automated Vulnerability Scanner",
                "Credential Stuffing Source",
                "DDoS Reflection Proxy"
            ]

            country = countries[ip_hash % len(countries)]
            isp = isps[ip_hash % len(isps)]
            threat_type = threat_types[ip_hash % len(threat_types)] if is_attacker else "Unclassified External Host"
            notes = (
                f"Simulated Threat Intelligence: Observed {score % 15 + 1} malicious telemetry reports. "
                f"Associated with {threat_type} activity."
            )

        return {
            "ip_address": ip_address,
            "reputation_score": score,
            "threat_type": threat_type,
            "country": country,
            "isp": isp,
            "is_known_attacker": is_attacker,
            "reports_count": 1 if is_private else (score % 20 + 2),
            "last_seen": datetime.utcnow().isoformat(),
            "source_type": "Simulated Threat Analysis",
            "notes": notes,
            "data_source": "Simulated Threat Intelligence (Local Sandbox Mode)"
        }

    @classmethod
    def get_all_threats(cls, db_session):
        records = db_session.query(ThreatIntelligence).order_by(ThreatIntelligence.reputation_score.desc()).all()
        return [r.to_dict() for r in records]
