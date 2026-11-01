from flask import Blueprint, request, jsonify, g
from datetime import datetime
from app.db import get_db
from app.models.models import Incident, Alert, SecurityLog, InvestigationNote, ResponseAction
from app.utils.helpers import login_required

incident_bp = Blueprint("incidents", __name__, url_prefix="/api/incidents")

@incident_bp.route("", methods=["GET"])
def list_incidents():
    db = get_db()
    query = db.query(Incident)

    # Filters
    severity = request.args.get("severity")
    if severity and severity != "ALL":
        query = query.filter(Incident.severity == severity)

    category = request.args.get("category")
    if category and category != "ALL":
        query = query.filter(Incident.category == category)

    status = request.args.get("status")
    if status and status != "ALL":
        query = query.filter(Incident.status == status)

    search = request.args.get("search", "").strip()
    if search:
        query = query.filter(
            (Incident.incident_id.ilike(f"%{search}%")) |
            (Incident.title.ilike(f"%{search}%")) |
            (Incident.source_ip.ilike(f"%{search}%")) |
            (Incident.affected_asset.ilike(f"%{search}%")) |
            (Incident.owner.ilike(f"%{search}%"))
        )

    incidents = query.order_by(Incident.updated_at.desc()).all()
    return jsonify([i.to_dict() for i in incidents])

@incident_bp.route("/<int:incident_id>", methods=["GET"])
def get_incident_detail(incident_id):
    db = get_db()
    incident = db.query(Incident).filter_by(id=incident_id).first()
    if not incident:
        return jsonify({"error": "Incident not found"}), 404

    # Related alerts
    alerts = db.query(Alert).filter_by(incident_id=incident.id).all()

    # Correlated security logs
    # Find logs by source IP or destination IP within a window around detection timestamp
    log_ids_set = set()
    for a in alerts:
        if a.log_ids:
            for lid in a.log_ids.split(","):
                if lid.strip().isdigit():
                    log_ids_set.add(int(lid.strip()))

    correlated_logs = []
    if log_ids_set:
        correlated_logs = db.query(SecurityLog).filter(SecurityLog.id.in_(list(log_ids_set))).all()
    
    # If explicit log_ids yielded few records, supplement with matching source_ip logs
    if len(correlated_logs) < 5 and incident.source_ip:
        more_logs = (
            db.query(SecurityLog)
            .filter(
                (SecurityLog.source_ip == incident.source_ip) |
                (SecurityLog.destination_ip == incident.source_ip)
            )
            .order_by(SecurityLog.timestamp.desc())
            .limit(10)
            .all()
        )
        existing_ids = {l.id for l in correlated_logs}
        for ml in more_logs:
            if ml.id not in existing_ids:
                correlated_logs.append(ml)

    # Investigation notes
    notes = (
        db.query(InvestigationNote)
        .filter_by(incident_id=incident.id)
        .order_by(InvestigationNote.created_at.asc())
        .all()
    )

    # Response actions
    actions = (
        db.query(ResponseAction)
        .filter_by(incident_id=incident.id)
        .order_by(ResponseAction.id.asc())
        .all()
    )

    # 6-Stage Timeline Computation
    t_det = incident.detection_timestamp or incident.created_at or datetime.utcnow()
    timeline = [
        {
            "step": 1,
            "stage": "Suspicious Activity",
            "timestamp": t_det.isoformat(),
            "status": "Completed",
            "description": f"Initial telemetry intercepted from source IP {incident.source_ip}."
        },
        {
            "step": 2,
            "stage": "Detection Event",
            "timestamp": t_det.isoformat(),
            "status": "Completed",
            "description": f"Detection rule matched pattern. Alert generated with {incident.severity} severity."
        },
        {
            "step": 3,
            "stage": "Alert Generated",
            "timestamp": t_det.isoformat(),
            "status": "Completed",
            "description": f"Alert cataloged and correlated to Incident {incident.incident_id}."
        },
        {
            "step": 4,
            "stage": "Investigation Started",
            "timestamp": incident.created_at.isoformat() if incident.created_at else t_det.isoformat(),
            "status": "Completed" if incident.status != "Open" else "In Progress",
            "description": f"Assigned to {incident.owner}. Correlating telemetry and threat intelligence."
        },
        {
            "step": 5,
            "stage": "Containment Action",
            "timestamp": incident.updated_at.isoformat() if incident.updated_at else t_det.isoformat(),
            "status": "Completed" if incident.status in ["Contained", "Resolved", "Closed"] else (
                "In Progress" if incident.status == "Investigating" else "Pending"
            ),
            "description": "Executing containment playbook actions (quarantine / firewall block / credential revocation)."
        },
        {
            "step": 6,
            "stage": "Resolution & Recovery",
            "timestamp": incident.updated_at.isoformat() if incident.status in ["Resolved", "Closed"] else None,
            "status": "Completed" if incident.status in ["Resolved", "Closed"] else "Pending",
            "description": f"Current status: {incident.status}. Post-incident security recommendations documented."
        }
    ]

    return jsonify({
        "incident": incident.to_dict(),
        "alerts": [a.to_dict() for a in alerts],
        "correlated_logs": [l.to_dict() for l in correlated_logs],
        "notes": [n.to_dict() for n in notes],
        "response_actions": [r.to_dict() for r in actions],
        "timeline": timeline
    })

