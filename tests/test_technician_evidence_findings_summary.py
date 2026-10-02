import pytest

from engine.diagnostic_case import DiagnosticCase
from engine.technician_evidence_findings_summary import (
    TechnicianEvidenceFindingsSummary,
)
from engine.technician_recovery_cycle_history import (
    TechnicianRecoveryCycleHistory,
)
from engine.technician_workflow import TechnicianWorkflow


@pytest.fixture
def workflow():
    workflow = TechnicianWorkflow(
        DiagnosticCase()
    )
    workflow.start_investigation()
    return workflow


@pytest.fixture
def history(workflow):
    return TechnicianRecoveryCycleHistory(
        workflow
    )


@pytest.fixture
def summary(workflow, history):
    return TechnicianEvidenceFindingsSummary(
        workflow,
        history,
    )


def test_summary_requires_workflow():
    with pytest.raises(ValueError):
        TechnicianEvidenceFindingsSummary(
            None,
            None,
        )


def test_summary_requires_cycle_history(
    workflow,
):
    with pytest.raises(ValueError):
        TechnicianEvidenceFindingsSummary(
            workflow,
            None,
        )


def test_summary_rejects_foreign_history(
    workflow,
):
    other_workflow = TechnicianWorkflow(
        DiagnosticCase()
    )

    other_history = TechnicianRecoveryCycleHistory(
        other_workflow
    )

    with pytest.raises(ValueError):
        TechnicianEvidenceFindingsSummary(
            workflow,
            other_history,
        )


def test_summary_exposes_workflow(
    workflow,
    summary,
):
    assert summary.workflow is workflow


def test_summary_exposes_cycle_history(
    history,
    summary,
):
    assert summary.cycle_history is history


def test_summary_exposes_findings(
    workflow,
    summary,
):
    assert summary.findings == workflow.case.findings


def test_summary_exposes_finding_count(
    workflow,
    summary,
):
    assert summary.finding_count == len(
        workflow.case.findings
    )


def test_summary_exposes_correlations(
    workflow,
    summary,
):
    assert (
        summary.correlations
        == workflow.case.correlations
    )


def test_summary_exposes_correlation_count(
    workflow,
    summary,
):
    assert (
        summary.correlation_count
        == len(workflow.case.correlations)
    )


def test_summary_exposes_evidence_count(
    workflow,
    summary,
):
    assert summary.evidence_count == len(
        workflow.case.evidence
    )


def test_summary_is_read_only(
    workflow,
    summary,
):
    findings = summary.findings

    if hasattr(findings, "clear"):
        findings.clear()

    assert summary.finding_count == len(
        workflow.case.findings
    )


def test_summary_does_not_change_workflow(
    workflow,
    history,
):
    original_state = workflow.state
    original_history = workflow.history

    TechnicianEvidenceFindingsSummary(
        workflow,
        history,
    )

    assert workflow.state is original_state
    assert workflow.history == original_history


def test_summary_updates_with_case_data(
    workflow,
    history,
):
    summary = TechnicianEvidenceFindingsSummary(
        workflow,
        history,
    )

    assert summary.finding_count == len(
        workflow.case.findings
    )

    assert summary.correlation_count == len(
        workflow.case.correlations
    )

    assert summary.evidence_count == len(
        workflow.case.evidence
    )