"""Persist ingested evidence and events in PostgreSQL."""

from sqlalchemy import delete, select

from .database import SessionLocal
from .models import Evidence, Event


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


def delete_persisted_ingestion(evidence_id: int) -> None:
    """Delete an ingestion and its events after a downstream failure."""
    session = SessionLocal()
    try:
        event_ids = session.scalars(
            select(Event.id).where(Event.evidence_id == evidence_id)
        ).all()
        if event_ids:
            session.execute(delete(Event).where(Event.id.in_(event_ids)))
        session.execute(delete(Evidence).where(Evidence.id == evidence_id))
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
