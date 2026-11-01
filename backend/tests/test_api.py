import unittest
import json
import io
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from app.db import get_db
from app.models.models import Incident, User, Alert, SecurityLog

class TestSentinelXAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client()

    def test_01_health_check(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "online")

    def test_02_auth_login(self):
        res = self.client.post("/api/auth/login", json={
            "username": "analyst@sentinelx.io",
            "password": "Sentinel@2025"
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("token", data)
        self.assertEqual(data["user"]["email"], "analyst@sentinelx.io")

    def test_03_dashboard_summary_and_charts(self):
        res = self.client.get("/api/dashboard/summary")
        self.assertEqual(res.status_code, 200)
        summary = res.get_json()["summary"]
        self.assertIn("total_events", summary)
        self.assertIn("total_incidents", summary)

        res_charts = self.client.get("/api/dashboard/charts")
        self.assertEqual(res_charts.status_code, 200)
        charts = res_charts.get_json()
        self.assertIn("severity_distribution", charts)
        self.assertIn("attack_type_distribution", charts)

    def test_04_logs_list_and_sample_download(self):
        res = self.client.get("/api/logs/list")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("logs", data)

        res_csv = self.client.get("/api/logs/sample/csv")
        self.assertEqual(res_csv.status_code, 200)
        self.assertIn("text/csv", res_csv.content_type)

    def test_05_incidents_api(self):
        res = self.client.get("/api/incidents")
        self.assertEqual(res.status_code, 200)
        incidents = res.get_json()
        self.assertIsInstance(incidents, list)
        self.assertGreaterEqual(len(incidents), 1)

        first_id = incidents[0]["id"]
        res_detail = self.client.get(f"/api/incidents/{first_id}")
        self.assertEqual(res_detail.status_code, 200)
        detail = res_detail.get_json()
        self.assertIn("incident", detail)
        self.assertIn("timeline", detail)
        self.assertIn("response_actions", detail)

        # Test adding a note
        res_note = self.client.post(f"/api/incidents/{first_id}/notes", json={
            "author": "Test Analyst",
            "note": "Automated verification note: threat isolated."
        })
        self.assertEqual(res_note.status_code, 200)

    def test_06_simulations_all_eight(self):
        attacks = [
            "brute_force",
            "port_scan",
            "suspicious_login",
            "malware",
            "data_exfiltration",
            "unauthorized_access",
            "ddos",
            "phishing"
        ]
        for atk in attacks:
            res = self.client.post(f"/api/simulation/trigger/{atk}")
            self.assertEqual(res.status_code, 200, f"Simulation {atk} failed: {res.data}")
            data = res.get_json()
            self.assertEqual(data["status"], "success")
            self.assertGreaterEqual(data["data"]["alerts_created"], 1, f"No alert created for {atk}")

    def test_07_threat_intelligence_lookup(self):
        res = self.client.get("/api/threat-intel/lookup/185.220.101.45")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["ip_address"], "185.220.101.45")
        self.assertGreaterEqual(data["reputation_score"], 80)

    def test_08_analytics_trends(self):
        res = self.client.get("/api/analytics/trends")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("attack_type_breakdown", data)
        self.assertIn("resolution_metrics", data)

    def test_09_pdf_and_csv_reports(self):
        # 1. Incident PDF
        res = self.client.get("/api/incidents")
        inc_id = res.get_json()[0]["id"]
        pdf_res = self.client.get(f"/api/reports/incident/{inc_id}/pdf")
        self.assertEqual(pdf_res.status_code, 200)
        self.assertEqual(pdf_res.content_type, "application/pdf")
        self.assertTrue(pdf_res.data.startswith(b"%PDF"))

        # 2. Executive Summary PDF
        sum_res = self.client.get("/api/reports/summary/pdf")
        self.assertEqual(sum_res.status_code, 200)
        self.assertEqual(sum_res.content_type, "application/pdf")
        self.assertTrue(sum_res.data.startswith(b"%PDF"))

        # 3. Incidents CSV
        csv_res = self.client.get("/api/reports/incidents/csv")
        self.assertEqual(csv_res.status_code, 200)
        self.assertIn("Incident ID", csv_res.data.decode())

        # 4. Logs CSV
        logs_csv_res = self.client.get("/api/reports/logs/csv")
        self.assertEqual(logs_csv_res.status_code, 200)
        self.assertIn("Log ID", logs_csv_res.data.decode())

if __name__ == "__main__":
    unittest.main()
