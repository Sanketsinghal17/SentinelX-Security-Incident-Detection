import re
from datetime import datetime, timedelta
from collections import defaultdict

class DetectionRule:
    rule_id = "BASE_RULE"
    rule_name = "Base Rule"
    category = "General"
    severity = "Medium"

    @classmethod
    def evaluate(cls, logs):
        """
        Takes a list of SecurityLog model instances or dictionaries.
        Returns a list of alert candidate dictionaries.
        """
        raise NotImplementedError

class BruteForceRule(DetectionRule):
    rule_id = "RULE_001_BRUTE_FORCE"
    rule_name = "Brute Force Authentication Attempt"
    category = "Brute Force"
    severity = "High"

    @classmethod
    def evaluate(cls, logs):
        alerts = []
        # Group failed logins by (source_ip, username)
        failed_by_ip = defaultdict(list)
        for log in logs:
            action = str(log.get("action", "")).upper()
            status = str(log.get("status", "")).upper()
            event_type = str(log.get("event_type", "")).upper()

            is_failed_login = (
                "LOGIN" in action or "AUTH" in event_type or "AUTH" in action
            ) and (status in ["FAILED", "FAILURE", "BLOCKED"] or "FAIL" in action)

            if is_failed_login and log.get("source_ip"):
                failed_by_ip[log.get("source_ip")].append(log)

        for src_ip, ip_logs in failed_by_ip.items():
            # Sort by timestamp
            ip_logs.sort(key=lambda x: x["timestamp"] if isinstance(x["timestamp"], datetime) else datetime.fromisoformat(str(x["timestamp"])))
            
            # Sliding window of 5 minutes (300 seconds)
            for i in range(len(ip_logs)):
                t_start = ip_logs[i]["timestamp"] if isinstance(ip_logs[i]["timestamp"], datetime) else datetime.fromisoformat(str(ip_logs[i]["timestamp"]))
                window_logs = [ip_logs[i]]
                for j in range(i + 1, len(ip_logs)):
                    t_curr = ip_logs[j]["timestamp"] if isinstance(ip_logs[j]["timestamp"], datetime) else datetime.fromisoformat(str(ip_logs[j]["timestamp"]))
                    if (t_curr - t_start).total_seconds() <= 300:
                        window_logs.append(ip_logs[j])
                    else:
                        break

                if len(window_logs) >= 5:
                    target_user = window_logs[0].get("username") or "multiple accounts"
                    target_host = window_logs[0].get("hostname") or "Auth Server"
                    severity = "Critical" if len(window_logs) >= 10 else "High"
                    log_ids = [l["id"] for l in window_logs if "id" in l]

                    alerts.append({
                        "attack_type": "Brute Force",
                        "source_ip": src_ip,
                        "destination_ip": window_logs[0].get("destination_ip"),
                        "target_system": target_host,
                        "severity": severity,
                        "description": f"Detected {len(window_logs)} failed authentication attempts from IP {src_ip} targeting user '{target_user}' within 5 minutes.",
                        "detection_rule": cls.rule_name,
                        "recommended_action": "Temporarily block source IP at the firewall, enforce MFA, and lock targeted account for 30 minutes.",
                        "log_ids": ",".join(str(lid) for lid in log_ids) if log_ids else ""
                    })
                    break # One alert per IP batch window
        return alerts

class PortScanningRule(DetectionRule):
    rule_id = "RULE_002_PORT_SCAN"
    rule_name = "Reconnaissance Port Sweep"
    category = "Port Scanning"
    severity = "Medium"

    @classmethod
    def evaluate(cls, logs):
        alerts = []
        ports_by_ip = defaultdict(lambda: {"ports": set(), "logs": []})

        for log in logs:
            event_type = str(log.get("event_type", "")).upper()
            action = str(log.get("action", "")).upper()
            port = log.get("port")
            src_ip = log.get("source_ip")

            if port and port > 0 and src_ip:
                if "NETWORK" in event_type or "FIREWALL" in event_type or "SCAN" in action or "CONNECT" in action:
                    ports_by_ip[src_ip]["ports"].add(port)
                    ports_by_ip[src_ip]["logs"].append(log)

        for src_ip, data in ports_by_ip.items():
            distinct_ports = data["ports"]
            if len(distinct_ports) >= 5: # 5 or more distinct ports accessed
                host = data["logs"][0].get("hostname") or "Network Gateway"
                dest_ip = data["logs"][0].get("destination_ip")
                severity = "High" if len(distinct_ports) >= 15 else "Medium"
                log_ids = [l["id"] for l in data["logs"] if "id" in l]

                sorted_ports = sorted(list(distinct_ports))[:10]
                ports_preview = ", ".join(str(p) for p in sorted_ports)

                alerts.append({
                    "attack_type": "Port Scanning",
                    "source_ip": src_ip,
                    "destination_ip": dest_ip,
                    "target_system": host,
                    "severity": severity,
                    "description": f"Reconnaissance detected: IP {src_ip} scanned {len(distinct_ports)} distinct ports (including {ports_preview}).",
                    "detection_rule": cls.rule_name,
                    "recommended_action": "Block port scanning source IP on external perimeter firewall, check if any target ports were open/vulnerable.",
                    "log_ids": ",".join(str(lid) for lid in log_ids) if log_ids else ""
                })
        return alerts

