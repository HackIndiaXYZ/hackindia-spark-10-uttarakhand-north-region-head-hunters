"""Read-only queries for persisted CHITRAGUPT events."""

from datetime import datetime

from sqlalchemy import select

from backend.app.database import SessionLocal
from backend.app.models import Event


def get_events_by_case(
    case_id: int,
    *,
    event_type: str | None = None,
    user: str | None = None,
    device: str | None = None,
    ip_address: str | None = None,
    application: str | None = None,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
) -> list[Event]:
    """Return case events matching optional filters in timestamp order."""
    session = SessionLocal()
    try:
        filters = [Event.case_id == case_id]
        if event_type is not None:
            filters.append(Event.event_type == event_type)
        if user is not None:
            filters.append(Event.user == user)
        if device is not None:
            filters.append(Event.device == device)
        if ip_address is not None:
            filters.append(Event.ip_address == ip_address)
        if application is not None:
            filters.append(Event.application == application)
        if start_time is not None:
            filters.append(Event.timestamp >= start_time)
        if end_time is not None:
            filters.append(Event.timestamp <= end_time)

        statement = select(Event).where(*filters).order_by(Event.timestamp.asc())
        return list(session.scalars(statement).all())
    finally:
        session.close()
