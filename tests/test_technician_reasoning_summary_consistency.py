from engine.diagnostic_case import DiagnosticCase
from engine.technician_recovery_cycle_history import (
    TechnicianRecoveryCycleHistory,
)
from engine.technician_reasoning_summary import (
    TechnicianReasoningSummary,
)
from engine.technician_workflow import TechnicianWorkflow


def create_summary():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)

    history = TechnicianRecoveryCycleHistory(
        workflow
    )

    summary = TechnicianReasoningSummary(
        workflow,
        history,
    )

    return summary, case


def test_finding_count_matches_findings():
    summary, _ = create_summary()

    assert summary.finding_count == len(summary.findings)


def test_correlation_count_matches_correlations():
    summary, _ = create_summary()

    assert summary.correlation_count == len(summary.correlations)


def test_root_cause_count_matches_root_causes():
    summary, _ = create_summary()

    assert summary.root_cause_count == len(summary.root_causes)


def test_recommendation_count_matches_recommendations():
    summary, _ = create_summary()

    assert (
        summary.recommendation_count
        == len(summary.recommendations)
    )


def test_overview_counts_match_overview_collections():
    summary, _ = create_summary()

    overview = summary.overview

    assert (
        overview["finding_count"]
        == len(overview["findings"])
    )
    assert (
        overview["correlation_count"]
        == len(overview["correlations"])
    )
    assert (
        overview["root_cause_count"]
        == len(overview["root_causes"])
    )
    assert (
        overview["recommendation_count"]
        == len(overview["recommendations"])
    )