class SuspiciousLoginRule(DetectionRule):
    rule_id = "RULE_003_SUSPICIOUS_LOGIN"
    rule_name = "Anomalous Login Pattern / Post-Failure Success"
    category = "Suspicious Login"
    severity = "High"

    @classmethod
    def evaluate(cls, logs):
        alerts = []
        user_auth_seq = defaultdict(list)

        for log in logs:
            event_type = str(log.get("event_type", "")).upper()
            action = str(log.get("action", "")).upper()
            username = log.get("username")
            if username and ("AUTH" in event_type or "LOGIN" in action):
                user_auth_seq[username].append(log)

        for username, user_logs in user_auth_seq.items():
            user_logs.sort(key=lambda x: x["timestamp"] if isinstance(x["timestamp"], datetime) else datetime.fromisoformat(str(x["timestamp"])))
            
            # Look for >=3 failed logins followed directly by a SUCCESS
            failed_run = []
            for entry in user_logs:
                status = str(entry.get("status", "")).upper()
                action = str(entry.get("action", "")).upper()
                is_fail = status in ["FAILED", "FAILURE"] or "FAIL" in action
                is_success = status in ["SUCCESS", "ALLOWED"] or "SUCCESS" in action

                if is_fail:
                    failed_run.append(entry)
                elif is_success:
                    if len(failed_run) >= 3:
                        # Success after multiple failures - potential password compromise!
                        src_ip = entry.get("source_ip") or (failed_run[-1].get("source_ip"))
                        dest_ip = entry.get("destination_ip")
                        host = entry.get("hostname") or "Domain Controller"
                        log_ids = [l["id"] for l in (failed_run + [entry]) if "id" in l]

                        alerts.append({
                            "attack_type": "Suspicious Login",
                            "source_ip": src_ip,
                            "destination_ip": dest_ip,
                            "target_system": host,
                            "severity": "High",
                            "description": f"Potential credential compromise: User '{username}' had {len(failed_run)} consecutive login failures followed by an immediate successful login from IP {src_ip}.",
                            "detection_rule": cls.rule_name,
                            "recommended_action": "Immediately revoke active session for user, force password reset, and investigate source IP.",
                            "log_ids": ",".join(str(lid) for lid in log_ids) if log_ids else ""
                        })
                        failed_run = []
                    else:
                        failed_run = []
        return alerts

class MalwareIndicatorRule(DetectionRule):
    rule_id = "RULE_004_MALWARE"
    rule_name = "Malware & Suspicious Process Activity"
    category = "Malware"
    severity = "Critical"

    SUSPICIOUS_PATTERNS = [
        r"mimikatz",
        r"powershell\s+(-enc|-encodedcommand|downloadstring|bypass)",
        r"vssadmin\s+delete\s+shadows",
        r"certutil(\.exe)?\s+(-urlcache|-f)",
        r"\.locked|\.crypted|\.enc$",
        r"ransomware",
        r"backdoor|trojan|meterpreter|cobaltstrike",
        r"eicar-standard-antivirus-testfile",
        r"cmd\.exe\s+/c\s+powershell",
        r"suspicious_payload\.exe"
    ]

    @classmethod
    def evaluate(cls, logs):
        alerts = []
        regex = re.compile("|".join(cls.SUSPICIOUS_PATTERNS), re.IGNORECASE)

        for log in logs:
            desc = str(log.get("description", ""))
            payload = str(log.get("raw_payload", ""))
            action = str(log.get("action", ""))
            combined = f"{desc} {payload} {action}"

            match = regex.search(combined)
            if match:
                src_ip = log.get("source_ip") or "127.0.0.1"
                dest_ip = log.get("destination_ip")
                host = log.get("hostname") or "Endpoint-Workstation"
                log_id = str(log.get("id")) if "id" in log else ""

                alerts.append({
                    "attack_type": "Malware",
                    "source_ip": src_ip,
                    "destination_ip": dest_ip,
                    "target_system": host,
                    "severity": "Critical",
                    "description": f"Malware indicator detected: Matched execution pattern '{match.group(0)}' on host {host}.",
                    "detection_rule": cls.rule_name,
                    "recommended_action": "Isolate host from the network immediately, terminate malicious processes, collect memory dump, and initiate malware remediation playbook.",
                    "log_ids": log_id
                })
        return alerts

