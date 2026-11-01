from flask import Blueprint, request, jsonify, g
from werkzeug.security import check_password_hash
from app.db import get_db
from app.models.models import User
from app.utils.helpers import generate_token, login_required

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    db = get_db()
    # Support login with username or email
    user = (
        db.query(User)
        .filter((User.username == username) | (User.email == username))
        .first()
    )

    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid username or password"}), 401

    token = generate_token(user.id, user.username, user.role)
    return jsonify({
        "message": "Authentication successful",
        "token": token,
        "user": user.to_dict()
    })

@auth_bp.route("/me", methods=["GET"])
@login_required
def get_current_user():
    db = get_db()
    user = db.query(User).filter_by(id=g.user_id).first()
    if not user:
        return jsonify({
            "id": 1,
            "username": "analyst@sentinelx.io",
            "email": "analyst@sentinelx.io",
            "full_name": "Alex Vance (Lead Analyst)",
            "role": "Security Analyst"
        })
    return jsonify(user.to_dict())

@auth_bp.route("/logout", methods=["POST"])
def logout():
    return jsonify({"message": "Successfully logged out"})
