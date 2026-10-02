from engine.correlation import Correlation
from engine.diagnostic_case import DiagnosticCase
from engine.finding import Finding
from engine.recommendation import Recommendation
from engine.root_cause import RootCauseCandidate
from engine.technician_recovery_cycle_history import (
    TechnicianRecoveryCycleHistory,
)
from engine.technician_reasoning_summary import (
    TechnicianReasoningSummary,
)
from engine.technician_workflow import TechnicianWorkflow


def create_summary():
    case = DiagnosticCase()

    finding = Finding(
        "MEMORY_PRESSURE",
        "MEMORY",
        "HIGH",
        "Memory pressure detected.",
    )
    case.findings.append(finding)

    correlation = Correlation(
        "MEMORY_PRESSURE + CPU_SPIKE",
        [finding],
        "HIGH",
        "Memory pressure is correlated with CPU activity.",
    )
    case.correlations.append(correlation)

    root_cause = RootCauseCandidate(
        "Insufficient available memory",
        "MEMORY",
        0.90,
        evidence=["MEMORY_PRESSURE"],
        reason="Available memory is consistently low.",
    )
    case.root_causes.append(root_cause)

    recommendation = Recommendation(
        "MEMORY_REVIEW",
        "MEMORY",
        "HIGH",
        "Review memory usage and reduce unnecessary processes.",
        "Memory pressure indicates that available memory "
        "is consistently low.",
    )
    case.recommendations.append(recommendation)

    workflow = TechnicianWorkflow(case)

    history = TechnicianRecoveryCycleHistory(
        workflow
    )

    summary = TechnicianReasoningSummary(
        workflow,
        history,
    )

    return summary


def test_overview_returns_reasoning_counts():
    summary = create_summary()

    overview = summary.overview

    assert overview["finding_count"] == 1
    assert overview["correlation_count"] == 1
    assert overview["root_cause_count"] == 1
    assert overview["recommendation_count"] == 1


def test_overview_returns_reasoning_objects():
    summary = create_summary()

    overview = summary.overview

    assert overview["findings"] == summary.findings
    assert overview["correlations"] == summary.correlations
    assert overview["root_causes"] == summary.root_causes
    assert overview["recommendations"] == summary.recommendations


def test_overview_contains_all_reasoning_sections():
    summary = create_summary()

    overview = summary.overview

    assert set(overview) == {
        "finding_count",
        "correlation_count",
        "root_cause_count",
        "recommendation_count",
        "findings",
        "correlations",
        "root_causes",
        "recommendations",
    }


def test_overview_does_not_expose_internal_case_lists():
    summary = create_summary()

    overview = summary.overview

    assert overview["findings"] is not summary.workflow.case.findings
    assert (
        overview["correlations"]
        is not summary.workflow.case.correlations
    )
    assert (
        overview["root_causes"]
        is not summary.workflow.case.root_causes
    )
    assert (
        overview["recommendations"]
        is not summary.workflow.case.recommendations
    )


def test_empty_reasoning_summary_has_empty_overview():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)
    history = TechnicianRecoveryCycleHistory(workflow)

    summary = TechnicianReasoningSummary(
        workflow,
        history,
    )

    overview = summary.overview

    assert overview["finding_count"] == 0
    assert overview["correlation_count"] == 0
    assert overview["root_cause_count"] == 0
    assert overview["recommendation_count"] == 0

    assert overview["findings"] == []
    assert overview["correlations"] == []
    assert overview["root_causes"] == []
    assert overview["recommendations"] == []