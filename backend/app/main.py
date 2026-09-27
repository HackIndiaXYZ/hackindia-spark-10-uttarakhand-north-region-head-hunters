import os
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from sqlalchemy import select

from .database import SessionLocal
from .ingestion import ingest_csv
from .models import Anomaly, Case, Evidence, Event, Finding
from .evidence_storage import (
    remove_retained_evidence,
    retain_evidence_file,
    verify_evidence_integrity,
)
from .persistence import delete_persisted_ingestion, persist_ingestion
from .pipeline import run_investigation_pipeline
from .queries import get_events_by_case
from .reporting import (
    generate_csv_report,
    generate_json_report,
    generate_pdf_report,
)
from .windows_event_ingestion import ingest_windows_event_xml
from .ollama_explanation import (
    OllamaHTTPError,
    OllamaOutputError,
    OllamaTimeoutError,
    OllamaUnavailableError,
    explain_finding,
)


MAX_EXPLANATION_SUPPORTING_EVENTS = 25
MAX_EXPLANATION_ANOMALIES = 50


def _bounded_explanation_text(value: str | None, max_length: int = 1200) -> str | None:
    return value[:max_length] if isinstance(value, str) else None

app = FastAPI(title="CHITRAGUPT API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
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
                "supporting_event_ids": finding.supporting_event_ids,
                "confidence": finding.confidence,
                "status": finding.status,
                "created_at": finding.created_at,
            }
            for finding in findings
        ]
    finally:
        session.close()


@app.post("/cases/{case_id}/findings/{finding_id}/explanation")
def explain_case_finding(case_id: int, finding_id: int):
    """Return an optional Ollama explanation of a persisted case finding."""
    session = SessionLocal()
    try:
        case = session.scalar(select(Case).where(Case.id == case_id))
        if case is None:
            raise HTTPException(status_code=404, detail=f"Case {case_id} not found.")

        finding = session.scalar(
            select(Finding).where(
                Finding.id == finding_id,
                Finding.case_id == case_id,
            )
        )
        if finding is None:
            raise HTTPException(
                status_code=404,
                detail=f"Finding {finding_id} was not found in case {case_id}.",
            )

        persisted_event_ids = finding.supporting_event_ids or []
        valid_event_ids = list(
            dict.fromkeys(
                event_id
                for event_id in persisted_event_ids
                if isinstance(event_id, int) and not isinstance(event_id, bool)
            )
        )
        bounded_event_ids = valid_event_ids[:MAX_EXPLANATION_SUPPORTING_EVENTS]
        supporting_events = []
        if bounded_event_ids:
            supporting_events = session.scalars(
                select(Event)
                .where(
                    Event.case_id == case_id,
                    Event.id.in_(bounded_event_ids),
                )
                .order_by(Event.timestamp.asc(), Event.id.asc())
            ).all()

        actual_event_ids = [event.id for event in supporting_events]
        evidence_ids = list(
            dict.fromkeys(
                event.evidence_id
                for event in supporting_events
                if event.evidence_id is not None
            )
        )
        evidence_items = []
        if evidence_ids:
            evidence_items = session.scalars(
                select(Evidence)
                .where(
                    Evidence.case_id == case_id,
                    Evidence.id.in_(evidence_ids),
                )
                .order_by(Evidence.id.asc())
            ).all()

        anomalies = []
        if actual_event_ids:
            anomalies = session.scalars(
                select(Anomaly)
                .where(
                    Anomaly.case_id == case_id,
                    Anomaly.event_id.in_(actual_event_ids),
                )
                .order_by(Anomaly.id.asc())
                .limit(MAX_EXPLANATION_ANOMALIES)
            ).all()

        finding_context = {
            "case": {
                "id": case.id,
                "case_number": _bounded_explanation_text(case.case_number, 255),
                "title": _bounded_explanation_text(case.title, 512),
                "description": _bounded_explanation_text(case.description, 2000),
            },
            "finding": {
                "id": finding.id,
                "finding_type": _bounded_explanation_text(finding.finding_type, 255),
                "title": _bounded_explanation_text(finding.title, 512),
                "description": _bounded_explanation_text(finding.description, 2000),
                "confidence": finding.confidence,
                "status": _bounded_explanation_text(finding.status, 100),
                "supporting_event_ids": actual_event_ids,
                "supporting_event_count_total": len(valid_event_ids),
                "supporting_events_truncated": (
                    len(valid_event_ids) > len(actual_event_ids)
                ),
            },
            "supporting_events": [
                {
                    "id": event.id,
                    "timestamp": event.timestamp.isoformat() if event.timestamp else None,
                    "event_type": _bounded_explanation_text(event.event_type, 255),
                    "source": _bounded_explanation_text(event.source, 512),
                    "user": _bounded_explanation_text(event.user, 512),
                    "device": _bounded_explanation_text(event.device, 512),
                    "ip_address": _bounded_explanation_text(event.ip_address, 128),
                    "application": _bounded_explanation_text(event.application, 512),
                    "process": _bounded_explanation_text(event.process, 512),
                    "file_path": _bounded_explanation_text(event.file_path, 1200),
                    "description": _bounded_explanation_text(event.description, 2000),
                    "evidence_id": event.evidence_id,
                }
                for event in supporting_events
            ],
            "evidence": [
                {
                    "id": evidence.id,
                    "filename": _bounded_explanation_text(evidence.filename, 512),
                    "source": _bounded_explanation_text(evidence.source, 512),
                    "evidence_type": _bounded_explanation_text(evidence.evidence_type, 255),
                    "file_size": evidence.file_size,
                    "sha256": evidence.sha256,
                }
                for evidence in evidence_items
            ],
            "persisted_anomalies": [
                {
                    "event_id": anomaly.event_id,
                    "model_name": _bounded_explanation_text(anomaly.model_name, 255),
                    "anomaly_score": anomaly.anomaly_score,
                    "is_anomaly": anomaly.is_anomaly,
                }
                for anomaly in anomalies
            ],
        }
    finally:
        session.close()

    try:
        return explain_finding(finding_context)
    except OllamaTimeoutError as exc:
        raise HTTPException(status_code=504, detail="Ollama explanation timed out.") from exc
    except OllamaUnavailableError as exc:
        raise HTTPException(status_code=503, detail="Ollama is unavailable.") from exc
    except OllamaHTTPError as exc:
        raise HTTPException(status_code=502, detail="Ollama returned an HTTP error.") from exc
    except OllamaOutputError as exc:
        raise HTTPException(
            status_code=502,
            detail="Ollama returned an invalid explanation.",
        ) from exc


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


