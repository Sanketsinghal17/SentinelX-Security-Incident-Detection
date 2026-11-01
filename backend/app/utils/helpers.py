import functools
from flask import jsonify, request, g
import jwt
from datetime import datetime, timedelta
from app.config import Config
from app.models.models import User

def generate_token(user_id, username, role):
    payload = {
        "user_id": user_id,
        "username": username,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, Config.SECRET_KEY, algorithm="HS256")

def decode_token(token):
    try:
        return jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
    except Exception:
        return None

def login_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            # For demonstration, permit API requests with a demo fallback if no token provided,
            # but decode if provided
            g.user_id = 1
            g.username = "analyst@sentinelx.io"
            g.role = "Security Analyst"
            return f(*args, **kwargs)

        token = auth_header.split(" ")[1]
        decoded = decode_token(token)
        if not decoded:
            return jsonify({"error": "Invalid or expired token"}), 401

        g.user_id = decoded["user_id"]
        g.username = decoded["username"]
        g.role = decoded.get("role", "Security Analyst")
        return f(*args, **kwargs)
    return decorated_function

def parse_iso_or_str(date_str):
    if not date_str:
        return datetime.utcnow()
    try:
        return datetime.fromisoformat(str(date_str).replace("Z", "+00:00"))
    except Exception:
        try:
            return datetime.strptime(str(date_str), "%Y-%m-%d %H:%M:%S")
        except Exception:
            return datetime.utcnow()
