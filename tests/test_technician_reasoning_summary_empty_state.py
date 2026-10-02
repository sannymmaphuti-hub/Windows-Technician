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


def test_empty_findings_are_list():
    summary = create_summary()

    assert summary.findings == []
    assert isinstance(summary.findings, list)


def test_empty_correlations_are_list():
    summary = create_summary()

    assert summary.correlations == []
    assert isinstance(summary.correlations, list)


def test_empty_root_causes_are_list():
    summary = create_summary()

    assert summary.root_causes == []
    assert isinstance(summary.root_causes, list)


def test_empty_recommendations_are_list():
    summary = create_summary()

    assert summary.recommendations == []
    assert isinstance(summary.recommendations, list)


def test_empty_counts_are_zero():
    summary = create_summary()

    assert summary.finding_count == 0
    assert summary.correlation_count == 0
    assert summary.root_cause_count == 0
    assert summary.recommendation_count == 0


def test_empty_overview_is_consistent():
    summary = create_summary()

    overview = summary.overview

    assert overview["finding_count"] == 0
    assert overview["correlation_count"] == 0
    assert overview["root_cause_count"] == 0
    assert overview["recommendation_count"] == 0

    assert overview["findings"] == []
    assert overview["correlations"] == []
    assert overview["root_causes"] == []
    assert overview["recommendations"] == []