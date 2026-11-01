from flask import Blueprint, jsonify, request
from app.db import get_db, SessionLocal
from app.services.simulation_service import SimulationService
from app.services.seeder import seed_database
from app.models.models import (
    SecurityLog, Alert, Incident, InvestigationNote,
    ResponseAction, SimulationHistory, ThreatIntelligence, User
)

simulation_bp = Blueprint("simulation", __name__, url_prefix="/api/simulation")

@simulation_bp.route("/trigger/<attack_type>", methods=["POST"])
def trigger_simulation(attack_type):
    db = get_db()
    try:
        result = SimulationService.simulate_attack(db, attack_type)
        return jsonify({
            "status": "success",
            "message": f"Successfully simulated {result['simulation']} and evaluated detection rules.",
            "data": result
        })
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        db.rollback()
        return jsonify({"error": f"Simulation failed: {str(e)}"}), 500

@simulation_bp.route("/history", methods=["GET"])
def get_simulation_history():
    db = get_db()
    history = db.query(SimulationHistory).order_by(SimulationHistory.timestamp.desc()).limit(20).all()
    return jsonify([h.to_dict() for h in history])

@simulation_bp.route("/reset", methods=["POST"])
def reset_demo_data():
    """
    Cleans all dynamic logs, alerts, incidents, and re-seeds baseline data.
    """
    db = get_db()
    try:
        # Delete dependent tables first
        db.query(ResponseAction).delete()
        db.query(InvestigationNote).delete()
        db.query(Alert).delete()
        db.query(Incident).delete()
        db.query(SecurityLog).delete()
        db.query(SimulationHistory).delete()
        db.commit()

        # Re-seed baseline
        seed_database(db)

        return jsonify({
            "status": "success",
            "message": "Demo data successfully reset to baseline clean SOC state."
        })
    except Exception as e:
        db.rollback()
        return jsonify({"error": f"Failed to reset demo data: {str(e)}"}), 500
