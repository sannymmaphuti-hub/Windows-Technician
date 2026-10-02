import pytest

from engine.diagnostic_case import DiagnosticCase
from engine.technician_case_evidence_overview import (
    TechnicianCaseEvidenceOverview,
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
def overview(workflow, history):
    return TechnicianCaseEvidenceOverview(
        workflow,
        history,
    )


def test_overview_requires_workflow():
    with pytest.raises(ValueError):
        TechnicianCaseEvidenceOverview(
            None,
            None,
        )


def test_overview_requires_cycle_history(
    workflow,
):
    with pytest.raises(ValueError):
        TechnicianCaseEvidenceOverview(
            workflow,
            None,
        )


def test_overview_rejects_foreign_history(
    workflow,
):
    other_workflow = TechnicianWorkflow(
        DiagnosticCase()
    )

    other_history = TechnicianRecoveryCycleHistory(
        other_workflow
    )

    with pytest.raises(ValueError):
        TechnicianCaseEvidenceOverview(
            workflow,
            other_history,
        )


def test_overview_exposes_workflow(
    workflow,
    overview,
):
    assert overview.workflow is workflow


def test_overview_exposes_cycle_history(
    history,
    overview,
):
    assert overview.cycle_history is history


def test_overview_exposes_case_id(
    workflow,
    overview,
):
    assert overview.case_id == workflow.case.case_id


def test_overview_exposes_evidence(
    workflow,
    overview,
):
    assert overview.evidence == workflow.case.evidence


def test_overview_exposes_evidence_count(
    workflow,
    overview,
):
    assert overview.evidence_count == len(
        workflow.case.evidence
    )


def test_overview_evidence_is_read_only(
    workflow,
    overview,
):
    evidence = overview.evidence

    if hasattr(evidence, "clear"):
        evidence.clear()

    assert overview.evidence_count == len(
        workflow.case.evidence
    )


def test_overview_exposes_findings(
    workflow,
    overview,
):
    assert overview.findings == workflow.case.findings


def test_overview_exposes_finding_count(
    workflow,
    overview,
):
    assert overview.finding_count == len(
        workflow.case.findings
    )


def test_overview_exposes_correlations(
    workflow,
    overview,
):
    assert (
        overview.correlations
        == workflow.case.correlations
    )


def test_overview_exposes_correlation_count(
    workflow,
    overview,
):
    assert (
        overview.correlation_count
        == len(workflow.case.correlations)
    )


def test_overview_does_not_change_workflow(
    workflow,
    history,
):
    original_state = workflow.state
    original_history = workflow.history

    TechnicianCaseEvidenceOverview(
        workflow,
        history,
    )

    assert workflow.state is original_state
    assert workflow.history == original_history