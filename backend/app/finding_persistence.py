"""Persistence helpers for deterministic CHITRAGUPT findings."""

from datetime import datetime, timezone

from backend.app.database import SessionLocal
from backend.app.models import Finding


def persist_findings(case_id: int, findings: list[dict]) -> list[Finding]:
    """Persist inference findings for a case and return refreshed records."""
    if not findings:
        return []

    persisted_findings = [
        Finding(
            case_id=case_id,
            finding_type=finding["finding_type"],
            title=finding["title"],
            description=finding["description"],
            confidence=finding["confidence"],
            status="open",
            created_at=datetime.now(timezone.utc),
        )
        for finding in findings
    ]

    session = SessionLocal()
    try:
        session.add_all(persisted_findings)
        session.commit()
        for finding in persisted_findings:
            session.refresh(finding)
        return persisted_findings
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
