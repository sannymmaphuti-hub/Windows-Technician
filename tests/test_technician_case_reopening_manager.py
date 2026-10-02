import pytest

from engine.technician_case_closure import TechnicianCaseClosure
from engine.technician_case_reopening import TechnicianCaseReopening
from engine.technician_case_reopening_manager import (
    TechnicianCaseReopeningManager,
)
from engine.technician_workflow import (
    TechnicianWorkflow,
    WorkflowState,
)


class FakeCase:
    case_id = "case-001"
    findings = []
    root_causes = []
    recommendations = []


@pytest.fixture
def resolved_workflow():
    workflow = TechnicianWorkflow(FakeCase())

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    return workflow


@pytest.fixture
def closure(resolved_workflow):
    return TechnicianCaseClosure(
        resolved_workflow,
        "tech-001",
        "Issue resolved and verified.",
    )


@pytest.fixture
def manager(resolved_workflow):
    return TechnicianCaseReopeningManager(
        resolved_workflow
    )


def test_manager_requires_workflow():
    with pytest.raises(ValueError):
        TechnicianCaseReopeningManager(None)


def test_manager_exposes_workflow(
    manager,
    resolved_workflow,
):
    assert manager.workflow is resolved_workflow


def test_manager_starts_without_reopenings(
    manager,
):
    assert manager.reopenings == []


def test_manager_can_request_reopening(
    manager,
):
    reopening = manager.request_reopening(
        "tech-001",
        "New evidence received.",
    )

    assert isinstance(
        reopening,
        TechnicianCaseReopening,
    )

    assert manager.latest_reopening is reopening
    assert manager.reopenings == [reopening]


def test_requesting_reopening_does_not_change_workflow(
    manager,
    resolved_workflow,
):
    original_history = resolved_workflow.history

    manager.request_reopening(
        "tech-001",
        "New evidence received.",
    )

    assert resolved_workflow.state is WorkflowState.RESOLVED
    assert resolved_workflow.history == original_history


def test_reopening_can_be_accepted(
    manager,
    resolved_workflow,
):
    reopening = manager.request_reopening(
        "tech-001",
        "New evidence received.",
    )

    manager.accept_reopening(reopening)

    assert resolved_workflow.state is WorkflowState.INVESTIGATING


def test_accepting_reopening_records_transition(
    manager,
    resolved_workflow,
):
    reopening = manager.request_reopening(
        "tech-001",
        "New evidence received.",
    )

    manager.accept_reopening(reopening)

    assert resolved_workflow.history[-1] == (
        WorkflowState.RESOLVED,
        WorkflowState.INVESTIGATING,
    )


def test_only_pending_reopening_can_be_accepted(
    manager,
):
    reopening = manager.request_reopening(
        "tech-001",
        "New evidence received.",
    )

    manager.accept_reopening(reopening)

    with pytest.raises(ValueError):
        manager.accept_reopening(reopening)


def test_reopening_must_belong_to_same_workflow(
    manager,
    resolved_workflow,
):
    other_workflow = TechnicianWorkflow(FakeCase())

    other_workflow.start_investigation()
    other_workflow.mark_diagnosed()
    other_workflow.require_action()
    other_workflow.start_remediation()
    other_workflow.start_verification()
    other_workflow.resolve()

    reopening = TechnicianCaseReopening(
        other_workflow,
        "tech-002",
        "New evidence.",
    )

    with pytest.raises(ValueError):
        manager.accept_reopening(reopening)


def test_reopening_history_is_preserved(
    manager,
    closure,
):
    reopening = manager.request_reopening(
        "tech-001",
        "New evidence received.",
        closure=closure,
    )

    assert reopening.closure is closure
    assert manager.latest_reopening is reopening


def test_manager_preserves_multiple_reopenings(
    manager,
):
    first = manager.request_reopening(
        "tech-001",
        "New evidence received.",
    )

    # Return the workflow to RESOLVED for a second request.
    manager.accept_reopening(first)

    manager.workflow._transition_to(
        WorkflowState.DIAGNOSED
    )
    manager.workflow._transition_to(
        WorkflowState.ACTION_REQUIRED
    )
    manager.workflow._transition_to(
        WorkflowState.REMEDIATING
    )
    manager.workflow._transition_to(
        WorkflowState.VERIFYING
    )
    manager.workflow.resolve()

    second = manager.request_reopening(
        "tech-002",
        "Case requires another investigation.",
    )

    assert manager.reopenings == [first, second]
    assert manager.latest_reopening is second