"""Deterministic evidence-backed inference for CHITRAGUPT events."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backend.app.models import Event


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


def infer_findings(
    events: list[Event],
    rule_results: list[dict],
    correlations: list[dict],
    isolation_forest_results: list[dict],
    lof_results: list[dict],
) -> list[dict]:
    """Combine supplied forensic signals into deterministic investigation findings."""
    del events

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

            if finding_type == _FINDING_TYPE:
                description = (
                    "Finding based on an explicit file-transfer/removable-media "
                    "rule match and event correlation."
                )
            else:
                description = (
                    "Finding based on an explicit ransomware activity rule match "
                    "and event correlation."
                )
            if relevant_isolation_forest_results:
                description += " Supporting Isolation Forest anomaly-model signals are available."
            if relevant_lof_results:
                description += " Supporting LOF anomaly-model signals are available."

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
