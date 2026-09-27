from hashlib import sha256
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from backend.app import evidence_storage
from backend.app.main import app


class FakeSession:
    def __init__(self, evidence):
        self.evidence = evidence
        self.closed = False

    def scalar(self, statement):
        return self.evidence

    def close(self):
        self.closed = True


def _evidence(evidence_id=1, filename="source.csv", stored_sha256=None):
    return SimpleNamespace(
        id=evidence_id,
        filename=filename,
        sha256=stored_sha256,
    )


def test_matching_evidence_hash(tmp_path, monkeypatch):
    content = b"original evidence"
    evidence = _evidence(stored_sha256=sha256(content).hexdigest())
    storage_dir = tmp_path / "evidence"
    storage_dir.mkdir()
    (storage_dir / "1.csv").write_bytes(content)
    monkeypatch.setattr(evidence_storage, "EVIDENCE_STORAGE_DIR", storage_dir)
    monkeypatch.setattr(evidence_storage, "SessionLocal", lambda: FakeSession(evidence))

    result = evidence_storage.verify_evidence_integrity(1)

    assert result["status"] == "match"
    assert result["matches"] is True
    assert result["calculated_sha256"] == evidence.sha256


def test_modified_evidence_file_is_mismatch(tmp_path, monkeypatch):
    evidence = _evidence(stored_sha256=sha256(b"original").hexdigest())
    storage_dir = tmp_path / "evidence"
    storage_dir.mkdir()
    (storage_dir / "1.csv").write_bytes(b"modified")
    monkeypatch.setattr(evidence_storage, "EVIDENCE_STORAGE_DIR", storage_dir)
    monkeypatch.setattr(evidence_storage, "SessionLocal", lambda: FakeSession(evidence))

    result = evidence_storage.verify_evidence_integrity(1)

    assert result["status"] == "mismatch"
    assert result["matches"] is False
    assert result["calculated_sha256"] != result["stored_sha256"]


def test_missing_evidence_file(tmp_path, monkeypatch):
    evidence = _evidence(stored_sha256=sha256(b"original").hexdigest())
    monkeypatch.setattr(evidence_storage, "EVIDENCE_STORAGE_DIR", tmp_path / "evidence")
    monkeypatch.setattr(evidence_storage, "SessionLocal", lambda: FakeSession(evidence))

    result = evidence_storage.verify_evidence_integrity(1)

    assert result["status"] == "missing_file"
    assert result["matches"] is None
    assert result["calculated_sha256"] is None


def test_invalid_evidence_id_is_handled_without_database_access(monkeypatch):
    def fail_session_creation():
        raise AssertionError("database should not be accessed")

    monkeypatch.setattr(evidence_storage, "SessionLocal", fail_session_creation)

    result = evidence_storage.verify_evidence_integrity(0)

    assert result["status"] == "invalid_evidence_id"
    assert result["matches"] is None


def test_integrity_endpoint_returns_result_for_matching_file(monkeypatch):
    expected = {"evidence_id": 1, "status": "match", "matches": True}
    monkeypatch.setattr("backend.app.main.verify_evidence_integrity", lambda evidence_id: expected)

    response = TestClient(app).get("/evidence/1/integrity")

    assert response.status_code == 200
    assert response.json() == expected


def test_integrity_endpoint_returns_errors_for_invalid_and_missing_ids(monkeypatch):
    monkeypatch.setattr(
        "backend.app.main.verify_evidence_integrity",
        lambda evidence_id: {
            "status": "invalid_evidence_id",
            "message": "Evidence ID must be a positive integer.",
        },
    )
    client = TestClient(app)
    invalid_response = client.get("/evidence/0/integrity")
    assert invalid_response.status_code == 400

    monkeypatch.setattr(
        "backend.app.main.verify_evidence_integrity",
        lambda evidence_id: {
            "status": "missing_evidence",
            "message": "Evidence 99 was not found.",
        },
    )
    missing_response = client.get("/evidence/99/integrity")
    assert missing_response.status_code == 404