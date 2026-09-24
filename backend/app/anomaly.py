"""Deterministic Isolation Forest anomaly detection for CHITRAGUPT events."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sklearn.ensemble import IsolationForest

from backend.app.features import extract_event_features

if TYPE_CHECKING:
    from backend.app.models import Event


def run_isolation_forest(
    events: list[Event],
    *,
    contamination: str | float = "auto",
    random_state: int = 42,
) -> list[dict]:
    """Run Isolation Forest and return anomaly results in input order."""
    if not events:
        return []

    feature_vectors = [
        list(extract_event_features(event).values()) for event in events
    ]
    model = IsolationForest(
        contamination=contamination,
        random_state=random_state,
    )
    model.fit(feature_vectors)

    anomaly_scores = model.decision_function(feature_vectors)
    predictions = model.predict(feature_vectors)

    return [
        {
            "event_id": event.id,
            "model_name": "isolation_forest",
            "anomaly_score": float(anomaly_score),
            "is_anomaly": bool(prediction == -1),
        }
        for event, anomaly_score, prediction in zip(
            events,
            anomaly_scores,
            predictions,
        )
    ]
