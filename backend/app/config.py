import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "sentinelx-soc-enterprise-secret-key-2025")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'sentinelx.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REPORTS_DIR = os.path.join(BASE_DIR, "reports")
    SAMPLE_DATA_DIR = os.path.join(BASE_DIR, "sample_data")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
