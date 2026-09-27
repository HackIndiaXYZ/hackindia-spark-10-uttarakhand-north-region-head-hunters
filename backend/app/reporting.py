"""Read-only investigation report assembly for CHITRAGUPT cases."""

import csv
import json
from io import BytesIO, StringIO
from datetime import datetime
from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sqlalchemy import select

from .database import SessionLocal
from .models import Anomaly, Case, Evidence, Event, Finding


def _isoformat(value: datetime | None) -> str | None:
    return value.isoformat() if value is not None else None


def build_investigation_report(case_id: int) -> dict[str, Any]:
    """Build a JSON-serializable report from persisted case data."""
    session = SessionLocal()
    try:
        case = session.scalar(select(Case).where(Case.id == case_id))
        if case is None:
            raise ValueError(f"Case {case_id} not found.")

        evidence_items = session.scalars(
            select(Evidence)
            .where(Evidence.case_id == case_id)
            .order_by(Evidence.id.asc())
        ).all()
        events = session.scalars(
            select(Event)
            .where(Event.case_id == case_id)
            .order_by(Event.timestamp.asc(), Event.id.asc())
        ).all()
        anomalies = session.scalars(
            select(Anomaly)
            .where(Anomaly.case_id == case_id)
            .order_by(Anomaly.id.asc())
        ).all()
        findings = session.scalars(
            select(Finding)
            .where(Finding.case_id == case_id)
            .order_by(Finding.id.asc())
        ).all()

        return {
            "case": {
                "id": case.id,
                "case_number": case.case_number,
                "title": case.title,
                "description": case.description,
                "status": case.status,
                "created_at": _isoformat(case.created_at),
                "updated_at": _isoformat(case.updated_at),
            },
            "evidence": [
                {
                    "id": evidence.id,
                    "case_id": evidence.case_id,
                    "filename": evidence.filename,
                    "source": evidence.source,
                    "evidence_type": evidence.evidence_type,
                    "file_size": evidence.file_size,
                    "sha256": evidence.sha256,
                    "ingested_at": _isoformat(evidence.ingested_at),
                    "processing_status": evidence.processing_status,
                }
                for evidence in evidence_items
            ],
            "events": [
                {
                    "id": event.id,
                    "case_id": event.case_id,
                    "evidence_id": event.evidence_id,
                    "timestamp": _isoformat(event.timestamp),
                    "event_type": event.event_type,
                    "source": event.source,
                    "user": event.user,
                    "device": event.device,
                    "ip_address": event.ip_address,
                    "application": event.application,
                    "process": event.process,
                    "file_path": event.file_path,
                    "description": event.description,
                    "raw_data": event.raw_data,
                }
                for event in events
            ],
            "anomalies": [
                {
                    "id": anomaly.id,
                    "case_id": anomaly.case_id,
                    "event_id": anomaly.event_id,
                    "model_name": anomaly.model_name,
                    "anomaly_score": anomaly.anomaly_score,
                    "is_anomaly": anomaly.is_anomaly,
                    "created_at": _isoformat(anomaly.created_at),
                }
                for anomaly in anomalies
            ],
            "findings": [
                {
                    "id": finding.id,
                    "case_id": finding.case_id,
                    "finding_type": finding.finding_type,
                    "title": finding.title,
                    "description": finding.description,
                    "supporting_event_ids": finding.supporting_event_ids,
                    "confidence": finding.confidence,
                    "status": finding.status,
                    "created_at": _isoformat(finding.created_at),
                }
                for finding in findings
            ],
        }
    finally:
        session.close()


def generate_json_report(case_id: int) -> str:
    """Return the complete investigation report as formatted JSON."""
    report = build_investigation_report(case_id)
    return json.dumps(report, indent=2, sort_keys=True)


def _csv_value(value: Any) -> Any:
    if isinstance(value, (dict, list)):
        return json.dumps(value, sort_keys=True)
    return value


