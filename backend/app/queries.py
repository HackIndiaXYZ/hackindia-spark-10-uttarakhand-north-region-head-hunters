"""Read-only queries for persisted CHITRAGUPT events."""

from sqlalchemy import select

from backend.app.database import SessionLocal
from backend.app.models import Event


def get_events_by_case(case_id: int) -> list[Event]:
    """Return events for a case ordered by timestamp ascending."""
    session = SessionLocal()
    try:
        statement = select(Event).where(Event.case_id == case_id).order_by(Event.timestamp.asc())
        return list(session.scalars(statement).all())
    finally:
        session.close()
