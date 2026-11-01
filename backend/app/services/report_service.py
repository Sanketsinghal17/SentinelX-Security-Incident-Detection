import io
import csv
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas
from app.models.models import Incident, Alert, SecurityLog

class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute and display total page count.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 755, "SentinelX Security Operations Center | Incident Investigation Report")
            self.setStrokeColor(colors.HexColor("#334155"))
            self.setLineWidth(0.5)
            self.line(54, 750, 558, 750)

        # Footer (all pages)
        self.setStrokeColor(colors.HexColor("#334155"))
        self.setLineWidth(0.5)
        self.line(54, 45, 558, 45)
        self.drawString(54, 32, "CONFIDENTIAL - RESTRICTED TO SOC ANALYSTS & IT SECURITY LEADERSHIP")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 32, page_str)
        self.restoreState()

class ReportService:
    """
    Enterprise PDF report and CSV data export service.
    """

    @classmethod
    def generate_incident_pdf(cls, incident, correlated_logs=None):
        """
        Generates a comprehensive 12-section PDF incident report using ReportLab.
        Returns bytes buffer.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            leftMargin=54,
            rightMargin=54,
            topMargin=54,
            bottomMargin=54
        )

        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#0f172a")
        )
        subtitle_style = ParagraphStyle(
            "DocSubtitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#475569")
        )
        h2_style = ParagraphStyle(
            "Heading2Custom",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=16,
            textColor=colors.HexColor("#1e293b"),
            spaceBefore=12,
            spaceAfter=6
        )
        body_style = ParagraphStyle(
            "BodyCustom",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=14,
            textColor=colors.HexColor("#334155")
        )
        code_style = ParagraphStyle(
            "CodeCustom",
            parent=styles["Normal"],
            fontName="Courier",
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#0f172a")
        )

        story = []

        # 1. Header & Title Banner
        story.append(Paragraph("SENTINELX SOC INCIDENT REPORT", title_style))
        story.append(Paragraph(f"Reference ID: <b>{incident.incident_id}</b> | Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}", subtitle_style))
        story.append(Spacer(1, 10))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284c7"), spaceAfter=14))

        # 2. Executive Metadata Grid
        severity_color = colors.HexColor("#ef4444") if incident.severity == "Critical" else (
            colors.HexColor("#f97316") if incident.severity == "High" else colors.HexColor("#eab308")
        )
        
        meta_data = [
            [
                Paragraph("<b>Incident Title:</b>", body_style),
                Paragraph(incident.title, body_style),
                Paragraph("<b>Severity:</b>", body_style),
                Paragraph(f"<font color='{severity_color.hexval()}'><b>{incident.severity}</b></font>", body_style)
            ],
            [
                Paragraph("<b>Category:</b>", body_style),
                Paragraph(incident.category, body_style),
                Paragraph("<b>Status:</b>", body_style),
                Paragraph(f"<b>{incident.status}</b>", body_style)
            ],
            [
                Paragraph("<b>Source IP:</b>", body_style),
                Paragraph(f"<code>{incident.source_ip}</code>", body_style),
                Paragraph("<b>Destination:</b>", body_style),
                Paragraph(f"<code>{incident.destination_ip or 'N/A'}</code>", body_style)
            ],
            [
                Paragraph("<b>Affected Asset:</b>", body_style),
                Paragraph(incident.affected_asset, body_style),
                Paragraph("<b>Incident Owner:</b>", body_style),
                Paragraph(incident.owner or "SOC Analyst", body_style)
            ],
            [
                Paragraph("<b>Detection Time:</b>", body_style),
                Paragraph(incident.detection_timestamp.strftime('%Y-%m-%d %H:%M:%S') if incident.detection_timestamp else "N/A", body_style),
                Paragraph("<b>Last Updated:</b>", body_style),
                Paragraph(incident.updated_at.strftime('%Y-%m-%d %H:%M:%S') if incident.updated_at else "N/A", body_style)
            ]
        ]
        
        meta_table = Table(meta_data, colWidths=[90, 160, 90, 160])
        meta_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ]))
        story.append(meta_table)
        story.append(Spacer(1, 14))

        # 3. Incident Summary & Description
        story.append(Paragraph("1. Incident Summary & Overview", h2_style))
        story.append(Paragraph(incident.description or "Automated detection rule triggered an alert based on anomalous activity.", body_style))
        story.append(Spacer(1, 10))

        # 4. Attack Vector & Root Cause Analysis
        story.append(Paragraph("2. Technical Attack Vector & Root Cause", h2_style))
        vector_text = f"<b>Identified Attack Vector:</b> {incident.attack_vector or 'Network reconnaissance and anomalous payload execution.'}"
        root_cause_text = f"<b>Root Cause Analysis:</b> {incident.root_cause or 'Configuration vulnerability or exposed perimeter service.'}"
        story.append(Paragraph(vector_text, body_style))
        story.append(Spacer(1, 4))
        story.append(Paragraph(root_cause_text, body_style))
        story.append(Spacer(1, 10))

        # 5. Business Impact Assessment
        story.append(Paragraph("3. Business Impact Assessment", h2_style))
        impact_text = incident.business_impact or "Potential disruption of enterprise operations, service latency, or credential exposure."
        story.append(Paragraph(impact_text, body_style))
        story.append(Spacer(1, 10))

        # 6. Incident Response Timeline (6 Stages)
        story.append(Paragraph("4. Incident Response Lifecycle Timeline", h2_style))
        t_base = incident.detection_timestamp or datetime.utcnow()
        timeline_rows = [
            ["Stage", "Milestone", "Timestamp (UTC)", "SOC Operational Status"],
            ["1. Detection", "Suspicious Telemetry Intercepted", t_base.strftime("%H:%M:%S"), "Alert Generated by Rule Engine"],
            ["2. Triage", "Classification & Priority Assigned", t_base.strftime("%H:%M:%S"), f"Categorized as {incident.category} ({incident.severity})"],
            ["3. Investigation", "Forensic Correlation & Log Analysis", t_base.strftime("%H:%M:%S"), "Analyst Assigned, Correlating Logs"],
            ["4. Containment", "Sandbox Mitigation Executed", t_base.strftime("%H:%M:%S"), "Firewall Rule / Endpoint Quarantine Applied"],
            ["5. Eradication", "Threat Artifacts Removed", t_base.strftime("%H:%M:%S"), "Malicious Sockets / Tasks Terminated"],
            ["6. Recovery", "Service Restored & Post-Mortem", t_base.strftime("%H:%M:%S"), f"Status: {incident.status}"]
        ]
        timeline_table = Table(timeline_rows, colWidths=[80, 160, 100, 160])
        timeline_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 8.5),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#94a3b8")),
            ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#ffffff")),
            ("FONTSIZE", (0, 1), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(timeline_table)
        story.append(Spacer(1, 12))

        # 7. Correlated Security Logs
        story.append(Paragraph("5. Correlated Security Telemetry & Evidence", h2_style))
        if correlated_logs and len(correlated_logs) > 0:
            log_table_data = [["Timestamp", "Source IP", "Action", "Status", "Hostname", "Port"]]
            for log in correlated_logs[:8]: # Display up to 8 correlated logs
                ts = log.timestamp.strftime("%Y-%m-%d %H:%M:%S") if hasattr(log, "timestamp") and log.timestamp else "N/A"
                log_table_data.append([
                    ts,
                    getattr(log, "source_ip", "N/A"),
                    getattr(log, "action", "N/A"),
                    getattr(log, "status", "N/A"),
                    getattr(log, "hostname", "N/A"),
                    str(getattr(log, "port", "0"))
                ])
            log_table = Table(log_table_data, colWidths=[105, 95, 110, 65, 85, 40])
            log_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 8),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("FONTSIZE", (0, 1), (-1, -1), 7.5),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]))
            story.append(log_table)
        else:
            story.append(Paragraph("<i>Telemetry linked directly to rule trigger alerts.</i>", body_style))
        story.append(Spacer(1, 10))

        # 8. Mitigation & Containment Response Actions
        story.append(Paragraph("6. Mitigation & Containment Actions", h2_style))
        actions = incident.response_actions if hasattr(incident, "response_actions") and incident.response_actions else []
        if actions:
            act_data = [["Action Title", "Action Type", "Status", "Analyst Operational Notes"]]
            for act in actions:
                act_data.append([
                    act.action_title,
                    act.action_type,
                    act.status,
                    act.analyst_notes or "Execution pending."
                ])
            act_table = Table(act_data, colWidths=[120, 100, 70, 210])
            act_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#334155")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 8),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("FONTSIZE", (0, 1), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))
            story.append(act_table)
        else:
            story.append(Paragraph(incident.recommended_mitigation or "Follow standard incident response containment playbook.", body_style))
        story.append(Spacer(1, 10))

        # 9. Future Security Recommendations
        story.append(Paragraph("7. Strategic Future Recommendations", h2_style))
        recommendations = (
            "1. Implement strict automated IP rate-limiting and geo-blocking on the border firewall.<br/>"
            "2. Enforce Mandatory Multi-Factor Authentication (MFA) across all remote access and administrative portals.<br/>"
            "3. Harden endpoint EDR policies with automated process-tree memory inspection.<br/>"
            "4. Conduct regular simulated phishing awareness drills for corporate personnel."
        )
        story.append(Paragraph(recommendations, body_style))
        story.append(Spacer(1, 16))

        # Sign-off footer block
        sign_data = [
            [Paragraph("<b>Lead Security Analyst:</b>", body_style), Paragraph("___________________________", body_style),
             Paragraph("<b>SOC Lead Approval:</b>", body_style), Paragraph("___________________________", body_style)]
        ]
        sign_table = Table(sign_data, colWidths=[130, 120, 130, 120])
        sign_table.setStyle(TableStyle([("TOPPADDING", (0,0), (-1,-1), 8)]))
        story.append(KeepTogether(sign_table))

        doc.build(story, canvasmaker=NumberedCanvas)
        buffer.seek(0)
        return buffer.getvalue()

    @classmethod
    def generate_summary_pdf(cls, incidents, alerts_count, logs_count):
        """
        Generates an Executive Security Operations Summary Report PDF.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            leftMargin=54,
            rightMargin=54,
            topMargin=54,
            bottomMargin=54
        )
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#0f172a")
        )
        subtitle_style = ParagraphStyle(
            "DocSubtitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#475569")
        )
        h2_style = ParagraphStyle(
            "Heading2Custom",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=16,
            textColor=colors.HexColor("#1e293b"),
            spaceBefore=14,
            spaceAfter=6
        )
        body_style = ParagraphStyle(
            "BodyCustom",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=14,
            textColor=colors.HexColor("#334155")
        )

        story = []

        # Title
        story.append(Paragraph("SENTINELX SOC EXECUTIVE SUMMARY", title_style))
        story.append(Paragraph(f"Enterprise Security Posture & Incident Overview | {datetime.utcnow().strftime('%B %Y')}", subtitle_style))
        story.append(Spacer(1, 10))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284c7"), spaceAfter=14))

        # KPI Metrics Box
        crit_count = sum(1 for i in incidents if i.severity == "Critical")
        high_count = sum(1 for i in incidents if i.severity == "High")
        resolved_count = sum(1 for i in incidents if i.status in ["Resolved", "Closed"])

        kpi_data = [
            [
                Paragraph("<b>Total Telemetry Logs:</b>", body_style), Paragraph(str(logs_count), body_style),
                Paragraph("<b>Total Security Alerts:</b>", body_style), Paragraph(str(alerts_count), body_style)
            ],
            [
                Paragraph("<b>Total Incidents:</b>", body_style), Paragraph(str(len(incidents)), body_style),
                Paragraph("<b>Critical Incidents:</b>", body_style), Paragraph(f"<font color='#ef4444'><b>{crit_count}</b></font>", body_style)
            ],
            [
                Paragraph("<b>High Incidents:</b>", body_style), Paragraph(f"<font color='#f97316'><b>{high_count}</b></font>", body_style),
                Paragraph("<b>Resolved Incidents:</b>", body_style), Paragraph(f"<font color='#22c55e'><b>{resolved_count}</b></font>", body_style)
            ]
        ]
        kpi_table = Table(kpi_data, colWidths=[130, 120, 130, 120])
        kpi_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ]))
        story.append(kpi_table)
        story.append(Spacer(1, 14))

        # Table of Active & Recent Incidents
        story.append(Paragraph("Active & Cataloged Incidents", h2_style))
        inc_data = [["Incident ID", "Title", "Category", "Severity", "Status", "Source IP"]]
        for inc in incidents[:12]:
            inc_data.append([
                inc.incident_id,
                inc.title[:24] + ("..." if len(inc.title) > 24 else ""),
                inc.category,
                inc.severity,
                inc.status,
                inc.source_ip
            ])
        inc_table = Table(inc_data, colWidths=[90, 140, 90, 60, 60, 60])
        inc_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 8),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#94a3b8")),
            ("FONTSIZE", (0, 1), (-1, -1), 7.5),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(inc_table)
        story.append(Spacer(1, 14))

        # Recommendations
        story.append(Paragraph("Executive Recommendations for Threat Mitigation", h2_style))
        story.append(Paragraph(
            "Based on analysis of ingested security events, prioritized remediation should focus on credential protection against distributed brute-force attacks, boundary rate-limiting against volumetric DDoS traffic, and EDR automated isolation for host malware execution.",
            body_style
        ))

        doc.build(story, canvasmaker=NumberedCanvas)
        buffer.seek(0)
        return buffer.getvalue()

    @classmethod
    def export_incidents_csv(cls, incidents):
        """
        Exports incidents to CSV string.
        """
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "Incident ID", "Title", "Category", "Severity", "Status",
            "Source IP", "Destination IP", "Affected Asset", "Detection Timestamp",
            "Owner", "Attack Vector", "Root Cause", "Business Impact"
        ])

        for inc in incidents:
            writer.writerow([
                inc.incident_id,
                inc.title,
                inc.category,
                inc.severity,
                inc.status,
                inc.source_ip,
                inc.destination_ip or "",
                inc.affected_asset,
                inc.detection_timestamp.isoformat() if inc.detection_timestamp else "",
                inc.owner,
                inc.attack_vector or "",
                inc.root_cause or "",
                inc.business_impact or ""
            ])
        return output.getvalue()

    @classmethod
    def export_logs_csv(cls, logs):
        """
        Exports security logs to CSV string.
        """
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "Log ID", "Timestamp", "Source IP", "Destination IP", "Username",
            "Event Type", "Action", "Protocol", "Status", "Hostname", "Port",
            "Bytes Sent", "Bytes Received", "Description"
        ])

        for log in logs:
            writer.writerow([
                log.id,
                log.timestamp.isoformat() if log.timestamp else "",
                log.source_ip,
                log.destination_ip,
                log.username,
                log.event_type,
                log.action,
                log.protocol,
                log.status,
                log.hostname,
                log.port,
                log.bytes_sent,
                log.bytes_received,
                log.description
            ])
        return output.getvalue()
