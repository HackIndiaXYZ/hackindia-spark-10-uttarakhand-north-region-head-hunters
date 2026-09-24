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
_RANSOMWARE_RULE_ID = "possible_ransomware_activity"
_RANSOMWARE_EVENT_TYPES = {
    "suspicious_download",
    "process_execution",
    "rapid_file_activity",
    "file_encryption",
    "ransom_note_created",
}
_RANSOMWARE_DESCRIPTION_KEYWORDS = (
    "suspicious download",
    "process execution",
    "rapid file activity",
    "file encryption",
    "ransom note",
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


def evaluate_ransomware_rule(event: Event) -> dict:
    """Evaluate whether an event has an explicit ransomware-stage indicator."""
    event_type = event.event_type
    if event_type in _RANSOMWARE_EVENT_TYPES:
        return {
            "event_id": event.id,
            "rule_id": _RANSOMWARE_RULE_ID,
            "matched": True,
            "reason": f"Matched event_type value '{event_type}'.",
        }

    description = event.description
    if description:
        description_casefolded = description.casefold()
        for keyword in _RANSOMWARE_DESCRIPTION_KEYWORDS:
            if keyword in description_casefolded:
                return {
                    "event_id": event.id,
                    "rule_id": _RANSOMWARE_RULE_ID,
                    "matched": True,
                    "reason": f"Matched description keyword '{keyword}'.",
                }

    return {
        "event_id": event.id,
        "rule_id": _RANSOMWARE_RULE_ID,
        "matched": False,
        "reason": "No explicit ransomware activity indicator found.",
    }
