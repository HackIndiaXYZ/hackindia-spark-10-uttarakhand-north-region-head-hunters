from pathlib import Path

import pytest

from backend.app.ingestion import ingest_csv


def test_ingest_csv_rejects_invalid_security_logs():
    fixture_path = Path(__file__).parent / "fixtures" / "invalid_security_logs.csv"

    with pytest.raises(ValueError, match=r"CSV is missing required columns: process"):
        ingest_csv(fixture_path, case_id=1)


def test_ingest_csv_processes_sample_security_logs():
    dataset_path = Path(__file__).parents[1] / "data" / "sample_security_logs.csv"

    evidence, events = ingest_csv(dataset_path, case_id=1)

    assert evidence.case_id == 1
    assert evidence.filename == "sample_security_logs.csv"
    assert evidence.evidence_type == "csv"
    assert evidence.file_size > 0
    assert evidence.sha256
    assert evidence.ingested_at is not None
    assert evidence.processing_status == "pending"
    assert len(events) == 20