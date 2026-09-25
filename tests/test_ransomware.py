from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from sqlalchemy import delete

from backend.app.anomaly import run_isolation_forest
from backend.app.correlation import correlate_events
from backend.app.database import SessionLocal
from backend.app.features import extract_event_features
from backend.app.ingestion import ingest_csv
from backend.app.inference import infer_findings
from backend.app.lof import run_lof
from backend.app.models import Anomaly, Case, Evidence, Event, Finding
from backend.app.persistence import persist_ingestion
from backend.app.queries import get_events_by_case
from backend.app.rules import evaluate_ransomware_rule


def test_ransomware_scenario_detects_stages_and_findings():
    dataset_path = Path(__file__).parents[1] / "data" / "synthetic_ransomware_logs.csv"
    expected_stages = {
        "suspicious_download",
        "process_execution",
        "rapid_file_activity",
        "file_encryption",
        "ransom_note_created",
    }
    case_id = None
    session = SessionLocal()
    try:
        case = Case(
            case_number=f"TEST-RANSOMWARE-{uuid4()}",
            title="Ransomware test case",
            description="Temporary case for ransomware scenario testing.",
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

        assert {event.event_type for event in persisted_events} == expected_stages

        rule_results = [
            evaluate_ransomware_rule(event) for event in persisted_events
        ]
        assert all(result["matched"] for result in rule_results)
        assert {result["event_id"] for result in rule_results} == {
            event.id for event in persisted_events
        }

        correlations = correlate_events(persisted_events)
        isolation_forest_results = run_isolation_forest(persisted_events)
        lof_results = run_lof(persisted_events)
        findings = infer_findings(
            persisted_events,
            rule_results,
            correlations,
            isolation_forest_results,
            lof_results,
        )

        assert correlations
        assert len(isolation_forest_results) == len(expected_stages)
        assert len(lof_results) == len(expected_stages)
        assert findings
        assert len(findings) == len(expected_stages)
        assert all(
            finding["finding_type"] == "possible_ransomware_activity"
            for finding in findings
        )
        event_ids = {event.id for event in persisted_events}
        assert all(finding["supporting_event_ids"] for finding in findings)
        assert all(
            set(finding["supporting_event_ids"]).issubset(event_ids)
            for finding in findings
        )
        assert all(
            result["model_name"] == "isolation_forest"
            for result in isolation_forest_results
        )
        assert all(result["model_name"] == "lof" for result in lof_results)
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