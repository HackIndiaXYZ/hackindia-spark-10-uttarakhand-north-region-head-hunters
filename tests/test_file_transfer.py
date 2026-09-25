from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from sqlalchemy import delete

from backend.app.database import SessionLocal
from backend.app.ingestion import ingest_csv
from backend.app.models import Anomaly, Case, Evidence, Event, Finding
from backend.app.persistence import persist_ingestion
from backend.app.pipeline import run_investigation_pipeline
from backend.app.queries import get_events_by_case


def test_file_transfer_scenario_produces_finding_with_supporting_events():
    dataset_path = Path(__file__).parents[1] / "data" / "sample_security_logs.csv"
    case_id = None
    session = SessionLocal()
    try:
        case = Case(
            case_number=f"TEST-FILE-TRANSFER-{uuid4()}",
            title="File-transfer test case",
            description="Temporary case for file-transfer scenario testing.",
            status="open",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        session.add(case)
        session.commit()
        session.refresh(case)
        case_id = case.id
    finally:
        session.close()

    try:
        evidence, events = ingest_csv(dataset_path, case_id=case_id)
        persist_ingestion(evidence, events)
        persisted_events = get_events_by_case(case_id)

        result = run_investigation_pipeline(case_id)

        matched_rule_results = [
            rule_result
            for rule_result in result["rule_results"]
            if rule_result["matched"]
        ]
        assert matched_rule_results
        assert any(
            event.event_type == "device_connected"
            and event.id in {item["event_id"] for item in matched_rule_results}
            for event in persisted_events
        )

        file_transfer_findings = [
            finding
            for finding in result["findings"]
            if finding["finding_type"] == "possible_file_transfer"
        ]
        assert file_transfer_findings
        event_ids = {event.id for event in persisted_events}
        assert all(finding["supporting_event_ids"] for finding in file_transfer_findings)
        assert all(
            set(finding["supporting_event_ids"]).issubset(event_ids)
            for finding in file_transfer_findings
        )
    finally:
        cleanup_session = SessionLocal()
        try:
            cleanup_session.execute(delete(Finding).where(Finding.case_id == case_id))
            cleanup_session.execute(delete(Anomaly).where(Anomaly.case_id == case_id))
            cleanup_session.execute(delete(Event).where(Event.case_id == case_id))
            cleanup_session.execute(delete(Evidence).where(Evidence.case_id == case_id))
            cleanup_session.execute(delete(Case).where(Case.id == case_id))
            cleanup_session.commit()
        finally:
            cleanup_session.close()