@incident_bp.route("/<int:incident_id>", methods=["PATCH", "PUT"])
def update_incident(incident_id):
    db = get_db()
    incident = db.query(Incident).filter_by(id=incident_id).first()
    if not incident:
        return jsonify({"error": "Incident not found"}), 404

    data = request.get_json() or {}
    if "status" in data:
        incident.status = data["status"]
    if "severity" in data:
        incident.severity = data["severity"]
    if "owner" in data:
        incident.owner = data["owner"]
    if "title" in data:
        incident.title = data["title"]
    if "root_cause" in data:
        incident.root_cause = data["root_cause"]
    if "business_impact" in data:
        incident.business_impact = data["business_impact"]
    if "recommended_mitigation" in data:
        incident.recommended_mitigation = data["recommended_mitigation"]

    incident.updated_at = datetime.utcnow()
    db.commit()

    return jsonify({"message": "Incident updated successfully", "incident": incident.to_dict()})

@incident_bp.route("/<int:incident_id>/notes", methods=["POST"])
def add_investigation_note(incident_id):
    db = get_db()
    incident = db.query(Incident).filter_by(id=incident_id).first()
    if not incident:
        return jsonify({"error": "Incident not found"}), 404

    data = request.get_json() or {}
    note_text = data.get("note", "").strip()
    author = data.get("author", "").strip() or "Alex Vance (Lead Analyst)"

    if not note_text:
        return jsonify({"error": "Note text is required"}), 400

    new_note = InvestigationNote(
        incident_id=incident.id,
        author=author,
        note=note_text,
        created_at=datetime.utcnow()
    )
    db.add(new_note)
    incident.updated_at = datetime.utcnow()
    db.commit()

    return jsonify({"message": "Note added successfully", "note": new_note.to_dict()})

@incident_bp.route("/<int:incident_id>/actions/<int:action_id>", methods=["PATCH", "PUT"])
def update_response_action(incident_id, action_id):
    db = get_db()
    action = (
        db.query(ResponseAction)
        .filter_by(id=action_id, incident_id=incident_id)
        .first()
    )
    if not action:
        return jsonify({"error": "Response action not found"}), 404

    data = request.get_json() or {}
    if "status" in data:
        action.status = data["status"]
    if "analyst_notes" in data:
        action.analyst_notes = data["analyst_notes"]
    if "resolution_details" in data:
        action.resolution_details = data["resolution_details"]

    action.response_timestamp = datetime.utcnow()
    db.commit()

    return jsonify({"message": "Response action updated", "action": action.to_dict()})
