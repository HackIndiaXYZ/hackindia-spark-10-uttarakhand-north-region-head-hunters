from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from backend.app.database import SessionLocal
from backend.app.models import Anomaly, Case, Evidence, Finding
from backend.app.queries import get_events_by_case

app = FastAPI(title="CHITRAGUPT API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "CHITRAGUPT API is running"}


@app.get("/cases/{case_id}/events")
def case_events(case_id: int):
    """Return persisted events for a case in database query order."""
    events = get_events_by_case(case_id)
    return [
        {
            "id": event.id,
            "case_id": event.case_id,
            "evidence_id": event.evidence_id,
            "timestamp": event.timestamp,
            "event_type": event.event_type,
            "source": event.source,
            "user": event.user,
            "device": event.device,
            "ip_address": event.ip_address,
            "application": event.application,
            "process": event.process,
            "file_path": event.file_path,
            "description": event.description,
        }
        for event in events
    ]


@app.get("/cases/{case_id}/findings")
def case_findings(case_id: int):
    """Return persisted findings for a case ordered by database ID."""
    session = SessionLocal()
    try:
        statement = (
            select(Finding)
            .where(Finding.case_id == case_id)
            .order_by(Finding.id.asc())
        )
        findings = session.scalars(statement).all()
        return [
            {
                "id": finding.id,
                "case_id": finding.case_id,
                "finding_type": finding.finding_type,
                "title": finding.title,
                "description": finding.description,
                "confidence": finding.confidence,
                "status": finding.status,
                "created_at": finding.created_at,
            }
            for finding in findings
        ]
    finally:
        session.close()


@app.get("/cases/{case_id}/anomalies")
def case_anomalies(case_id: int):
    """Return persisted anomalies for a case ordered by database ID."""
    session = SessionLocal()
    try:
        statement = (
            select(Anomaly)
            .where(Anomaly.case_id == case_id)
            .order_by(Anomaly.id.asc())
        )
        anomalies = session.scalars(statement).all()
        return [
            {
                "id": anomaly.id,
                "case_id": anomaly.case_id,
                "event_id": anomaly.event_id,
                "model_name": anomaly.model_name,
                "anomaly_score": anomaly.anomaly_score,
                "is_anomaly": anomaly.is_anomaly,
                "created_at": anomaly.created_at,
            }
            for anomaly in anomalies
        ]
    finally:
        session.close()


@app.get("/cases/{case_id}/evidence")
def case_evidence(case_id: int):
    """Return persisted evidence for a case ordered by database ID."""
    session = SessionLocal()
    try:
        statement = (
            select(Evidence)
            .where(Evidence.case_id == case_id)
            .order_by(Evidence.id.asc())
        )
        evidence_items = session.scalars(statement).all()
        return [
            {
                "id": evidence.id,
                "case_id": evidence.case_id,
                "filename": evidence.filename,
                "source": evidence.source,
                "evidence_type": evidence.evidence_type,
                "file_size": evidence.file_size,
                "sha256": evidence.sha256,
                "ingested_at": evidence.ingested_at,
                "processing_status": evidence.processing_status,
            }
            for evidence in evidence_items
        ]
    finally:
        session.close()


@app.get("/cases/{case_id}")
def case_details(case_id: int):
    """Return persisted metadata for a case."""
    session = SessionLocal()
    try:
        statement = select(Case).where(Case.id == case_id)
        case = session.scalar(statement)
        if case is None:
            raise HTTPException(
                status_code=404,
                detail=f"Case {case_id} not found.",
            )

        return {
            "id": case.id,
            "case_number": case.case_number,
            "title": case.title,
            "description": case.description,
            "status": case.status,
            "created_at": case.created_at,
            "updated_at": case.updated_at,
        }
    finally:
        session.close()