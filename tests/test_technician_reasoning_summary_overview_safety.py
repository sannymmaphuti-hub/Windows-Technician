from engine.diagnostic_case import DiagnosticCase
from engine.finding import Finding
from engine.recommendation import Recommendation
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

    recommendation = Recommendation(
        "MEMORY_REVIEW",
        "MEMORY",
        "HIGH",
        "Review memory usage.",
        "Memory pressure requires review.",
    )

    case.findings.append(finding)
    case.recommendations.append(recommendation)

    workflow = TechnicianWorkflow(case)

    history = TechnicianRecoveryCycleHistory(
        workflow
    )

    return TechnicianReasoningSummary(
        workflow,
        history,
    )


def test_overview_findings_are_independent():
    summary = create_summary()

    overview = summary.overview
    overview["findings"].clear()

    assert summary.finding_count == 1


def test_overview_recommendations_are_independent():
    summary = create_summary()

    overview = summary.overview
    overview["recommendations"].clear()

    assert summary.recommendation_count == 1


def test_each_overview_access_returns_new_lists():
    summary = create_summary()

    first = summary.overview
    second = summary.overview

    assert first["findings"] is not second["findings"]
    assert first["correlations"] is not second["correlations"]
    assert first["root_causes"] is not second["root_causes"]
    assert first["recommendations"] is not second["recommendations"]


def test_overview_mutation_does_not_change_case():
    summary = create_summary()

    overview = summary.overview

    overview["findings"].append("unexpected")
    overview["recommendations"].append("unexpected")

    assert len(summary.workflow.case.findings) == 1
    assert len(summary.workflow.case.recommendations) == 1