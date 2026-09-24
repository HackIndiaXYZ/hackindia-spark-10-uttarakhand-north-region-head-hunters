from fastapi import FastAPI

from backend.app.queries import get_events_by_case

app = FastAPI(title="CHITRAGUPT API")


@app.get("/")
def root():
    return {"message": "CHITRAGUPT API is running"}


@app.get("/cases/{case_id}/events")
def case_events(case_id: int):
    """Return persisted events for a case in database query order."""
    events = get_events_by_case(case_id)
    return [
        {
            "id": event.id,
            "case_id": event.case_id,
            "evidence_id": event.evidence_id,
            "timestamp": event.timestamp,
            "event_type": event.event_type,
            "source": event.source,
            "user": event.user,
            "device": event.device,
            "ip_address": event.ip_address,
            "application": event.application,
            "process": event.process,
            "file_path": event.file_path,
            "description": event.description,
        }
        for event in events
    ]