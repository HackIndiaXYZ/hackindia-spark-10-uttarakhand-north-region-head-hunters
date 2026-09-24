"""Deterministic correlation of nearby events sharing investigation attributes."""

from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backend.app.models import Event


_CORRELATION_ATTRIBUTES = (
    "user",
    "device",
    "ip_address",
    "application",
    "file_path",
)


def correlate_events(
    events: list[Event],
    *,
    window_seconds: int = 300,
) -> list[dict]:
    """Return unique event pairs within the time window sharing attributes."""
    correlations = []

    for index, first_event in enumerate(events):
        first_timestamp = first_event.timestamp
        if not isinstance(first_timestamp, datetime):
            continue

        for second_event in events[index + 1 :]:
            if first_event is second_event or first_event.id == second_event.id:
                continue

            second_timestamp = second_event.timestamp
            if not isinstance(second_timestamp, datetime):
                continue

            try:
                time_difference = abs(
                    (first_timestamp - second_timestamp).total_seconds()
                )
            except TypeError:
                first_is_aware = first_timestamp.utcoffset() is not None
                second_is_aware = second_timestamp.utcoffset() is not None
                if first_is_aware != second_is_aware:
                    raise ValueError(
                        "Event timestamps must use compatible timezone information."
                    ) from None
                continue

            if time_difference > window_seconds:
                continue

            shared_attributes = [
                attribute
                for attribute in _CORRELATION_ATTRIBUTES
                if (
                    getattr(first_event, attribute) not in (None, "")
                    and getattr(first_event, attribute)
                    == getattr(second_event, attribute)
                )
            ]
            if not shared_attributes:
                continue

            if first_timestamp < second_timestamp or (
                first_timestamp == second_timestamp
                and first_event.id <= second_event.id
            ):
                event_a, event_b = first_event, second_event
            else:
                event_a, event_b = second_event, first_event

            correlations.append(
                {
                    "event_id_a": event_a.id,
                    "event_id_b": event_b.id,
                    "time_difference_seconds": time_difference,
                    "shared_attributes": shared_attributes,
                }
            )

    correlations.sort(key=lambda correlation: (
        correlation["event_id_a"],
        correlation["event_id_b"],
    ))
    return correlations