"""Deterministic evidence-backed inference for CHITRAGUPT events."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import Event


_FINDING_TYPE = "possible_file_transfer"
_FINDING_TITLE = "Possible file-transfer activity"
_RANSOMWARE_FINDING_TYPE = "possible_ransomware_activity"
_RANSOMWARE_FINDING_TITLE = "Possible ransomware activity"
_RULE_TO_FINDING_TYPE = {
    _FINDING_TYPE: (_FINDING_TYPE, _FINDING_TITLE),
    _RANSOMWARE_FINDING_TYPE: (
        _RANSOMWARE_FINDING_TYPE,
        _RANSOMWARE_FINDING_TITLE,
    ),
}


def _event_sort_key(event: Event) -> tuple[int, str, int]:
    timestamp = getattr(event, "timestamp", None)
    timestamp_text = ""
    if isinstance(timestamp, datetime):
        timestamp_text = timestamp.isoformat()
    return (0 if timestamp_text else 1, timestamp_text, int(event.id))


def _event_value_list(events: list[Event], attribute: str) -> list[str]:
    values: list[str] = []
    for event in events:
        value = getattr(event, attribute, None)
        if value and value not in values:
            values.append(str(value))
    return values


def _describe_event_sequence(events: list[Event], *, finding_type: str) -> str:
    if not events:
        return (
            "No supporting events were available for this finding. The available evidence is insufficient "
            "to describe the underlying activity beyond the rule match and correlation signals."
        )

    ordered_events = sorted(events, key=_event_sort_key)
    user_names = _event_value_list(ordered_events, "user")
    device_names = _event_value_list(ordered_events, "device")
    applications = _event_value_list(ordered_events, "application")
    file_targets = []
    for event in ordered_events:
        file_path = getattr(event, "file_path", None)
        if file_path and file_path not in file_targets:
            file_targets.append(str(file_path))

    event_types = [
        str(event.event_type)
        for event in ordered_events
        if getattr(event, "event_type", None)
    ]
    context_bits = []
    if user_names:
        context_bits.append(f"user {', '.join(user_names)}")
    if device_names:
        context_bits.append(f"device {', '.join(device_names)}")
    if applications:
        context_bits.append(f"application {', '.join(applications)}")
    if file_targets:
        context_bits.append(f"file path(s) {', '.join(file_targets[:3])}")
    if event_types:
        sequence_text = " -> ".join(event_types[:5])
        context_bits.append(f"event sequence {sequence_text}")

    if not context_bits:
        return (
            "The available supporting events do not provide enough detail to describe the activity beyond the "
            "rule match and correlation signals."
        )

    observed_context = "; ".join(context_bits)
    if finding_type == _FINDING_TYPE:
        description = (
            f"Observed supporting events include {observed_context}. This pattern is consistent with a file-transfer or removable-media indicator in the available evidence, "
            "but the available evidence does not establish that a transfer completed successfully."
        )
    else:
        description = (
            f"Observed supporting events include {observed_context}. This pattern may be consistent with ransomware-related activity in the available evidence, "
            "but the available evidence does not establish execution, encryption, or a successful ransomware payload without explicit supporting events."
        )
    return description


def infer_findings(
    events: list[Event],
    rule_results: list[dict],
    correlations: list[dict],
    isolation_forest_results: list[dict],
    lof_results: list[dict],
) -> list[dict]:
    """Combine supplied forensic signals into deterministic investigation findings."""
    matched_rules_by_finding_type = {
        finding_type: {} for finding_type in _RULE_TO_FINDING_TYPE
    }
    for rule_result in rule_results:
        rule_id = rule_result.get("rule_id")
        if rule_id in _RULE_TO_FINDING_TYPE and rule_result.get("matched") is True:
            if "event_id" not in rule_result:
                raise ValueError("Rule results must identify their event.")
            matched_rules_by_finding_type[rule_id].setdefault(
                rule_result["event_id"], []
            ).append(rule_result)

    findings = []
    for rule_id, (finding_type, finding_title) in _RULE_TO_FINDING_TYPE.items():
        for event_id in sorted(matched_rules_by_finding_type[rule_id]):
            event_correlations = [
                correlation
                for correlation in correlations
                if event_id in (
                    correlation["event_id_a"],
                    correlation["event_id_b"],
                )
            ]
            if not event_correlations:
                continue

            supporting_event_ids = {event_id}
            for correlation in event_correlations:
                supporting_event_ids.update(
                    (correlation["event_id_a"], correlation["event_id_b"])
                )
            sorted_supporting_event_ids = sorted(supporting_event_ids)

            relevant_isolation_forest_results = [
                result
                for result in isolation_forest_results
                if result["event_id"] in supporting_event_ids
            ]
            relevant_lof_results = [
                result
                for result in lof_results
                if result["event_id"] in supporting_event_ids
            ]

            confidence = 0.50
            if any(result.get("is_anomaly") is True for result in relevant_isolation_forest_results):
                confidence += 0.20
            if any(result.get("is_anomaly") is True for result in relevant_lof_results):
                confidence += 0.20
            confidence = round(min(confidence, 0.90), 2)

            supporting_events = [
                event
                for event in sorted(events, key=_event_sort_key)
                if event.id in sorted_supporting_event_ids
            ]
            description = _describe_event_sequence(
                supporting_events,
                finding_type=finding_type,
            )
            if relevant_isolation_forest_results or relevant_lof_results:
                model_summary = []
                if any(result.get("is_anomaly") is True for result in relevant_isolation_forest_results):
                    model_summary.append("Isolation Forest")
                if any(result.get("is_anomaly") is True for result in relevant_lof_results):
                    model_summary.append("LOF")
                if model_summary:
                    description += (
                        f" Additional anomaly indicators were produced by {', '.join(model_summary)} for related events, "
                        "but these indicators are not proof of malicious activity on their own."
                    )
            if event_correlations:
                shared_attributes = sorted(
                    {
                        attribute
                        for correlation in event_correlations
                        for attribute in correlation.get("shared_attributes", [])
                    }
                )
                if shared_attributes:
                    description += (
                        f" Related events also shared {', '.join(shared_attributes)} within the same activity window."
                    )

            findings.append(
                {
                    "finding_type": finding_type,
                    "title": finding_title,
                    "description": description,
                    "confidence": confidence,
                    "supporting_event_ids": sorted_supporting_event_ids,
                    "signals": {
                        "rules": sorted(
                            matched_rules_by_finding_type[rule_id][event_id],
                            key=lambda result: result["event_id"],
                        ),
                        "correlations": sorted(
                            event_correlations,
                            key=lambda correlation: (
                                correlation["event_id_a"],
                                correlation["event_id_b"],
                            ),
                        ),
                        "isolation_forest": sorted(
                            relevant_isolation_forest_results,
                            key=lambda result: result["event_id"],
                        ),
                        "lof": sorted(
                            relevant_lof_results,
                            key=lambda result: result["event_id"],
                        ),
                    },
                }
            )

    return findings