def generate_csv_report(case_id: int) -> str:
    """Return the investigation report as deterministic, sectioned CSV text."""
    report = build_investigation_report(case_id)
    output = StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")

    sections = (
        ("case", report["case"]),
        ("evidence", report["evidence"]),
        ("events", report["events"]),
        ("anomalies", report["anomalies"]),
        ("findings", report["findings"]),
    )
    for section_name, section in sections:
        writer.writerow([section_name])
        if isinstance(section, dict):
            columns = list(section)
            writer.writerow(columns)
            writer.writerow([_csv_value(section[column]) for column in columns])
        else:
            columns = list(section[0]) if section else []
            writer.writerow(columns)
            for item in section:
                writer.writerow([_csv_value(item[column]) for column in columns])
        writer.writerow([])

    return output.getvalue()


def _pdf_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, sort_keys=True)
    return str(value)


def _pdf_table(
    title: str,
    rows: list[dict[str, Any]],
    columns: tuple[str, ...],
    styles: dict[str, ParagraphStyle],
) -> list[Any]:
    content: list[Any] = [Paragraph(title, styles["section"])]
    if not rows:
        content.append(Paragraph("No records.", styles["body"]))
        content.append(Spacer(1, 0.12 * inch))
        return content

    table_data = [
        [Paragraph(column.replace("_", " ").title(), styles["table_header"]) for column in columns]
    ]
    table_data.extend(
        [Paragraph(_pdf_value(row[column]), styles["table_cell"]) for column in columns]
        for row in rows
    )
    table = Table(table_data, repeatRows=1, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#9ca3af")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3f4f6")]),
            ]
        )
    )
    content.extend([table, Spacer(1, 0.16 * inch)])
    return content


def generate_pdf_report(case_id: int) -> bytes:
    """Return a readable in-memory PDF investigation report."""
    report = build_investigation_report(case_id)
    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.45 * inch,
        leftMargin=0.45 * inch,
        topMargin=0.45 * inch,
        bottomMargin=0.45 * inch,
        title="CHITRAGUPT Investigation Report",
    )
    stylesheet = getSampleStyleSheet()
    styles = {
        "title": ParagraphStyle(
            "ReportTitle",
            parent=stylesheet["Title"],
            alignment=TA_LEFT,
            spaceAfter=12,
        ),
        "section": ParagraphStyle(
            "ReportSection",
            parent=stylesheet["Heading2"],
            textColor=colors.HexColor("#111827"),
            spaceBefore=8,
            spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "ReportBody",
            parent=stylesheet["BodyText"],
            fontSize=9,
            leading=11,
        ),
        "table_header": ParagraphStyle(
            "ReportTableHeader",
            parent=stylesheet["BodyText"],
            fontSize=7,
            leading=8,
            textColor=colors.white,
        ),
        "table_cell": ParagraphStyle(
            "ReportTableCell",
            parent=stylesheet["BodyText"],
            fontSize=7,
            leading=8,
        ),
    }

    story: list[Any] = [
        Paragraph("CHITRAGUPT Investigation Report", styles["title"]),
        Paragraph(
            f"Case {report['case']['case_number']}: {report['case']['title']}",
            styles["body"],
        ),
        Paragraph(
            f"Status: {_pdf_value(report['case']['status'])} | "
            f"Created: {_pdf_value(report['case']['created_at'])} | "
            f"Updated: {_pdf_value(report['case']['updated_at'])}",
            styles["body"],
        ),
        Paragraph(_pdf_value(report["case"]["description"]), styles["body"]),
        Spacer(1, 0.12 * inch),
    ]
    story.extend(
        _pdf_table(
            "Evidence",
            report["evidence"],
            (
                "id",
                "filename",
                "source",
                "evidence_type",
                "file_size",
                "sha256",
                "ingested_at",
                "processing_status",
            ),
            styles,
        )
    )
    story.extend(
        _pdf_table(
            "Event Timeline",
            report["events"],
            ("id", "timestamp", "event_type", "source", "user", "device", "description"),
            styles,
        )
    )
    story.extend(
        _pdf_table(
            "Anomalies",
            report["anomalies"],
            ("id", "event_id", "model_name", "anomaly_score", "is_anomaly", "created_at"),
            styles,
        )
    )
    story.extend(
        _pdf_table(
            "Investigation Findings",
            report["findings"],
            (
                "id",
                "finding_type",
                "title",
                "description",
                "supporting_event_ids",
                "confidence",
                "status",
                "created_at",
            ),
            styles,
        )
    )
    document.build(story)
    return buffer.getvalue()