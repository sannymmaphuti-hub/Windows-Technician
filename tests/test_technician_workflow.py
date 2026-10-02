import pytest

from engine.diagnostic_case import DiagnosticCase
from engine.technician_workflow import (
    TechnicianWorkflow,
    WorkflowState,
)


def test_workflow_starts_open():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)

    assert workflow.state == WorkflowState.OPEN
    assert workflow.case is case


def test_workflow_supports_valid_investigation_path():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    assert workflow.state == WorkflowState.RESOLVED


def test_workflow_supports_escalation():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)

    workflow.start_investigation()
    workflow.escalate()

    assert workflow.state == WorkflowState.ESCALATED


@pytest.mark.parametrize(
    "operation",
    [
        "mark_diagnosed",
        "require_action",
        "start_remediation",
        "start_verification",
        "resolve",
    ],
)
def test_invalid_workflow_transitions_are_rejected(operation):
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)

    with pytest.raises(ValueError):
        getattr(workflow, operation)()


def test_terminal_states_reject_further_transitions():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)

    workflow.start_investigation()
    workflow.escalate()

    with pytest.raises(ValueError):
        workflow.start_investigation()


def test_resolved_workflow_is_terminal():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    with pytest.raises(ValueError):
        workflow.start_investigation()


def test_workflow_records_transition_history():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()

    assert workflow.history == [
        (WorkflowState.OPEN, WorkflowState.INVESTIGATING),
        (WorkflowState.INVESTIGATING, WorkflowState.DIAGNOSED),
        (WorkflowState.DIAGNOSED, WorkflowState.ACTION_REQUIRED),
    ]


def test_workflow_does_not_mutate_diagnostic_case():
    case = DiagnosticCase()

    original_state = case.lifecycle_state
    original_findings = list(case.findings)
    original_recommendations = list(case.recommendations)

    workflow = TechnicianWorkflow(case)
    workflow.start_investigation()
    workflow.mark_diagnosed()

    assert case.lifecycle_state == original_state
    assert case.findings == original_findings
    assert case.recommendations == original_recommendations