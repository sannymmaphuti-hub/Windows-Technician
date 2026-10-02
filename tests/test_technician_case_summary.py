import pytest

from engine.recommendation import Recommendation
from engine.technician_case_summary import TechnicianCaseSummary
from engine.technician_decision import (
    TechnicianDecision,
    TechnicianDecisionType,
)
from engine.technician_case_notes import TechnicianCaseNotes
from engine.technician_workflow import (
    TechnicianWorkflow,
    WorkflowState,
)


class FakeCase:
    case_id = "case-001"
    findings = ["finding-1"]
    root_causes = ["cause-1"]
    recommendations = []


@pytest.fixture
def workflow():
    workflow = TechnicianWorkflow(FakeCase())
    return workflow


@pytest.fixture
def recommendation():
    return Recommendation(
        "memory_review",
        "MEMORY",
        "HIGH",
        "Review memory-intensive processes.",
        "High memory usage may affect responsiveness.",
    )


@pytest.fixture
def summary(workflow):
    return TechnicianCaseSummary(workflow)


def test_summary_requires_workflow():
    with pytest.raises(ValueError):
        TechnicianCaseSummary(None)


def test_summary_exposes_workflow(
    summary,
    workflow,
):
    assert summary.workflow is workflow


def test_summary_exposes_case_identity(
    summary,
    workflow,
):
    assert summary.case_id == workflow.case.case_id


def test_summary_exposes_workflow_id(
    summary,
    workflow,
):
    assert summary.workflow_id == workflow.workflow_id


def test_summary_exposes_current_state(
    summary,
    workflow,
):
    assert summary.workflow_state is WorkflowState.OPEN


def test_summary_reports_terminal_state(
    summary,
    workflow,
):
    assert summary.is_terminal is False

    workflow.escalate()

    assert summary.is_terminal is True


def test_summary_exposes_findings(
    summary,
):
    assert summary.findings == ["finding-1"]


def test_summary_exposes_root_causes(
    summary,
):
    assert summary.root_causes == ["cause-1"]


def test_summary_exposes_recommendations(
    summary,
    workflow,
    recommendation,
):
    workflow.case.recommendations.append(recommendation)

    assert summary.recommendations == [recommendation]


def test_summary_exposes_decision(
    summary,
    workflow,
    recommendation,
):
    decision = TechnicianDecision(
        workflow,
        recommendation,
        TechnicianDecisionType.ACCEPT,
        notes="Proceed with remediation.",
    )

    summary.set_decision(decision)

    assert summary.decision is decision


def test_summary_exposes_notes(
    summary,
    workflow,
):
    notes = TechnicianCaseNotes(workflow)
    note = notes.add_note("Initial investigation completed.")

    summary.set_notes(notes)

    assert summary.notes == [note]


def test_summary_exposes_workflow_history(
    summary,
    workflow,
):
    workflow.start_investigation()
    workflow.mark_diagnosed()

    assert summary.workflow_history == workflow.history


def test_summary_collections_are_read_only(
    summary,
    workflow,
):
    findings = summary.findings
    findings.clear()

    assert summary.findings == ["finding-1"]


def test_summary_does_not_mutate_case(
    summary,
    workflow,
):
    original_findings = list(workflow.case.findings)
    original_root_causes = list(workflow.case.root_causes)

    _ = summary.findings
    _ = summary.root_causes

    assert workflow.case.findings == original_findings
    assert workflow.case.root_causes == original_root_causes


def test_summary_reflects_workflow_state_changes(
    summary,
    workflow,
):
    assert summary.workflow_state is WorkflowState.OPEN

    workflow.start_investigation()

    assert summary.workflow_state is WorkflowState.INVESTIGATING


def test_summary_can_expose_remediation_status(
    summary,
):
    summary.set_remediation_status("EXECUTED")

    assert summary.remediation_status == "EXECUTED"


def test_summary_can_expose_verification_status(
    summary,
):
    summary.set_verification_status(True)

    assert summary.verification_status is True


def test_summary_can_expose_escalation_status(
    summary,
):
    summary.set_escalation_status("ESCALATED")

    assert summary.escalation_status == "ESCALATED"