import os
import sys

# Ensure backend root is on Python sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"[*] Starting SentinelX SOC Engine on http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
