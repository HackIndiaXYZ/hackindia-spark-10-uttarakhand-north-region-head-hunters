"""Persist ingested evidence and events in PostgreSQL."""

from backend.app.database import SessionLocal


def persist_ingestion(evidence, events):
    """Persist an Evidence object and its associated Event objects."""
    session = SessionLocal()
    try:
        session.add(evidence)
        session.add_all(events)
        session.commit()
        session.refresh(evidence)
        return evidence
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
