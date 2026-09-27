from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from sqlalchemy import delete, select

from backend.app.anomaly_persistence import persist_anomalies
from backend.app.database import SessionLocal
from backend.app.finding_persistence import persist_findings
from backend.app.ingestion import ingest_csv
from backend.app.models import Anomaly, Case, Evidence, Event, Finding
from backend.app.persistence import persist_ingestion
from backend.app.pipeline import run_investigation_pipeline


def test_run_investigation_pipeline_processes_sample_data():
    dataset_path = Path(__file__).parents[1] / "data" / "sample_security_logs.csv"
    case_id = None
    session = SessionLocal()
    try:
        case = Case(
            case_number=f"TEST-PIPELINE-{uuid4()}",
            title="Pipeline test case",
            description="Temporary case for pipeline testing.",
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

        result = run_investigation_pipeline(case_id)

        assert result["event_count"] == 20
        assert result["correlations"]
        assert result["isolation_forest_results"]
        assert result["lof_results"]
        assert result["findings"]
        assert result["persisted_anomaly_ids"]
        assert all(anomaly_id is not None for anomaly_id in result["persisted_anomaly_ids"])
        assert result["persisted_finding_ids"]
        assert all(finding_id is not None for finding_id in result["persisted_finding_ids"])

        finding_types = {finding["finding_type"] for finding in result["findings"]}
        assert "possible_file_transfer" in finding_types
        assert "possible_ransomware_activity" in finding_types
        assert all(finding["supporting_event_ids"] for finding in result["findings"])

        file_transfer_finding = next(
            finding
            for finding in result["findings"]
            if finding["finding_type"] == "possible_file_transfer"
        )
        description = file_transfer_finding["description"]
        assert "ava.quill" in description or "ORION-LT-07" in description
        assert (
            "client_roster.xlsx" in description
            or "atlas_bundle.zip" in description
            or "device_connected" in description
            or "file_copy" in description
        )

        verify_session = SessionLocal()
        try:
            persisted_findings = verify_session.scalars(
                select(Finding).where(Finding.case_id == case_id)
            ).all()
            persisted_types = {finding.finding_type for finding in persisted_findings}
            assert "possible_file_transfer" in persisted_types
            assert "possible_ransomware_activity" in persisted_types
            assert all(finding.supporting_event_ids for finding in persisted_findings)
        finally:
            verify_session.close()
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