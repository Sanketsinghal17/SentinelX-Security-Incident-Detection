import json
import csv
import io
import os
from datetime import datetime
from flask import Blueprint, request, jsonify, send_file, Response
from app.db import get_db
from app.models.models import SecurityLog
from app.detection_engine.engine import DetectionEngine
from app.utils.helpers import parse_iso_or_str
from app.config import Config

log_bp = Blueprint("logs", __name__, url_prefix="/api/logs")

@log_bp.route("/list", methods=["GET"])
def list_logs():
    db = get_db()
    query = db.query(SecurityLog)

    # Search query parameter (searches across IP, username, description, hostname)
    search = request.args.get("search", "").strip().lower()
    if search:
        query = query.filter(
            (SecurityLog.source_ip.ilike(f"%{search}%")) |
            (SecurityLog.destination_ip.ilike(f"%{search}%")) |
            (SecurityLog.username.ilike(f"%{search}%")) |
            (SecurityLog.hostname.ilike(f"%{search}%")) |
            (SecurityLog.description.ilike(f"%{search}%")) |
            (SecurityLog.event_type.ilike(f"%{search}%"))
        )

    # Category / Event Type filter
    event_type = request.args.get("event_type", "").strip()
    if event_type and event_type != "ALL":
        query = query.filter(SecurityLog.event_type == event_type)

    # Status filter
    status = request.args.get("status", "").strip()
    if status and status != "ALL":
        query = query.filter(SecurityLog.status == status)

    # Date filters
    start_date = request.args.get("start_date")
    if start_date:
        query = query.filter(SecurityLog.timestamp >= parse_iso_or_str(start_date))

    end_date = request.args.get("end_date")
    if end_date:
        query = query.filter(SecurityLog.timestamp <= parse_iso_or_str(end_date))

    # Pagination
    total = query.count()
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))
    offset = (page - 1) * per_page

    logs = query.order_by(SecurityLog.timestamp.desc()).offset(offset).limit(per_page).all()

    return jsonify({
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page,
        "logs": [l.to_dict() for l in logs]
    })

@log_bp.route("/upload", methods=["POST"])
def upload_logs():
    if "file" not in request.files:
        return jsonify({"error": "No file part in upload request"}), 400

    file = request.files["file"]
    if not file or file.filename == "":
        return jsonify({"error": "No file selected for upload"}), 400

    filename = file.filename.lower()
    raw_content = file.read().decode("utf-8", errors="replace")
    
    parsed_records = []
    
    try:
        if filename.endswith(".json"):
            data = json.loads(raw_content)
            if isinstance(data, list):
                parsed_records = data
            elif isinstance(data, dict):
                parsed_records = data.get("logs", [data])
            else:
                return jsonify({"error": "Invalid JSON log structure"}), 400

        elif filename.endswith(".csv"):
            reader = csv.DictReader(io.StringIO(raw_content))
            for row in reader:
                parsed_records.append(dict(row))
        else:
            return jsonify({"error": "Unsupported file format. Please upload a CSV or JSON log file."}), 400

    except Exception as e:
        return jsonify({"error": f"Failed to parse log file: {str(e)}"}), 400

    if not parsed_records:
        return jsonify({"error": "Log file is empty or contains no records."}), 400

    db = get_db()
    saved_models = []
    duplicates = 0

    for item in parsed_records:
        ts = parse_iso_or_str(item.get("timestamp") or item.get("time") or item.get("date"))
        src_ip = item.get("source_ip") or item.get("src_ip") or item.get("source") or "10.0.0.1"
        dest_ip = item.get("destination_ip") or item.get("dest_ip") or item.get("dst_ip") or "10.0.0.2"
        user = item.get("username") or item.get("user") or "system"
        evt_type = item.get("event_type") or item.get("category") or "System"
        action = item.get("action") or item.get("event") or "LOG_ENTRY"
        proto = item.get("protocol") or item.get("proto") or "TCP"
        status = item.get("status") or item.get("result") or "SUCCESS"
        desc = item.get("description") or item.get("message") or item.get("details") or ""
        host = item.get("hostname") or item.get("host") or item.get("device") or "endpoint-01"
        port = int(item.get("port") or 0) if str(item.get("port", "")).isdigit() else 0
        b_sent = int(item.get("bytes_sent") or 0) if str(item.get("bytes_sent", "")).isdigit() else 0
        b_recv = int(item.get("bytes_received") or 0) if str(item.get("bytes_received", "")).isdigit() else 0
        raw_p = item.get("raw_payload") or item.get("payload") or str(item)

        # Basic duplicate suppression
        existing = db.query(SecurityLog).filter_by(
            timestamp=ts,
            source_ip=src_ip,
            action=action,
            description=desc
        ).first()

        if existing:
            duplicates += 1
            continue

        log_model = SecurityLog(
            timestamp=ts,
            source_ip=src_ip,
            destination_ip=dest_ip,
            username=user,
            event_type=evt_type,
            action=action,
            protocol=proto,
            status=status,
            description=desc,
            hostname=host,
            port=port,
            bytes_sent=b_sent,
            bytes_received=b_recv,
            raw_payload=raw_p
        )
        db.add(log_model)
        saved_models.append(log_model)

    db.commit()

    # Automatically run Detection Engine on newly imported logs
    detection_summary = {"alerts_created": 0, "incidents_created": 0, "alerts": [], "incidents": []}
    if saved_models:
        detection_summary = DetectionEngine.process_logs(db, saved_models)

    return jsonify({
        "message": f"Successfully processed {len(parsed_records)} log entries.",
        "imported_count": len(saved_models),
        "duplicate_count": duplicates,
        "detection_engine": {
            "alerts_created": detection_summary["alerts_created"],
            "incidents_created": detection_summary["incidents_created"],
            "incidents": detection_summary["incidents"]
        }
    })

@log_bp.route("/sample/<format_type>", methods=["GET"])
def download_sample_log(format_type):
    """
    Provides downloadable sample CSV or JSON security logs for demonstration.
    """
    sample_dir = Config.SAMPLE_DATA_DIR
    if format_type.lower() == "csv":
        sample_path = os.path.join(sample_dir, "sample_firewall_logs.csv")
        mimetype = "text/csv"
        filename = "sentinelx_sample_security_logs.csv"
    elif format_type.lower() == "json":
        sample_path = os.path.join(sample_dir, "sample_auth_logs.json")
        mimetype = "application/json"
        filename = "sentinelx_sample_security_logs.json"
    else:
        return jsonify({"error": "Format must be 'csv' or 'json'"}), 400

    if not os.path.exists(sample_path):
        return jsonify({"error": "Sample file not found."}), 404

    return send_file(sample_path, mimetype=mimetype, as_attachment=True, download_name=filename)
