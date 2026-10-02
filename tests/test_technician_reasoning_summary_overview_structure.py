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

    return summary


def test_overview_contains_expected_keys():
    summary = create_summary()

    assert set(summary.overview.keys()) == {
        "finding_count",
        "correlation_count",
        "root_cause_count",
        "recommendation_count",
        "findings",
        "correlations",
        "root_causes",
        "recommendations",
    }


def test_overview_counts_match_properties():
    summary = create_summary()

    overview = summary.overview

    assert overview["finding_count"] == summary.finding_count
    assert overview["correlation_count"] == summary.correlation_count
    assert overview["root_cause_count"] == summary.root_cause_count
    assert (
        overview["recommendation_count"]
        == summary.recommendation_count
    )


def test_overview_collections_match_properties():
    summary = create_summary()

    overview = summary.overview

    assert overview["findings"] == summary.findings
    assert overview["correlations"] == summary.correlations
    assert overview["root_causes"] == summary.root_causes
    assert overview["recommendations"] == summary.recommendations


def test_overview_counts_are_integers():
    summary = create_summary()

    overview = summary.overview

    assert isinstance(overview["finding_count"], int)
    assert isinstance(overview["correlation_count"], int)
    assert isinstance(overview["root_cause_count"], int)
    assert isinstance(
        overview["recommendation_count"],
        int,
    )