from hashlib import sha256
from pathlib import Path

import pytest

from backend.app.ingestion import ingest_csv
from backend.app.windows_event_ingestion import ingest_windows_event_xml


FIXTURES = Path(__file__).parent / "fixtures"


def test_ingest_windows_event_xml_maps_fields_and_preserves_raw_data():
    source_path = FIXTURES / "windows_events.xml"

    evidence, events = ingest_windows_event_xml(source_path, case_id=7)

    assert evidence.case_id == 7
    assert evidence.filename == "windows_events.xml"
    assert evidence.evidence_type == "windows_event_xml"
    assert evidence.sha256 == sha256(source_path.read_bytes()).hexdigest()
    assert len(events) == 2

    first_event = events[0]
    assert first_event.case_id == 7
    assert first_event.event_type == "4624"
    assert first_event.source == "Microsoft-Windows-Security-Auditing"
    assert first_event.device == "WORKSTATION-01"
    assert first_event.user == "alice"
    assert first_event.process == "812"
    assert first_event.ip_address == "192.0.2.10"
    assert first_event.timestamp is not None
    assert first_event.raw_data["event_id"] == "4624"
    assert first_event.raw_data["event_data"]["IpAddress"] == "192.0.2.10"
    assert first_event.raw_data["event"]["tag"] == "Event"


def test_ingest_windows_event_xml_handles_missing_optional_fields():
    _, events = ingest_windows_event_xml(FIXTURES / "windows_events.xml", case_id=7)

    second_event = events[1]
    assert second_event.event_type == "6005"
    assert second_event.source == "Microsoft-Windows-System"
    assert second_event.device == "WORKSTATION-01"
    assert second_event.user is None
    assert second_event.process is None
    assert second_event.raw_data["event_data"] == {}


def test_ingest_windows_event_xml_rejects_malformed_xml():
    with pytest.raises(ValueError, match="Unable to parse Windows Event XML"):
        ingest_windows_event_xml(FIXTURES / "malformed_windows_events.xml", case_id=7)


def test_ingest_windows_event_xml_reports_malformed_individual_event():
    with pytest.raises(
        ValueError,
        match=r"Malformed Windows Event XML event 2: missing System element",
    ):
        ingest_windows_event_xml(FIXTURES / "malformed_windows_event.xml", case_id=7)


def test_existing_csv_ingestion_remains_available():
    evidence, events = ingest_csv(
        Path(__file__).parents[1] / "data" / "sample_security_logs.csv",
        case_id=7,
    )

    assert evidence.evidence_type == "csv"
    assert len(events) == 20