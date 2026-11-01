from flask import Blueprint, jsonify, Response, send_file
from app.db import get_db
from app.models.models import Incident, Alert, SecurityLog
from app.services.report_service import ReportService

report_bp = Blueprint("reports", __name__, url_prefix="/api/reports")

@report_bp.route("/incident/<int:incident_id>/pdf", methods=["GET"])
def download_incident_pdf(incident_id):
    db = get_db()
    incident = db.query(Incident).filter_by(id=incident_id).first()
    if not incident:
        return jsonify({"error": "Incident not found"}), 404

    # Fetch correlated logs
    alerts = db.query(Alert).filter_by(incident_id=incident.id).all()
    log_ids_set = set()
    for a in alerts:
        if a.log_ids:
            for lid in a.log_ids.split(","):
                if lid.strip().isdigit():
                    log_ids_set.add(int(lid.strip()))

    correlated_logs = []
    if log_ids_set:
        correlated_logs = db.query(SecurityLog).filter(SecurityLog.id.in_(list(log_ids_set))).all()

    if len(correlated_logs) < 5 and incident.source_ip:
        more_logs = (
            db.query(SecurityLog)
            .filter(
                (SecurityLog.source_ip == incident.source_ip) |
                (SecurityLog.destination_ip == incident.source_ip)
            )
            .limit(10)
            .all()
        )
        existing = {l.id for l in correlated_logs}
        for ml in more_logs:
            if ml.id not in existing:
                correlated_logs.append(ml)

    try:
        pdf_bytes = ReportService.generate_incident_pdf(incident, correlated_logs)
        filename = f"SentinelX_Incident_{incident.incident_id}.pdf"
        return Response(
            pdf_bytes,
            mimetype="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        return jsonify({"error": f"Failed to generate PDF: {str(e)}"}), 500

@report_bp.route("/summary/pdf", methods=["GET"])
def download_summary_pdf():
    db = get_db()
    incidents = db.query(Incident).order_by(Incident.updated_at.desc()).all()
    alerts_count = db.query(Alert).count()
    logs_count = db.query(SecurityLog).count()

    try:
        pdf_bytes = ReportService.generate_summary_pdf(incidents, alerts_count, logs_count)
        filename = "SentinelX_Executive_Security_Summary.pdf"
        return Response(
            pdf_bytes,
            mimetype="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        return jsonify({"error": f"Failed to generate summary PDF: {str(e)}"}), 500

@report_bp.route("/incidents/csv", methods=["GET"])
def export_incidents_csv():
    db = get_db()
    incidents = db.query(Incident).order_by(Incident.id.desc()).all()
    csv_data = ReportService.export_incidents_csv(incidents)
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=sentinelx_incidents.csv"}
    )

@report_bp.route("/logs/csv", methods=["GET"])
def export_logs_csv():
    db = get_db()
    logs = db.query(SecurityLog).order_by(SecurityLog.timestamp.desc()).limit(1000).all()
    csv_data = ReportService.export_logs_csv(logs)
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=sentinelx_security_logs.csv"}
    )
