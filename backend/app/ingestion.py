"""CSV security-log ingestion into transient evidence and event ORM objects."""

from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any

import pandas as pd

from backend.app.models import Evidence, Event


REQUIRED_COLUMNS = (
    "timestamp",
    "event_type",
    "source",
    "user",
    "device",
    "ip_address",
    "application",
    "process",
    "file_path",
    "description",
)


def _sha256_file(file_path: Path) -> str:
    digest = sha256()
    with file_path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _normalize_value(value: Any) -> Any:
    return None if pd.isna(value) else value


def _normalize_timestamp(value: Any, row_number: int) -> datetime | None:
    value = _normalize_value(value)
    if value is None:
        return None
    try:
        timestamp = pd.to_datetime(value, utc=True, errors="raise")
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"Invalid timestamp at CSV data row {row_number}: {value!r}"
        ) from exc
    return timestamp.to_pydatetime()


def ingest_csv(
    csv_path: str | Path,
    case_id: int,
    *,
    source: str | None = None,
    ingested_at: datetime | None = None,
) -> tuple[Evidence, list[Event]]:
    """Hash and normalize a CSV file into unsaved Evidence and Event objects."""
    file_path = Path(csv_path)
    if not file_path.is_file():
        raise FileNotFoundError(f"CSV evidence file not found: {file_path}")

    try:
        dataframe = pd.read_csv(file_path)
    except (OSError, pd.errors.ParserError, UnicodeDecodeError) as exc:
        raise ValueError(f"Unable to read CSV evidence file: {file_path}") from exc

    missing_columns = [column for column in REQUIRED_COLUMNS if column not in dataframe.columns]
    if missing_columns:
        missing = ", ".join(missing_columns)
        raise ValueError(f"CSV is missing required columns: {missing}")

    evidence = Evidence(
        case_id=case_id,
        filename=file_path.name,
        source=source,
        evidence_type="csv",
        file_size=file_path.stat().st_size,
        sha256=_sha256_file(file_path),
        ingested_at=ingested_at or datetime.now(timezone.utc),
        processing_status="pending",
    )

    events: list[Event] = []
    for row_number, row in enumerate(dataframe.itertuples(index=False), start=2):
        values = row._asdict()
        events.append(
            Event(
                case_id=case_id,
                evidence=evidence,
                timestamp=_normalize_timestamp(values["timestamp"], row_number),
                event_type=_normalize_value(values["event_type"]),
                source=_normalize_value(values["source"]),
                user=_normalize_value(values["user"]),
                device=_normalize_value(values["device"]),
                ip_address=_normalize_value(values["ip_address"]),
                application=_normalize_value(values["application"]),
                process=_normalize_value(values["process"]),
                file_path=_normalize_value(values["file_path"]),
                description=_normalize_value(values["description"]),
            )
        )

    return evidence, events