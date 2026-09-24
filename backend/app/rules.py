"""Deterministic forensic context rules for CHITRAGUPT events."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backend.app.models import Event


_RULE_ID = "possible_file_transfer"
_EXPLICIT_EVENT_TYPES = {
    "file_transfer",
    "usb_connect",
    "bluetooth_transfer",
    "removable_media",
}
_DESCRIPTION_KEYWORDS = (
    "file transfer",
    "usb",
    "bluetooth transfer",
    "removable media",
)


def evaluate_file_transfer_rule(event: Event) -> dict:
    """Evaluate whether an event has an explicit file-transfer indicator."""
    event_type = event.event_type
    if event_type in _EXPLICIT_EVENT_TYPES:
        return {
            "event_id": event.id,
            "rule_id": _RULE_ID,
            "matched": True,
            "reason": f"Matched event_type value '{event_type}'.",
        }

    description = event.description
    if description:
        description_casefolded = description.casefold()
        for keyword in _DESCRIPTION_KEYWORDS:
            if keyword in description_casefolded:
                return {
                    "event_id": event.id,
                    "rule_id": _RULE_ID,
                    "matched": True,
                    "reason": f"Matched description keyword '{keyword}'.",
                }

    return {
        "event_id": event.id,
        "rule_id": _RULE_ID,
        "matched": False,
        "reason": "No explicit file-transfer or removable-media indicator found.",
    }
