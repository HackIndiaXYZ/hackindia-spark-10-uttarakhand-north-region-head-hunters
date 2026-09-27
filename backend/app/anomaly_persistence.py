"""Persistence helpers for deterministic CHITRAGUPT anomaly results."""

from datetime import datetime, timezone

from .database import SessionLocal
from .models import Anomaly


def persist_anomalies(
    case_id: int,
    anomaly_results: list[dict],
) -> list[Anomaly]:
    """Persist anomaly results for a case and return refreshed records."""
    if not anomaly_results:
        return []

    persisted_anomalies = [
        Anomaly(
            case_id=case_id,
            event_id=result["event_id"],
            model_name=result["model_name"],
            anomaly_score=result["anomaly_score"],
            is_anomaly=result["is_anomaly"],
            created_at=datetime.now(timezone.utc),
        )
        for result in anomaly_results
    ]

    session = SessionLocal()
    try:
        session.add_all(persisted_anomalies)
        session.commit()
        for anomaly in persisted_anomalies:
            session.refresh(anomaly)
        return persisted_anomalies
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
