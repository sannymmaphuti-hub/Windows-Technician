import pytest

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

    return (
        summary,
        workflow,
        history,
        finding,
        correlation,
        root_cause,
        recommendation,
    )


def test_requires_workflow():
    _, _, history, *_ = create_summary()

    with pytest.raises(ValueError):
        TechnicianReasoningSummary(
            None,
            history,
        )


def test_requires_cycle_history():
    _, workflow, _, *_ = create_summary()

    with pytest.raises(ValueError):
        TechnicianReasoningSummary(
            workflow,
            None,
        )


def test_requires_matching_cycle_history():
    _, workflow, _, *_ = create_summary()

    other_case = DiagnosticCase()
    other_workflow = TechnicianWorkflow(other_case)
    other_history = TechnicianRecoveryCycleHistory(
        other_workflow
    )

    with pytest.raises(ValueError):
        TechnicianReasoningSummary(
            workflow,
            other_history,
        )


def test_exposes_workflow():
    summary, workflow, *_ = create_summary()

    assert summary.workflow is workflow


def test_exposes_cycle_history():
    summary, _, history, *_ = create_summary()

    assert summary.cycle_history is history


def test_exposes_findings():
    summary, _, _, finding, *_ = create_summary()

    assert summary.findings == [finding]


def test_exposes_correlations():
    summary, _, _, _, correlation, *_ = create_summary()

    assert summary.correlations == [correlation]


def test_exposes_root_causes():
    summary, _, _, _, _, root_cause, *_ = create_summary()

    assert summary.root_causes == [root_cause]


def test_exposes_recommendations():
    summary, _, _, _, _, _, recommendation = create_summary()

    assert summary.recommendations == [recommendation]


def test_finding_count():
    summary, *_ = create_summary()

    assert summary.finding_count == 1


def test_correlation_count():
    summary, *_ = create_summary()

    assert summary.correlation_count == 1


def test_root_cause_count():
    summary, *_ = create_summary()

    assert summary.root_cause_count == 1


def test_recommendation_count():
    summary, *_ = create_summary()

    assert summary.recommendation_count == 1


def test_findings_are_returned_as_copy():
    summary, *_ = create_summary()

    findings = summary.findings

    assert findings is not summary.workflow.case.findings


def test_correlations_are_returned_as_copy():
    summary, *_ = create_summary()

    correlations = summary.correlations

    assert correlations is not summary.workflow.case.correlations


def test_root_causes_are_returned_as_copy():
    summary, *_ = create_summary()

    root_causes = summary.root_causes

    assert root_causes is not summary.workflow.case.root_causes


def test_recommendations_are_returned_as_copy():
    summary, *_ = create_summary()

    recommendations = summary.recommendations

    assert (
        recommendations
        is not summary.workflow.case.recommendations
    )