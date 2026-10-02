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


def test_findings_returns_copy():
    summary, case = create_summary()

    findings = summary.findings

    assert findings is not case.findings


def test_correlations_returns_copy():
    summary, case = create_summary()

    correlations = summary.correlations

    assert correlations is not case.correlations


def test_root_causes_returns_copy():
    summary, case = create_summary()

    root_causes = summary.root_causes

    assert root_causes is not case.root_causes


def test_recommendations_returns_copy():
    summary, case = create_summary()

    recommendations = summary.recommendations

    assert recommendations is not case.recommendations


def test_findings_mutation_does_not_change_case():
    summary, case = create_summary()

    findings = summary.findings
    original_count = len(case.findings)

    findings.append("fake-finding")

    assert len(case.findings) == original_count


def test_correlations_mutation_does_not_change_case():
    summary, case = create_summary()

    correlations = summary.correlations
    original_count = len(case.correlations)

    correlations.append("fake-correlation")

    assert len(case.correlations) == original_count


def test_root_causes_mutation_does_not_change_case():
    summary, case = create_summary()

    root_causes = summary.root_causes
    original_count = len(case.root_causes)

    root_causes.append("fake-root-cause")

    assert len(case.root_causes) == original_count


def test_recommendations_mutation_does_not_change_case():
    summary, case = create_summary()

    recommendations = summary.recommendations
    original_count = len(case.recommendations)

    recommendations.append("fake-recommendation")

    assert len(case.recommendations) == original_count