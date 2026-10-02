import uuid

import pytest

from engine.diagnostic_case import DiagnosticCase
from engine.technician_workflow import TechnicianWorkflow, WorkflowState


def test_workflow_has_unique_workflow_id():
    case = DiagnosticCase()

    workflow_a = TechnicianWorkflow(case)
    workflow_b = TechnicianWorkflow(case)

    assert isinstance(workflow_a.workflow_id, str)
    assert isinstance(workflow_b.workflow_id, str)
    assert uuid.UUID(workflow_a.workflow_id)
    assert uuid.UUID(workflow_b.workflow_id)
    assert workflow_a.workflow_id != workflow_b.workflow_id


def test_workflow_exposes_creation_timestamp():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)

    assert workflow.created_at is not None


def test_workflow_exposes_current_lifecycle_state():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)

    assert workflow.state == WorkflowState.OPEN


def test_workflow_tracks_case_identity():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)

    assert workflow.case is case
    assert workflow.case.case_id == case.case_id


def test_workflow_history_is_read_only_from_external_mutation():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)

    workflow.start_investigation()

    history = workflow.history
    history.clear()

    assert workflow.history == [
        (WorkflowState.OPEN, WorkflowState.INVESTIGATING),
    ]


def test_workflow_can_report_terminal_state():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)

    assert workflow.is_terminal is False

    workflow.start_investigation()
    workflow.escalate()

    assert workflow.is_terminal is True


def test_resolved_workflow_reports_terminal_state():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    assert workflow.is_terminal is True


@pytest.mark.parametrize(
    "terminal_transition",
    ["resolve", "escalate"],
)
def test_terminal_state_cannot_be_reentered(terminal_transition):
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)

    if terminal_transition == "resolve":
        workflow.start_investigation()
        workflow.mark_diagnosed()
        workflow.require_action()
        workflow.start_remediation()
        workflow.start_verification()
        workflow.resolve()
    else:
        workflow.start_investigation()
        workflow.escalate()

    with pytest.raises(ValueError):
        getattr(workflow, terminal_transition)()


def test_workflow_metadata_does_not_change_after_transition():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)

    workflow_id = workflow.workflow_id
    created_at = workflow.created_at

    workflow.start_investigation()
    workflow.mark_diagnosed()

    assert workflow.workflow_id == workflow_id
    assert workflow.created_at == created_at