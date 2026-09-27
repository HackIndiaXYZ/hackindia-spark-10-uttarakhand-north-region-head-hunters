from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from sqlalchemy import delete

from backend.app.anomaly import run_isolation_forest
from backend.app.correlation import correlate_events
from backend.app.database import SessionLocal
from backend.app.features import extract_event_features
from backend.app.inference import _describe_event_sequence, _event_sort_key, infer_findings
from backend.app.ingestion import ingest_csv
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


def test_infer_findings_uses_neutral_language_and_avoids_confirmed_activity_claims():
    events = [
        Event(
            id=1,
            case_id=1,
            evidence_id=None,
            timestamp=datetime(2026, 9, 21, 9, 5, 0, tzinfo=timezone.utc),
            event_type="file_access",
            source="fixture",
            user="ava.quill",
            device="ORION-LT-07",
            ip_address="10.44.18.27",
            application="File Explorer",
            process="explorer.exe",
            file_path="D:\\Casework\\Atlas\\confidential\\client_roster.xlsx",
            description="Synthetic confidential file access",
            raw_data={},
        ),
        Event(
            id=2,
            case_id=1,
            evidence_id=None,
            timestamp=datetime(2026, 9, 21, 9, 6, 0, tzinfo=timezone.utc),
            event_type="device_connected",
            source="fixture",
            user="ava.quill",
            device="ORION-LT-07",
            ip_address="10.44.18.27",
            application="Device Manager",
            process="devmgmt.exe",
            file_path=None,
            description="Synthetic Android USB device connected",
            raw_data={},
        ),
    ]
    findings = infer_findings(
        events,
        [{"event_id": 1, "rule_id": "possible_file_transfer", "matched": True}],
        [{"event_id_a": 1, "event_id_b": 2, "shared_attributes": ["user", "device"]}],
        [{"event_id": 1, "model_name": "isolation_forest", "is_anomaly": True}],
        [{"event_id": 2, "model_name": "lof", "is_anomaly": True}],
    )

    description = findings[0]["description"]
    lowered = description.lower()
    assert "consistent with" in lowered
    assert "successful transfer" not in lowered
    assert "confirmed" not in lowered
    assert "proof of malicious activity" in lowered
    assert "ava.quill" in description
    assert "isolation forest" in lowered
    assert "lof" in lowered


def test_infer_findings_handles_missing_events_and_incomplete_context():
    empty_description = _describe_event_sequence([], finding_type="possible_file_transfer")
    assert "insufficient" in empty_description.lower()

    event_a = Event(
        id=5,
        case_id=7,
        evidence_id=None,
        timestamp=None,
        event_type="file_access",
        source="fixture",
        user=None,
        device=None,
        ip_address=None,
        application=None,
        process="explorer.exe",
        file_path=None,
        description="No user or file path recorded",
        raw_data={},
    )
    event_b = Event(
        id=3,
        case_id=7,
        evidence_id=None,
        timestamp=None,
        event_type="device_connected",
        source="fixture",
        user=None,
        device=None,
        ip_address=None,
        application="Device Manager",
        process="devmgmt.exe",
        file_path=None,
        description="No timestamp recorded",
        raw_data={},
    )

    ordered = sorted([event_a, event_b], key=_event_sort_key)
    assert [event.id for event in ordered] == [3, 5]

    description = _describe_event_sequence([event_a, event_b], finding_type="possible_ransomware_activity")
    lowered = description.lower()
    assert "observed supporting events" in lowered
    assert "confirm" not in lowered
    assert "execution" in lowered or "activity" in lowered

    assert _event_sort_key(event_a)[2] == 5
    assert _event_sort_key(event_b)[2] == 3