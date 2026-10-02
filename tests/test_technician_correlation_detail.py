import pytest

from engine.correlation import Correlation
from engine.diagnostic_case import DiagnosticCase
from engine.finding import Finding
from engine.technician_case_evidence_overview import (
    TechnicianCaseEvidenceOverview,
)
from engine.technician_correlation_detail import (
    TechnicianCorrelationDetail,
)
from engine.technician_recovery_cycle_history import (
    TechnicianRecoveryCycleHistory,
)
from engine.technician_workflow import TechnicianWorkflow


def create_detail():
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

    workflow = TechnicianWorkflow(case)

    history = TechnicianRecoveryCycleHistory(
        workflow
    )

    detail = TechnicianCorrelationDetail(
        workflow,
        history,
        correlation,
    )

    return detail, workflow, history, correlation


def test_requires_workflow():
    _, _, history, correlation = create_detail()

    with pytest.raises(ValueError):
        TechnicianCorrelationDetail(
            None,
            history,
            correlation,
        )


def test_requires_cycle_history():
    _, workflow, _, correlation = create_detail()

    with pytest.raises(ValueError):
        TechnicianCorrelationDetail(
            workflow,
            None,
            correlation,
        )


def test_requires_matching_cycle_history():
    detail, workflow, _, correlation = create_detail()

    other_case = DiagnosticCase()
    other_workflow = TechnicianWorkflow(other_case)
    other_history = TechnicianRecoveryCycleHistory(
        other_workflow
    )

    with pytest.raises(ValueError):
        TechnicianCorrelationDetail(
            workflow,
            other_history,
            correlation,
        )


def test_requires_correlation():
    _, workflow, history, _ = create_detail()

    with pytest.raises(ValueError):
        TechnicianCorrelationDetail(
            workflow,
            history,
            None,
        )


def test_correlation_must_belong_to_workflow_case():
    detail, workflow, history, _ = create_detail()

    other_finding = Finding(
        "CPU_SPIKE",
        "CPU",
        "MEDIUM",
        "CPU activity increased.",
    )

    other_correlation = Correlation(
        "CPU_SPIKE + DISK_ACTIVITY",
        [other_finding],
        "MEDIUM",
        "CPU activity is correlated with disk activity.",
    )

    with pytest.raises(ValueError):
        TechnicianCorrelationDetail(
            workflow,
            history,
            other_correlation,
        )


def test_exposes_workflow():
    detail, workflow, _, _ = create_detail()

    assert detail.workflow is workflow


def test_exposes_cycle_history():
    detail, _, history, _ = create_detail()

    assert detail.cycle_history is history


def test_exposes_correlation():
    detail, _, _, correlation = create_detail()

    assert detail.correlation is correlation


def test_exposes_correlation_type():
    detail, _, _, correlation = create_detail()

    assert (
        detail.correlation_type
        == correlation.correlation_type
    )


def test_exposes_findings():
    detail, _, _, correlation = create_detail()

    assert detail.findings == correlation.findings


def test_exposes_findings_as_copy():
    detail, _, _, correlation = create_detail()

    findings = detail.findings

    assert findings == correlation.findings
    assert findings is not correlation.findings


def test_exposes_strength():
    detail, _, _, correlation = create_detail()

    assert detail.strength == correlation.strength


def test_exposes_explanation():
    detail, _, _, correlation = create_detail()

    assert detail.explanation == correlation.explanation


def test_correlation_reference_is_preserved():
    detail, _, _, correlation = create_detail()

    assert detail.correlation is correlation