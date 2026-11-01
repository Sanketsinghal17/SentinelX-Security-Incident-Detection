from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, ForeignKey
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(120), nullable=False, default="SOC Analyst")
    role = Column(String(50), nullable=False, default="Security Analyst")
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

class SecurityLog(Base):
    __tablename__ = "security_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    source_ip = Column(String(45), nullable=False, default="0.0.0.0")
    destination_ip = Column(String(45), nullable=False, default="127.0.0.1")
    username = Column(String(80), nullable=True, default="system")
    event_type = Column(String(50), nullable=False, default="System") # Authentication, Network, Firewall, System, Application, Endpoint
    action = Column(String(50), nullable=False, default="INFO")
    protocol = Column(String(20), nullable=True, default="TCP")
    status = Column(String(30), nullable=False, default="SUCCESS") # SUCCESS, FAILED, BLOCKED, ALLOWED, ALERT
    description = Column(Text, nullable=True)
    hostname = Column(String(100), nullable=True, default="corp-host-01")
    port = Column(Integer, nullable=True, default=0)
    bytes_sent = Column(Integer, nullable=True, default=0)
    bytes_received = Column(Integer, nullable=True, default=0)
    raw_payload = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "source_ip": self.source_ip,
            "destination_ip": self.destination_ip,
            "username": self.username,
            "event_type": self.event_type,
            "action": self.action,
            "protocol": self.protocol,
            "status": self.status,
            "description": self.description,
            "hostname": self.hostname,
            "port": self.port,
            "bytes_sent": self.bytes_sent,
            "bytes_received": self.bytes_received,
            "raw_payload": self.raw_payload,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    alert_id = Column(String(50), unique=True, nullable=False)
    detection_timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    attack_type = Column(String(80), nullable=False)
    source_ip = Column(String(45), nullable=False)
    destination_ip = Column(String(45), nullable=True)
    target_system = Column(String(100), nullable=False)
    severity = Column(String(20), nullable=False) # Low, Medium, High, Critical
    description = Column(Text, nullable=False)
    detection_rule = Column(String(100), nullable=False)
    recommended_action = Column(Text, nullable=True)
    investigation_status = Column(String(30), nullable=False, default="New") # New, Under Review, Incident Created, Closed
    log_ids = Column(Text, nullable=True) # Comma-separated or JSON string of log IDs
    incident_id = Column(Integer, ForeignKey("incidents.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "alert_id": self.alert_id,
            "detection_timestamp": self.detection_timestamp.isoformat() if self.detection_timestamp else None,
            "attack_type": self.attack_type,
            "source_ip": self.source_ip,
            "destination_ip": self.destination_ip,
            "target_system": self.target_system,
            "severity": self.severity,
            "description": self.description,
            "detection_rule": self.detection_rule,
            "recommended_action": self.recommended_action,
            "investigation_status": self.investigation_status,
            "log_ids": self.log_ids,
            "incident_id": self.incident_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    incident_id = Column(String(50), unique=True, nullable=False)
    title = Column(String(200), nullable=False)
    category = Column(String(50), nullable=False) # Malware, Phishing, DDoS, Insider Threat, Brute Force, Data Breach, Port Scanning, Unauthorized Access
    severity = Column(String(20), nullable=False) # Low, Medium, High, Critical
    status = Column(String(30), nullable=False, default="Open") # Open, Investigating, Contained, Resolved, Closed
    source_ip = Column(String(45), nullable=False)
    destination_ip = Column(String(45), nullable=True)
    affected_asset = Column(String(100), nullable=False)
    detection_timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    description = Column(Text, nullable=False)
    attack_vector = Column(String(150), nullable=True)
    root_cause = Column(Text, nullable=True)
    business_impact = Column(Text, nullable=True)
    recommended_mitigation = Column(Text, nullable=True)
    owner = Column(String(80), nullable=False, default="Unassigned")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    alerts = relationship("Alert", backref="incident", lazy="select")
    notes = relationship("InvestigationNote", backref="incident", cascade="all, delete-orphan", lazy="select")
    response_actions = relationship("ResponseAction", backref="incident", cascade="all, delete-orphan", lazy="select")

    def to_dict(self):
        return {
            "id": self.id,
            "incident_id": self.incident_id,
            "title": self.title,
            "category": self.category,
            "severity": self.severity,
            "status": self.status,
            "source_ip": self.source_ip,
            "destination_ip": self.destination_ip,
            "affected_asset": self.affected_asset,
            "detection_timestamp": self.detection_timestamp.isoformat() if self.detection_timestamp else None,
            "description": self.description,
            "attack_vector": self.attack_vector,
            "root_cause": self.root_cause,
            "business_impact": self.business_impact,
            "recommended_mitigation": self.recommended_mitigation,
            "owner": self.owner,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "alerts_count": len(self.alerts) if self.alerts else 0,
        }

class InvestigationNote(Base):
    __tablename__ = "investigation_notes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    incident_id = Column(Integer, ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False)
    author = Column(String(80), nullable=False)
    note = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "incident_id": self.incident_id,
            "author": self.author,
            "note": self.note,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

class ResponseAction(Base):
    __tablename__ = "response_actions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    incident_id = Column(Integer, ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False)
    action_title = Column(String(150), nullable=False)
    action_type = Column(String(50), nullable=False) # Firewall Block, Endpoint Isolation, Credential Reset, Rate Limiting, Threat Hunting, Policy Update
    status = Column(String(30), nullable=False, default="Pending") # Pending, In Progress, Completed
    analyst_notes = Column(Text, nullable=True)
    response_timestamp = Column(DateTime, nullable=True)
    resolution_details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "incident_id": self.incident_id,
            "action_title": self.action_title,
            "action_type": self.action_type,
            "status": self.status,
            "analyst_notes": self.analyst_notes,
            "response_timestamp": self.response_timestamp.isoformat() if self.response_timestamp else None,
            "resolution_details": self.resolution_details,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

class ThreatIntelligence(Base):
    __tablename__ = "threat_intelligence"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ip_address = Column(String(45), unique=True, nullable=False)
    reputation_score = Column(Integer, nullable=False, default=50) # 0 to 100 (100 = critical threat)
    threat_type = Column(String(80), nullable=False, default="Suspicious Host")
    country = Column(String(60), nullable=False, default="Unknown")
    isp = Column(String(120), nullable=False, default="Unknown ISP")
    is_known_attacker = Column(Boolean, default=False)
    reports_count = Column(Integer, default=1)
    last_seen = Column(DateTime, default=datetime.utcnow)
    source_type = Column(String(50), default="Local Threat DB")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "ip_address": self.ip_address,
            "reputation_score": self.reputation_score,
            "threat_type": self.threat_type,
            "country": self.country,
            "isp": self.isp,
            "is_known_attacker": self.is_known_attacker,
            "reports_count": self.reports_count,
            "last_seen": self.last_seen.isoformat() if self.last_seen else None,
            "source_type": self.source_type,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

class SimulationHistory(Base):
    __tablename__ = "simulation_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    simulation_name = Column(String(100), nullable=False)
    attack_type = Column(String(80), nullable=False)
    logs_generated = Column(Integer, default=0)
    alerts_generated = Column(Integer, default=0)
    incidents_created = Column(Integer, default=0)
    status = Column(String(30), default="Completed")
    timestamp = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "simulation_name": self.simulation_name,
            "attack_type": self.attack_type,
            "logs_generated": self.logs_generated,
            "alerts_generated": self.alerts_generated,
            "incidents_created": self.incidents_created,
            "status": self.status,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }
