import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app

app = create_app()
client = app.test_client()

print("Static folder:", app.static_folder)
print("Static folder exists:", os.path.exists(app.static_folder) if app.static_folder else False)

paths = [
    "/",
    "/login",
    "/simulation",
    "/incidents",
    "/logs",
    "/threat-intel",
    "/analytics",
    "/reports",
    "/api/health",
    "/api/dashboard/summary",
    "/api/nonexistent_endpoint",
]

for p in paths:
    res = client.get(p)
    print(f"Path '{p}': Status {res.status_code}, Content-Type: {res.content_type}")

# Check assets
frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))
assets_dir = os.path.join(frontend_dist, "assets")
if os.path.exists(assets_dir):
    for f in os.listdir(assets_dir):
        asset_path = f"/assets/{f}"
        res = client.get(asset_path)
        print(f"Asset '{asset_path}': Status {res.status_code}, Content-Type: {res.content_type}, Length: {len(res.data)}")
