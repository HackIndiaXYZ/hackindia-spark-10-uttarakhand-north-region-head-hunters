"""Persistent local storage for uploaded CHITRAGUPT evidence files."""

import os
import shutil
from pathlib import Path


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