@app.get("/evidence/{evidence_id}/integrity")
def evidence_integrity(evidence_id: int):
    """Verify a retained evidence file against its persisted SHA-256 hash."""
    result = verify_evidence_integrity(evidence_id)
    if result["status"] == "invalid_evidence_id":
        raise HTTPException(status_code=400, detail=result["message"])
    if result["status"] == "missing_evidence":
        raise HTTPException(status_code=404, detail=result["message"])
    return result


@app.get("/cases")
def cases():
    """Return all persisted cases ordered by ID."""
    session = SessionLocal()
    try:
        statement = select(Case).order_by(Case.id.asc())
        case_records = session.scalars(statement).all()
        return list(
            {
                "id": case.id,
                "case_number": case.case_number,
                "title": case.title,
                "description": case.description,
                "status": case.status,
                "created_at": case.created_at,
                "updated_at": case.updated_at,
            }
            for case in case_records
        )
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


def _ensure_case_exists(case_id: int) -> None:
    session = SessionLocal()
    try:
        if session.get(Case, case_id) is None:
            raise HTTPException(
                status_code=404,
                detail=f"Case {case_id} not found.",
            )
    finally:
        session.close()


@app.get("/cases/{case_id}/report/json")
def case_json_report(case_id: int):
    """Download a JSON investigation report for a case."""
    _ensure_case_exists(case_id)
    return Response(
        content=generate_json_report(case_id),
        media_type="application/json",
        headers={
            "Content-Disposition": (
                f'attachment; filename="CHITRAGUPT_case_{case_id}_report.json"'
            )
        },
    )


@app.get("/cases/{case_id}/report/csv")
def case_csv_report(case_id: int):
    """Download a CSV investigation report for a case."""
    _ensure_case_exists(case_id)
    return Response(
        content=generate_csv_report(case_id),
        media_type="text/csv",
        headers={
            "Content-Disposition": (
                f'attachment; filename="CHITRAGUPT_case_{case_id}_report.csv"'
            )
        },
    )


@app.get("/cases/{case_id}/report/pdf")
def case_pdf_report(case_id: int):
    """Download a PDF investigation report for a case."""
    _ensure_case_exists(case_id)
    return Response(
        content=generate_pdf_report(case_id),
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                f'attachment; filename="CHITRAGUPT_case_{case_id}_report.pdf"'
            )
        },
    )


@app.post("/cases/{case_id}/ingest")
async def ingest_case(case_id: int, file: UploadFile = File(...)):
    """Ingest an uploaded CSV or Windows Event XML file and run the pipeline."""
    case_session = SessionLocal()
    try:
        if case_session.get(Case, case_id) is None:
            raise HTTPException(
                status_code=404,
                detail=f"Case {case_id} not found.",
            )
    finally:
        case_session.close()

    temporary_path = None
    try:
        filename = file.filename or "evidence.csv"
        suffix = Path(filename).suffix.lower() or ".csv"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temporary_file:
            temporary_path = temporary_file.name
            while chunk := await file.read(1024 * 1024):
                temporary_file.write(chunk)

        try:
            if suffix == ".csv":
                evidence, events = ingest_csv(temporary_path, case_id)
            elif suffix == ".xml":
                evidence, events = ingest_windows_event_xml(temporary_path, case_id)
            else:
                raise ValueError(
                    "Unsupported evidence format. Use CSV or Windows Event XML."
                )
        except (OSError, ValueError) as exc:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid or unreadable CSV: {exc}",
            ) from exc

        persisted_evidence = None
        retained_path = None
        try:
            persisted_evidence = persist_ingestion(evidence, events)
            retained_path = retain_evidence_file(
                temporary_path,
                persisted_evidence.id,
                file.filename,
            )
            pipeline_result = run_investigation_pipeline(case_id)
        except Exception as exc:
            remove_retained_evidence(retained_path)
            if persisted_evidence is not None:
                try:
                    delete_persisted_ingestion(persisted_evidence.id)
                except Exception:
                    pass
            raise HTTPException(
                status_code=500,
                detail="CSV processing failed.",
            ) from exc

        return {
            "case_id": case_id,
            "evidence_id": persisted_evidence.id,
            "filename": file.filename,
            "event_count": pipeline_result["event_count"],
            "finding_count": len(pipeline_result["findings"]),
            "anomaly_count": len(pipeline_result["isolation_forest_results"])
            + len(pipeline_result["lof_results"]),
            "finding_ids": pipeline_result["persisted_finding_ids"],
        }
    except HTTPException:
        raise
    except OSError as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to save the uploaded file temporarily.",
        ) from exc
    finally:
        await file.close()
        if temporary_path is not None:
            try:
                os.unlink(temporary_path)
            except FileNotFoundError:
                pass