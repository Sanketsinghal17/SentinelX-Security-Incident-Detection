from flask import Blueprint, jsonify, request
from app.db import get_db
from app.services.threat_service import ThreatService
from app.models.models import ThreatIntelligence

threat_bp = Blueprint("threat", __name__, url_prefix="/api/threat-intel")

@threat_bp.route("/lookup/<path:ip_address>", methods=["GET"])
def lookup_ip(ip_address):
    db = get_db()
    ip_clean = ip_address.strip()
    result = ThreatService.lookup_ip(db, ip_clean)
    return jsonify(result)

@threat_bp.route("/list", methods=["GET"])
def list_threats():
    db = get_db()
    threats = ThreatService.get_all_threats(db)
    return jsonify(threats)

@threat_bp.route("/indicators", methods=["POST"])
def add_threat_indicator():
    db = get_db()
    data = request.get_json() or {}
    ip = data.get("ip_address", "").strip()
    
    if not ip:
        return jsonify({"error": "IP address is required"}), 400

    existing = db.query(ThreatIntelligence).filter_by(ip_address=ip).first()
    if existing:
        existing.reputation_score = int(data.get("reputation_score", existing.reputation_score))
        existing.threat_type = data.get("threat_type", existing.threat_type)
        existing.is_known_attacker = bool(data.get("is_known_attacker", existing.is_known_attacker))
        existing.notes = data.get("notes", existing.notes)
        db.commit()
        return jsonify({"message": "Indicator updated", "data": existing.to_dict()})

    new_threat = ThreatIntelligence(
        ip_address=ip,
        reputation_score=int(data.get("reputation_score", 75)),
        threat_type=data.get("threat_type", "Manual SOC Indicator"),
        country=data.get("country", "Unknown"),
        isp=data.get("isp", "Unknown ISP"),
        is_known_attacker=bool(data.get("is_known_attacker", True)),
        reports_count=int(data.get("reports_count", 1)),
        notes=data.get("notes", "Manually cataloged indicator by SOC analyst.")
    )
    db.add(new_threat)
    db.commit()
    return jsonify({"message": "Threat indicator cataloged", "data": new_threat.to_dict()})
