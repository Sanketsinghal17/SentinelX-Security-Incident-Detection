import unittest
from datetime import datetime, timedelta
import sys
import os

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.detection_engine.rules import (
    BruteForceRule,
    PortScanningRule,
    SuspiciousLoginRule,
    MalwareIndicatorRule,
    DataExfiltrationRule,
    UnauthorizedAccessRule,
    DenialOfServiceRule,
    PhishingRule,
)

class TestDetectionEngineRules(unittest.TestCase):

    def test_01_brute_force_rule(self):
        """Rule A: Brute Force Detection (>5 failed attempts in 5 mins)"""
        now = datetime.utcnow()
        logs = []
        for i in range(6):
            logs.append({
                "timestamp": now - timedelta(seconds=(6 - i) * 10),
                "source_ip": "198.51.100.99",
                "destination_ip": "10.0.1.15",
                "username": "root",
                "event_type": "Authentication",
                "action": "LOGIN_FAILED",
                "status": "FAILED",
                "hostname": "auth-server",
                "port": 22
            })
        alerts = BruteForceRule.evaluate(logs)
        self.assertGreaterEqual(len(alerts), 1)
        self.assertEqual(alerts[0]["attack_type"], "Brute Force")
        self.assertIn("198.51.100.99", alerts[0]["description"])

    def test_02_port_scanning_rule(self):
        """Rule B: Port Scanning Detection (>= 5 distinct ports)"""
        logs = []
        now = datetime.utcnow()
        ports = [21, 22, 23, 25, 80, 443, 8080]
        for p in ports:
            logs.append({
                "timestamp": now,
                "source_ip": "203.0.113.88",
                "destination_ip": "10.0.1.50",
                "event_type": "Network",
                "action": "PORT_SWEEP_SYN",
                "status": "BLOCKED",
                "port": p,
                "hostname": "firewall-01"
            })
        alerts = PortScanningRule.evaluate(logs)
        self.assertGreaterEqual(len(alerts), 1)
        self.assertEqual(alerts[0]["attack_type"], "Port Scanning")
        self.assertIn("distinct ports", alerts[0]["description"])

    def test_03_suspicious_login_rule(self):
        """Rule C: Suspicious Login Pattern (Failed attempts followed by Success)"""
        logs = []
        now = datetime.utcnow()
        # 3 failures then 1 success
        for i in range(3):
            logs.append({
                "timestamp": now - timedelta(seconds=(4 - i) * 20),
                "source_ip": "185.220.101.55",
                "username": "victim_user",
                "event_type": "Authentication",
                "action": "LOGIN_FAILED",
                "status": "FAILED",
                "hostname": "sso-portal"
            })
        logs.append({
            "timestamp": now - timedelta(seconds=5),
            "source_ip": "185.220.101.55",
            "username": "victim_user",
            "event_type": "Authentication",
            "action": "LOGIN_SUCCESS",
            "status": "SUCCESS",
            "hostname": "sso-portal"
        })
        alerts = SuspiciousLoginRule.evaluate(logs)
        self.assertGreaterEqual(len(alerts), 1)
        self.assertEqual(alerts[0]["attack_type"], "Suspicious Login")

    def test_04_malware_indicator_rule(self):
        """Rule D: Malware Indicators (mimikatz, powershell -enc, vssadmin)"""
        logs = [{
            "timestamp": datetime.utcnow(),
            "source_ip": "10.0.2.14",
            "destination_ip": "91.240.118.88",
            "event_type": "Endpoint",
            "action": "PROCESS_SPAWN",
            "description": "Critical event: mimikatz.exe dumping credentials from lsass.exe",
            "raw_payload": "powershell -enc JABzAD0ATgBl...",
            "hostname": "workstation-05"
        }]
        alerts = MalwareIndicatorRule.evaluate(logs)
        self.assertGreaterEqual(len(alerts), 1)
        self.assertEqual(alerts[0]["attack_type"], "Malware")
        self.assertEqual(alerts[0]["severity"], "Critical")

    def test_05_data_exfiltration_rule(self):
        """Rule E: Data Exfiltration (> 15MB transfer)"""
        logs = [{
            "timestamp": datetime.utcnow(),
            "source_ip": "10.0.5.20",
            "destination_ip": "142.250.190.46",
            "event_type": "Network",
            "action": "DATA_TRANSFER_OUTBOUND",
            "bytes_sent": 22 * 1024 * 1024, # 22 MB
            "bytes_received": 1024,
            "hostname": "db-server"
        }]
        alerts = DataExfiltrationRule.evaluate(logs)
        self.assertGreaterEqual(len(alerts), 1)
        self.assertEqual(alerts[0]["attack_type"], "Data Breach")

    def test_06_unauthorized_access_rule(self):
        """Rule F: Unauthorized Access (/etc/shadow, SQL injection)"""
        logs = [{
            "timestamp": datetime.utcnow(),
            "source_ip": "172.16.88.10",
            "destination_ip": "10.0.3.50",
            "event_type": "Application",
            "action": "ACCESS_VIOLATION",
            "status": "FORBIDDEN",
            "description": "Attempted traversal to /etc/shadow with union select query",
            "hostname": "api-server"
        }]
        alerts = UnauthorizedAccessRule.evaluate(logs)
        self.assertGreaterEqual(len(alerts), 1)
        self.assertEqual(alerts[0]["attack_type"], "Unauthorized Access")

    def test_07_denial_of_service_rule(self):
        """Rule G: Denial of Service / Flood requests"""
        logs = []
        now = datetime.utcnow()
        for i in range(18):
            logs.append({
                "timestamp": now - timedelta(seconds=i),
                "source_ip": "194.26.29.50",
                "destination_ip": "10.0.3.80",
                "event_type": "Network",
                "action": "HTTP_FLOOD_REQUEST",
                "hostname": "edge-proxy"
            })
        alerts = DenialOfServiceRule.evaluate(logs)
        self.assertGreaterEqual(len(alerts), 1)
        self.assertEqual(alerts[0]["attack_type"], "DDoS")

    def test_08_phishing_indicator_rule(self):
        """Rule H: Phishing Indicators (login-verify, phishing domain, malicious excel macro)"""
        logs = [{
            "timestamp": datetime.utcnow(),
            "source_ip": "10.0.8.22",
            "destination_ip": "192.0.2.100",
            "event_type": "Application",
            "action": "MALICIOUS_LINK_CLICKED",
            "description": "Employee clicked link navigating to https://login-verify-corp.xyz/update",
            "hostname": "laptop-hr"
        }]
        alerts = PhishingRule.evaluate(logs)
        self.assertGreaterEqual(len(alerts), 1)
        self.assertEqual(alerts[0]["attack_type"], "Phishing")

if __name__ == "__main__":
    unittest.main()
