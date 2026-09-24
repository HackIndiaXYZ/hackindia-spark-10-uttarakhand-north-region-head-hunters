"""Deterministic Local Outlier Factor detection for CHITRAGUPT events."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sklearn.neighbors import LocalOutlierFactor

from backend.app.features import extract_event_features

if TYPE_CHECKING:
    from backend.app.models import Event


def run_lof(
    events: list[Event],
    *,
    n_neighbors: int = 5,
    contamination: str | float = "auto",
) -> list[dict]:
    """Run Local Outlier Factor and return anomaly results in input order."""
    if not events:
        return []

    feature_vectors = [
        list(extract_event_features(event).values()) for event in events
    ]
    model = LocalOutlierFactor(
        n_neighbors=n_neighbors,
        contamination=contamination,
    )
    predictions = model.fit_predict(feature_vectors)

    return [
        {
            "event_id": event.id,
            "model_name": "lof",
            "anomaly_score": float(anomaly_score),
            "is_anomaly": bool(prediction == -1),
        }
        for event, anomaly_score, prediction in zip(
            events,
            model.negative_outlier_factor_,
            predictions,
        )
    ]
