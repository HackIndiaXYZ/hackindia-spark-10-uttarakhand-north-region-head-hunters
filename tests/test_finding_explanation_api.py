from datetime import datetime, timezone
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from backend.app import main, ollama_explanation
from backend.app.database import SessionLocal
from backend.app.models import Anomaly, Case, Evidence, Event, Finding


@pytest.fixture
def explanation_records():
    session = SessionLocal()
    records = {}
    case_ids = []
    finding_ids = []
    try:
        for suffix in ("one", "two"):
            now = datetime.now(timezone.utc)
            case = Case(
                case_number=f"TEST-EXPLAIN-{suffix}-{uuid4()}",
                title=f"Explanation test case {suffix}",
                description="Case description for explanation tests.",
                status="open",
                created_at=now,
                updated_at=now,
            )
            session.add(case)
            session.flush()
            case_ids.append(case.id)

            evidence = Evidence(
                case_id=case.id,
                filename=f"{suffix}.csv",
                source="test fixture",
                evidence_type="csv",
                file_size=100,
                sha256="a" * 64,
                ingested_at=now,
                processing_status="complete",
            )
            session.add(evidence)
            session.flush()

            event = Event(
                case_id=case.id,
                evidence_id=evidence.id,
                timestamp=now,
                event_type="file_access",
                source="fixture source",
                user="analyst-test-user",
                device="test-device",
                ip_address="192.0.2.10",
                application="test-app",
                process="test-process",
                file_path="/fixture/private-path.txt",
                description="Persisted supporting event.",
                raw_data={"must_not_be_sent": "unbounded source data"},
            )
            session.add(event)
            session.flush()

            finding = Finding(
                case_id=case.id,
                finding_type="possible_file_transfer",
                title=f"Existing finding {suffix}",
                description="Persisted deterministic finding.",
                supporting_event_ids=[event.id],
                confidence=0.7,
                status="open",
                created_at=now,
            )
            session.add(finding)
            session.flush()
            finding_ids.append(finding.id)

            session.add(
                Anomaly(
                    case_id=case.id,
                    event_id=event.id,
                    model_name="isolation_forest",
                    anomaly_score=-0.2,
                    is_anomaly=True,
                    created_at=now,
                )
            )
            records[suffix] = {
                "case_id": case.id,
                "evidence_id": evidence.id,
                "event_id": event.id,
                "finding_id": finding.id,
            }
        session.commit()
        yield records
    finally:
        if case_ids:
            session.execute(delete(Anomaly).where(Anomaly.case_id.in_(case_ids)))
            session.execute(delete(Finding).where(Finding.case_id.in_(case_ids)))
            session.execute(delete(Event).where(Event.case_id.in_(case_ids)))
            session.execute(delete(Evidence).where(Evidence.case_id.in_(case_ids)))
            session.execute(delete(Case).where(Case.id.in_(case_ids)))
            session.commit()
        session.close()


def test_finding_explanation_returns_service_result_and_persisted_context(
    monkeypatch,
    explanation_records,
):
    target = explanation_records["one"]
    explanation = {
        "summary": "Explanation of the existing finding.",
        "reasoning": ["The persisted event records a file access."],
        "supporting_event_ids": [target["event_id"]],
        "limitations": ["Only supplied records were considered."],
        "recommended_investigation_points": ["Review the source evidence."],
    }
    captured_context = {}

    def fake_explain_finding(context):
        captured_context.update(context)
        return explanation

    monkeypatch.setattr(main, "explain_finding", fake_explain_finding)

    response = TestClient(main.app).post(
        f"/cases/{target['case_id']}/findings/{target['finding_id']}/explanation"
    )

    assert response.status_code == 200
    assert response.json() == explanation
    assert captured_context["case"]["id"] == target["case_id"]
    assert captured_context["finding"]["id"] == target["finding_id"]
    assert captured_context["finding"]["supporting_event_ids"] == [target["event_id"]]
    assert captured_context["supporting_events"][0]["id"] == target["event_id"]
    assert captured_context["supporting_events"][0]["evidence_id"] == target["evidence_id"]
    assert captured_context["evidence"][0]["id"] == target["evidence_id"]
    assert captured_context["persisted_anomalies"][0]["event_id"] == target["event_id"]
    assert "raw_data" not in captured_context["supporting_events"][0]
    assert "correlations" not in captured_context
    assert "signals" not in captured_context["finding"]

    verify_session = SessionLocal()
    try:
        persisted_finding = verify_session.scalar(
            select(Finding).where(Finding.id == target["finding_id"])
        )
        assert persisted_finding.description == "Persisted deterministic finding."
        assert persisted_finding.confidence == 0.7
    finally:
        verify_session.close()


@pytest.mark.parametrize(
    ("error", "expected_status"),
    [
        (ollama_explanation.OllamaTimeoutError("timed out"), 504),
        (ollama_explanation.OllamaUnavailableError("offline"), 503),
        (ollama_explanation.OllamaHTTPError("upstream HTTP error"), 502),
        (ollama_explanation.OllamaOutputError("invalid output"), 502),
    ],
)
def test_finding_explanation_maps_service_failures(
    monkeypatch,
    explanation_records,
    error,
    expected_status,
):
    target = explanation_records["one"]

    def fail_explanation(context):
        raise error

    monkeypatch.setattr(main, "explain_finding", fail_explanation)

    response = TestClient(main.app).post(
        f"/cases/{target['case_id']}/findings/{target['finding_id']}/explanation"
    )

    assert response.status_code == expected_status
    assert response.json()["detail"]


def test_finding_explanation_returns_404_for_unknown_case(monkeypatch):
    monkeypatch.setattr(
        main,
        "explain_finding",
        lambda context: pytest.fail("Ollama must not be called for an unknown case."),
    )

    response = TestClient(main.app).post("/cases/-918273/findings/1/explanation")

    assert response.status_code == 404


def test_finding_explanation_returns_404_for_unknown_finding(
    monkeypatch,
    explanation_records,
):
    target = explanation_records["one"]
    monkeypatch.setattr(
        main,
        "explain_finding",
        lambda context: pytest.fail("Ollama must not be called for an unknown finding."),
    )

    response = TestClient(main.app).post(
        f"/cases/{target['case_id']}/findings/-918273/explanation"
    )

    assert response.status_code == 404


def test_finding_explanation_does_not_expose_another_cases_finding(
    monkeypatch,
    explanation_records,
):
    first_case = explanation_records["one"]
    other_case_finding = explanation_records["two"]["finding_id"]
    monkeypatch.setattr(
        main,
        "explain_finding",
        lambda context: pytest.fail("Ollama must not receive another case's finding."),
    )

    response = TestClient(main.app).post(
        f"/cases/{first_case['case_id']}/findings/{other_case_finding}/explanation"
    )

    assert response.status_code == 404
