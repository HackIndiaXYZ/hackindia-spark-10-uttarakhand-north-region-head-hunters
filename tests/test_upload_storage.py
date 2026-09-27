import asyncio
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from backend.app import evidence_storage, main


class FakeUpload:
    def __init__(self, content: bytes, filename: str = "upload.csv"):
        self.content = content
        self.filename = filename
        self._read = False
        self.closed = False

    async def read(self, size: int = -1):
        if self._read:
            return b""
        self._read = True
        return self.content

    async def close(self):
        self.closed = True


class FakeSession:
    def get(self, model, case_id):
        return object()

    def close(self):
        pass


def _run_ingest(upload):
    return asyncio.run(main.ingest_case(1, upload))


def test_upload_retains_file_and_preserves_response(tmp_path, monkeypatch):
    storage_dir = tmp_path / "evidence"
    monkeypatch.setattr(evidence_storage, "EVIDENCE_STORAGE_DIR", storage_dir)
    evidence = SimpleNamespace(id=100)
    content = b"uploaded evidence"
    upload = FakeUpload(content)
    monkeypatch.setattr(main, "SessionLocal", lambda: FakeSession())
    monkeypatch.setattr(main, "ingest_csv", lambda path, case_id: (evidence, []))
    monkeypatch.setattr(main, "persist_ingestion", lambda item, events: item)
    monkeypatch.setattr(
        main,
        "run_investigation_pipeline",
        lambda case_id: {
            "event_count": 2,
            "findings": [{"id": 7}],
            "isolation_forest_results": [{}],
            "lof_results": [{}],
            "persisted_finding_ids": [7],
        },
    )

    response = _run_ingest(upload)

    retained_path = storage_dir / "100.csv"
    assert response == {
        "case_id": 1,
        "evidence_id": 100,
        "filename": "upload.csv",
        "event_count": 2,
        "finding_count": 1,
        "anomaly_count": 2,
        "finding_ids": [7],
    }
    assert retained_path.read_bytes() == content
    assert upload.closed


def test_invalid_csv_upload_does_not_retain_file(tmp_path, monkeypatch):
    storage_dir = tmp_path / "evidence"
    monkeypatch.setattr(evidence_storage, "EVIDENCE_STORAGE_DIR", storage_dir)
    upload = FakeUpload(b"invalid")
    monkeypatch.setattr(main, "SessionLocal", lambda: FakeSession())

    def reject_csv(path, case_id):
        raise ValueError("invalid CSV")

    monkeypatch.setattr(main, "ingest_csv", reject_csv)

    with pytest.raises(HTTPException) as error:
        _run_ingest(upload)

    assert error.value.status_code == 400
    assert not storage_dir.exists()
    assert upload.closed


def test_retention_failure_cleans_up_persisted_ingestion(tmp_path, monkeypatch):
    storage_dir = tmp_path / "evidence"
    monkeypatch.setattr(evidence_storage, "EVIDENCE_STORAGE_DIR", storage_dir)
    evidence = SimpleNamespace(id=200)
    upload = FakeUpload(b"uploaded evidence")
    deleted_ids = []
    monkeypatch.setattr(main, "SessionLocal", lambda: FakeSession())
    monkeypatch.setattr(main, "ingest_csv", lambda path, case_id: (evidence, []))
    monkeypatch.setattr(main, "persist_ingestion", lambda item, events: item)
    monkeypatch.setattr(
        main,
        "retain_evidence_file",
        lambda source, evidence_id, filename: (_ for _ in ()).throw(
            OSError("storage unavailable")
        ),
    )
    monkeypatch.setattr(main, "delete_persisted_ingestion", deleted_ids.append)

    with pytest.raises(HTTPException) as error:
        _run_ingest(upload)

    assert error.value.status_code == 500
    assert deleted_ids == [200]
    assert not storage_dir.exists()
    assert upload.closed