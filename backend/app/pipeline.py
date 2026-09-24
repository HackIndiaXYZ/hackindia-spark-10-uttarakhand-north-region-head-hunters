"""Deterministic end-to-end investigation pipeline for CHITRAGUPT."""

from backend.app.anomaly import run_isolation_forest
from backend.app.anomaly_persistence import persist_anomalies
from backend.app.correlation import correlate_events
from backend.app.finding_persistence import persist_findings
from backend.app.inference import infer_findings
from backend.app.lof import run_lof
from backend.app.queries import get_events_by_case
from backend.app.rules import evaluate_file_transfer_rule


def run_investigation_pipeline(case_id: int) -> dict:
    """Run the investigation components and persist their results for a case."""
    events = get_events_by_case(case_id)
    if not events:
        raise ValueError(f"No events found for case ID {case_id}.")

    rule_results = [evaluate_file_transfer_rule(event) for event in events]
    correlations = correlate_events(events)
    isolation_forest_results = run_isolation_forest(events)
    lof_results = run_lof(events)
    findings = infer_findings(
        events,
        rule_results,
        correlations,
        isolation_forest_results,
        lof_results,
    )

    all_anomaly_results = isolation_forest_results + lof_results
    persisted_anomalies = persist_anomalies(case_id, all_anomaly_results)
    persisted_findings = persist_findings(case_id, findings)

    return {
        "case_id": case_id,
        "event_count": len(events),
        "rule_results": rule_results,
        "correlations": correlations,
        "isolation_forest_results": isolation_forest_results,
        "lof_results": lof_results,
        "findings": findings,
        "persisted_anomaly_ids": [anomaly.id for anomaly in persisted_anomalies],
        "persisted_finding_ids": [finding.id for finding in persisted_findings],
    }