class DataExfiltrationRule(DetectionRule):
    rule_id = "RULE_005_EXFILTRATION"
    rule_name = "Abnormal Outbound Data Transfer"
    category = "Data Exfiltration"
    severity = "Critical"

    BYTE_THRESHOLD = 15 * 1024 * 1024 # 15 Megabytes

    @classmethod
    def evaluate(cls, logs):
        alerts = []
        outbound_by_flow = defaultdict(lambda: {"bytes": 0, "logs": []})

        for log in logs:
            bytes_sent = log.get("bytes_sent") or 0
            src_ip = log.get("source_ip")
            dest_ip = log.get("destination_ip")
            action = str(log.get("action", "")).upper()
            desc = str(log.get("description", "")).upper()

            # Identify outbound transfers
            if bytes_sent > 0 and src_ip and dest_ip:
                flow_key = (src_ip, dest_ip)
                outbound_by_flow[flow_key]["bytes"] += bytes_sent
                outbound_by_flow[flow_key]["logs"].append(log)
            elif "EXFILTRAT" in desc or "DATA_DUMP" in action or "LARGE_UPLOAD" in action:
                # Direct indicator
                log_id = str(log.get("id")) if "id" in log else ""
                alerts.append({
                    "attack_type": "Data Breach",
                    "source_ip": src_ip or "Internal Host",
                    "destination_ip": dest_ip or "External Host",
                    "target_system": log.get("hostname") or "File Server",
                    "severity": "Critical",
                    "description": f"Potential data exfiltration detected: {desc or 'Large confidential dataset upload detected'}.",
                    "detection_rule": cls.rule_name,
                    "recommended_action": "Immediately severed outbound session, block external IP, audit affected data repositories, and assess regulatory reporting requirements.",
                    "log_ids": log_id
                })

        for (src_ip, dest_ip), data in outbound_by_flow.items():
            total_bytes = data["bytes"]
            if total_bytes >= cls.BYTE_THRESHOLD:
                mb = round(total_bytes / (1024 * 1024), 2)
                log_ids = [l["id"] for l in data["logs"] if "id" in l]
                host = data["logs"][0].get("hostname") or "Database-Cluster"

                alerts.append({
                    "attack_type": "Data Breach",
                    "source_ip": src_ip,
                    "destination_ip": dest_ip,
                    "target_system": host,
                    "severity": "Critical",
                    "description": f"Exfiltration alert: Unusually high outbound data volume ({mb} MB transferred) from {src_ip} to external IP {dest_ip}.",
                    "detection_rule": cls.rule_name,
                    "recommended_action": "Block destination IP on boundary proxy, quarantine source endpoint, and review transferred file hashes.",
                    "log_ids": ",".join(str(lid) for lid in log_ids) if log_ids else ""
                })
        return alerts

class UnauthorizedAccessRule(DetectionRule):
    rule_id = "RULE_006_UNAUTHORIZED"
    rule_name = "Privilege Violation & Directory Traversal"
    category = "Unauthorized Access"
    severity = "High"

    RESTRICTED_KEYWORDS = [
        r"/etc/passwd",
        r"/etc/shadow",
        r"/admin/secrets",
        r"/config/database\.yml",
        r"\.\./\.\./",
        r"union\s+select",
        r"exec\s+xp_cmdshell",
        r"privilege_escalation"
    ]

    @classmethod
    def evaluate(cls, logs):
        alerts = []
        regex = re.compile("|".join(cls.RESTRICTED_KEYWORDS), re.IGNORECASE)

        for log in logs:
            desc = str(log.get("description", ""))
            payload = str(log.get("raw_payload", ""))
            action = str(log.get("action", "")).upper()
            status = str(log.get("status", "")).upper()

            is_violation = (
                regex.search(desc) or 
                regex.search(payload) or 
                status in ["FORBIDDEN", "UNAUTHORIZED", "403"] or
                "PERMISSION_DENIED" in action or
                "UNAUTHORIZED" in action
            )

            if is_violation:
                src_ip = log.get("source_ip") or "10.0.0.15"
                dest_ip = log.get("destination_ip")
                host = log.get("hostname") or "Internal API Server"
                log_id = str(log.get("id")) if "id" in log else ""

                alerts.append({
                    "attack_type": "Unauthorized Access",
                    "source_ip": src_ip,
                    "destination_ip": dest_ip,
                    "target_system": host,
                    "severity": "High",
                    "description": f"Unauthorized resource access attempt detected on {host}. Attempted path/action: '{desc or payload or action}'.",
                    "detection_rule": cls.rule_name,
                    "recommended_action": "Verify user authorization ACLs, restrict IP access, and check Web Application Firewall (WAF) rule sets.",
                    "log_ids": log_id
                })
        return alerts

