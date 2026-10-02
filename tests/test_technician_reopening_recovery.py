import pytest

from engine.diagnostic_case import DiagnosticCase
from engine.technician_case_reopening_manager import (
    TechnicianCaseReopeningManager,
)
from engine.technician_workflow import (
    TechnicianWorkflow,
    WorkflowState,
)


@pytest.fixture
def resolved_workflow():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    return workflow


@pytest.fixture
def manager(resolved_workflow):
    return TechnicianCaseReopeningManager(
        resolved_workflow
    )


@pytest.fixture
def reopening(manager):
    return manager.request_reopening(
        "Technician B",
        "Issue returned after closure.",
    )


def test_reopened_case_returns_to_investigating(
    resolved_workflow,
    manager,
    reopening,
):
    manager.accept_reopening(reopening)

    assert resolved_workflow.state is WorkflowState.INVESTIGATING


def test_reopened_case_can_be_diagnosed_again(
    resolved_workflow,
    manager,
    reopening,
):
    manager.accept_reopening(reopening)

    resolved_workflow.mark_diagnosed()

    assert resolved_workflow.state is WorkflowState.DIAGNOSED


def test_reopened_case_can_require_action_again(
    resolved_workflow,
    manager,
    reopening,
):
    manager.accept_reopening(reopening)

    resolved_workflow.mark_diagnosed()
    resolved_workflow.require_action()

    assert resolved_workflow.state is WorkflowState.ACTION_REQUIRED


def test_reopened_case_can_enter_remediation_again(
    resolved_workflow,
    manager,
    reopening,
):
    manager.accept_reopening(reopening)

    resolved_workflow.mark_diagnosed()
    resolved_workflow.require_action()
    resolved_workflow.start_remediation()

    assert resolved_workflow.state is WorkflowState.REMEDIATING


def test_reopened_case_can_be_verified_again(
    resolved_workflow,
    manager,
    reopening,
):
    manager.accept_reopening(reopening)

    resolved_workflow.mark_diagnosed()
    resolved_workflow.require_action()
    resolved_workflow.start_remediation()
    resolved_workflow.start_verification()

    assert resolved_workflow.state is WorkflowState.VERIFYING


def test_reopened_case_can_be_resolved_again(
    resolved_workflow,
    manager,
    reopening,
):
    manager.accept_reopening(reopening)

    resolved_workflow.mark_diagnosed()
    resolved_workflow.require_action()
    resolved_workflow.start_remediation()
    resolved_workflow.start_verification()
    resolved_workflow.resolve()

    assert resolved_workflow.state is WorkflowState.RESOLVED


def test_recovery_preserves_previous_history(
    resolved_workflow,
    manager,
    reopening,
):
    original_history = resolved_workflow.history

    manager.accept_reopening(reopening)

    assert resolved_workflow.history[:len(original_history)] == (
        original_history
    )

    assert resolved_workflow.history[-1] == (
        WorkflowState.RESOLVED,
        WorkflowState.INVESTIGATING,
    )


def test_recovery_uses_same_workflow_id(
    resolved_workflow,
    manager,
    reopening,
):
    workflow_id = resolved_workflow.workflow_id

    manager.accept_reopening(reopening)

    assert resolved_workflow.workflow_id == workflow_id


def test_recovery_does_not_create_second_workflow(
    resolved_workflow,
    manager,
    reopening,
):
    workflow_id = resolved_workflow.workflow_id

    manager.accept_reopening(reopening)

    assert reopening.workflow is resolved_workflow
    assert reopening.workflow.workflow_id == workflow_id


def test_resolved_recovery_cycle_can_be_repeated(
    resolved_workflow,
    manager,
    reopening,
):
    manager.accept_reopening(reopening)

    resolved_workflow.mark_diagnosed()
    resolved_workflow.require_action()
    resolved_workflow.start_remediation()
    resolved_workflow.start_verification()
    resolved_workflow.resolve()

    assert resolved_workflow.state is WorkflowState.RESOLVED

    second_reopening = manager.request_reopening(
        "Technician C",
        "Issue returned again.",
    )

    manager.accept_reopening(second_reopening)

    assert resolved_workflow.state is WorkflowState.INVESTIGATING
    assert len(manager.reopenings) == 2