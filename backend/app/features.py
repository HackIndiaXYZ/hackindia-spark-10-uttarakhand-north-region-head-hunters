"""Deterministic numerical feature extraction for CHITRAGUPT events."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backend.app.models import Event


def _has_value(value: str | None) -> float:
    return 1.0 if value is not None and value.strip() else 0.0


def extract_event_features(event: Event) -> dict[str, float]:
    """Convert an event into deterministic numerical presence and time features."""
    timestamp = event.timestamp

    return {
        "hour_of_day": float(timestamp.hour) if timestamp is not None else -1.0,
        "day_of_week": float(timestamp.weekday()) if timestamp is not None else -1.0,
        "has_user": _has_value(event.user),
        "has_device": _has_value(event.device),
        "has_ip": _has_value(event.ip_address),
        "has_application": _has_value(event.application),
        "has_process": _has_value(event.process),
        "has_file_path": _has_value(event.file_path),
        "has_description": _has_value(event.description),
    }
