from hashlib import sha256
from pathlib import Path

import pytest

from backend.app import evidence_storage
from backend.app.ingestion import ingest_csv


def test_retain_evidence_file_preserves_contents_and_extension(tmp_path, monkeypatch):
    source = tmp_path / "uploaded.csv"
    source.write_bytes(b"evidence contents")
    storage_dir = tmp_path / "evidence"
    monkeypatch.setattr(evidence_storage, "EVIDENCE_STORAGE_DIR", storage_dir)

    retained_path = evidence_storage.retain_evidence_file(source, 123, source.name)

    assert retained_path == storage_dir / "123.csv"
    assert retained_path.read_bytes() == source.read_bytes()


def test_retained_file_hash_matches_source_hash(tmp_path, monkeypatch):
    source = tmp_path / "uploaded.csv"
    source.write_bytes(
        (Path(__file__).parents[1] / "data" / "sample_security_logs.csv").read_bytes()
    )
    storage_dir = tmp_path / "evidence"
    monkeypatch.setattr(evidence_storage, "EVIDENCE_STORAGE_DIR", storage_dir)
    evidence, _ = ingest_csv(source, case_id=1)

    retained_path = evidence_storage.retain_evidence_file(source, 456, source.name)

    retained_hash = sha256(retained_path.read_bytes()).hexdigest()

    assert retained_hash == evidence.sha256


def test_duplicate_retention_does_not_overwrite_existing_file(tmp_path, monkeypatch):
    source = tmp_path / "uploaded.csv"
    source.write_bytes(b"original")
    storage_dir = tmp_path / "evidence"
    monkeypatch.setattr(evidence_storage, "EVIDENCE_STORAGE_DIR", storage_dir)
    retained_path = evidence_storage.retain_evidence_file(source, 789, source.name)
    source.write_bytes(b"replacement")

    with pytest.raises(FileExistsError):
        evidence_storage.retain_evidence_file(source, 789, source.name)

    assert retained_path.read_bytes() == b"original"


def test_failed_retention_removes_partial_file(tmp_path, monkeypatch):
    source = tmp_path / "uploaded.csv"
    source.write_bytes(b"evidence contents")
    storage_dir = tmp_path / "evidence"
    monkeypatch.setattr(evidence_storage, "EVIDENCE_STORAGE_DIR", storage_dir)

    def fail_copyfileobj(source_file, retained_file):
        retained_file.write(b"partial")
        raise OSError("copy failed")

    monkeypatch.setattr(evidence_storage.shutil, "copyfileobj", fail_copyfileobj)

    with pytest.raises(OSError, match="copy failed"):
        evidence_storage.retain_evidence_file(source, 321, source.name)

    assert not (storage_dir / "321.csv").exists()