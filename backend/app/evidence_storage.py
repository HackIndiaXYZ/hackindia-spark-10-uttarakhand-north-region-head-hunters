"""Persistent local storage for uploaded CHITRAGUPT evidence files."""

import os
import shutil
from hashlib import sha256
from pathlib import Path

from sqlalchemy import select

from backend.app.database import SessionLocal
from backend.app.models import Evidence


EVIDENCE_STORAGE_DIR = Path(__file__).resolve().parents[2] / "data" / "evidence"


def retain_evidence_file(
    source_path: str | Path,
    evidence_id: int,
    original_filename: str | None,
) -> Path:
    """Copy an uploaded file to its evidence-ID path without overwriting."""
    source = Path(source_path)
    if not source.is_file():
        raise FileNotFoundError(f"Evidence source file not found: {source}")

    EVIDENCE_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    extension = Path(original_filename or source.name).suffix
    destination = EVIDENCE_STORAGE_DIR / f"{evidence_id}{extension}"
    destination_fd = None
    destination_created = False
    try:
        destination_fd = os.open(
            destination,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL,
        )
        destination_created = True
        with os.fdopen(destination_fd, "wb") as retained_file:
            destination_fd = None
            with source.open("rb") as source_file:
                shutil.copyfileobj(source_file, retained_file)
    except Exception:
        if destination_fd is not None:
            os.close(destination_fd)
        if destination_created:
            destination.unlink(missing_ok=True)
        raise

    return destination


def remove_retained_evidence(path: str | Path | None) -> None:
    """Remove a retained evidence file when a later operation fails."""
    if path is not None:
        Path(path).unlink(missing_ok=True)


def _sha256_file(file_path: Path) -> str:
    digest = sha256()
    with file_path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _retained_evidence_path(evidence: Evidence) -> Path:
    extension = Path(evidence.filename).suffix
    return EVIDENCE_STORAGE_DIR / f"{evidence.id}{extension}"


def verify_evidence_integrity(evidence_id: int) -> dict:
    """Compare a retained evidence file with its persisted SHA-256 hash."""
    if (
        not isinstance(evidence_id, int)
        or isinstance(evidence_id, bool)
        or evidence_id <= 0
    ):
        return {
            "evidence_id": evidence_id,
            "status": "invalid_evidence_id",
            "matches": None,
            "message": "Evidence ID must be a positive integer.",
        }

    session = SessionLocal()
    try:
        evidence = session.scalar(select(Evidence).where(Evidence.id == evidence_id))
        if evidence is None:
            return {
                "evidence_id": evidence_id,
                "status": "missing_evidence",
                "matches": None,
                "message": f"Evidence {evidence_id} was not found.",
            }

        retained_path = _retained_evidence_path(evidence)
        result = {
            "evidence_id": evidence.id,
            "status": "missing_file",
            "matches": None,
            "stored_sha256": evidence.sha256,
            "calculated_sha256": None,
            "file_path": str(retained_path),
            "message": f"Retained evidence file is missing: {retained_path.name}.",
        }
        if not retained_path.is_file():
            return result

        calculated_sha256 = _sha256_file(retained_path)
        matches = calculated_sha256 == evidence.sha256
        result.update(
            {
                "status": "match" if matches else "mismatch",
                "matches": matches,
                "calculated_sha256": calculated_sha256,
                "message": (
                    "Retained evidence hash matches the database hash."
                    if matches
                    else "Retained evidence hash does not match the database hash."
                ),
            }
        )
        return result
    finally:
        session.close()