class DenialOfServiceRule(DetectionRule):
    rule_id = "RULE_007_DDOS"
    rule_name = "Denial of Service / Traffic Flood"
    category = "DDoS"
    severity = "High"

    @classmethod
    def evaluate(cls, logs):
        alerts = []
        requests_by_ip = defaultdict(list)

        for log in logs:
            event_type = str(log.get("event_type", "")).upper()
            action = str(log.get("action", "")).upper()
            src_ip = log.get("source_ip")
            if src_ip and ("NETWORK" in event_type or "WEB" in event_type or "HTTP" in action or "SYN" in action):
                requests_by_ip[src_ip].append(log)

        for src_ip, ip_logs in requests_by_ip.items():
            if len(ip_logs) >= 15: # High frequency request threshold in sample batch
                dest_ip = ip_logs[0].get("destination_ip")
                host = ip_logs[0].get("hostname") or "Public Web Server"
                log_ids = [l["id"] for l in ip_logs if "id" in l]
                severity = "Critical" if len(ip_logs) >= 30 else "High"

                alerts.append({
                    "attack_type": "DDoS",
                    "source_ip": src_ip,
                    "destination_ip": dest_ip,
                    "target_system": host,
                    "severity": severity,
                    "description": f"High volume traffic surge detected: {len(ip_logs)} rapid requests from source IP {src_ip} hitting {host}.",
                    "detection_rule": cls.rule_name,
                    "recommended_action": "Activate upstream DDoS mitigation / rate limiting, enable Cloudflare/WAF challenge mode, and drop packets from source subnet.",
                    "log_ids": ",".join(str(lid) for lid in log_ids) if log_ids else ""
                })
        return alerts

class PhishingRule(DetectionRule):
    rule_id = "RULE_008_PHISHING"
    rule_name = "Phishing Indicators & Suspicious Domain Access"
    category = "Phishing"
    severity = "High"

    PHISHING_PATTERNS = [
        r"login-verify",
        r"paypa1",
        r"secure-bank-update",
        r"urgent-credential",
        r"microsoft-security-alert\.xyz",
        r"auth-support-portal\.top",
        r"invoice_overdue_\d+\.xlsm",
        r"account-suspension-warning"
    ]

    @classmethod
    def evaluate(cls, logs):
        alerts = []
        regex = re.compile("|".join(cls.PHISHING_PATTERNS), re.IGNORECASE)

        for log in logs:
            desc = str(log.get("description", ""))
            payload = str(log.get("raw_payload", ""))
            event_type = str(log.get("event_type", "")).upper()
            action = str(log.get("action", "")).upper()
            combined = f"{desc} {payload} {event_type} {action}"

            match = regex.search(combined)
            if match or "PHISHING" in combined or "MALICIOUS_LINK" in action:
                matched_text = match.group(0) if match else "Malicious Link Clicked"
                src_ip = log.get("source_ip") or "10.0.1.45"
                dest_ip = log.get("destination_ip")
                host = log.get("hostname") or "Corporate Email Gateway"
                log_id = str(log.get("id")) if "id" in log else ""

                alerts.append({
                    "attack_type": "Phishing",
                    "source_ip": src_ip,
                    "destination_ip": dest_ip,
                    "target_system": host,
                    "severity": "High",
                    "description": f"Phishing indicator detected: Employee workstation contacted suspicious credential-harvesting domain or received phishing attachment ({matched_text}).",
                    "detection_rule": cls.rule_name,
                    "recommended_action": "Block phishing domain at DNS level, quarantine related email messages, reset user credentials, and conduct user awareness briefing.",
                    "log_ids": log_id
                })
        return alerts

ALL_RULES = [
    BruteForceRule,
    PortScanningRule,
    SuspiciousLoginRule,
    MalwareIndicatorRule,
    DataExfiltrationRule,
    UnauthorizedAccessRule,
    DenialOfServiceRule,
    PhishingRule,
]
