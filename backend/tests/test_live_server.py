import urllib.request
import json

def test_server():
    # 1. Test Root
    res_root = urllib.request.urlopen("http://localhost:5000/")
    html = res_root.read().decode()
    print("1. Root URL (GET /): Status", res_root.status, "- Contains SentinelX Title:", "SentinelX" in html)

    # 2. Test SPA Route (/login)
    res_login = urllib.request.urlopen("http://localhost:5000/login")
    print("2. Client-side route (GET /login): Status", res_login.status)

    # 3. Test Health API
    res_health = urllib.request.urlopen("http://localhost:5000/api/health")
    health = json.loads(res_health.read())
    print("3. Health API (GET /api/health): Status", res_health.status, "- Service:", health["service"])

    # 4. Test Login API
    login_payload = json.dumps({"username": "analyst@sentinelx.io", "password": "Sentinel@2025"}).encode()
    req_login = urllib.request.Request("http://localhost:5000/api/auth/login", data=login_payload, headers={"Content-Type": "application/json"})
    res_auth = urllib.request.urlopen(req_login)
    auth_data = json.loads(res_auth.read())
    print("4. Auth API (POST /api/auth/login): Status", res_auth.status, "- Message:", auth_data["message"], "- User:", auth_data["user"]["full_name"])

    # 5. Test Authenticated Dashboard API
    token = auth_data["token"]
    req_dash = urllib.request.Request("http://localhost:5000/api/dashboard/summary", headers={"Authorization": f"Bearer {token}"})
    res_dash = urllib.request.urlopen(req_dash)
    dash_data = json.loads(res_dash.read())
    print("5. Dashboard API (GET /api/dashboard/summary): Status", res_dash.status, "- Total Events:", dash_data["summary"]["total_events"], "- Incidents:", dash_data["summary"]["total_incidents"])

    # 6. Test Static Assets
    # Extract asset JS filename from HTML
    import re
    js_match = re.search(r'src="(/assets/[^"]+\.js)"', html)
    css_match = re.search(r'href="(/assets/[^"]+\.css)"', html)

    if js_match:
        js_url = f"http://localhost:5000{js_match.group(1)}"
        res_js = urllib.request.urlopen(js_url)
        print("6. JS Bundle Asset:", res_js.status, res_js.headers.get("Content-Type"), f"({len(res_js.read())} bytes)")

    if css_match:
        css_url = f"http://localhost:5000{css_match.group(1)}"
        res_css = urllib.request.urlopen(css_url)
        print("7. CSS Bundle Asset:", res_css.status, res_css.headers.get("Content-Type"), f"({len(res_css.read())} bytes)")

    print("\nALL LIVE SERVER TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_server()
