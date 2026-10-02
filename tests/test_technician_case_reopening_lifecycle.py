import pytest

from engine.technician_case_reopening import (
    TechnicianCaseReopening,
)
from engine.technician_case_reopening_lifecycle import (
    ReopeningState,
    TechnicianCaseReopeningLifecycle,
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
def reopening(resolved_workflow):
    return TechnicianCaseReopening(
        resolved_workflow,
        "tech-001",
        "New evidence received.",
    )


@pytest.fixture
def lifecycle(reopening):
    return TechnicianCaseReopeningLifecycle(reopening)


def test_lifecycle_requires_reopening():
    with pytest.raises(ValueError):
        TechnicianCaseReopeningLifecycle(None)


def test_lifecycle_exposes_reopening(
    lifecycle,
    reopening,
):
    assert lifecycle.reopening is reopening


def test_lifecycle_starts_pending(lifecycle):
    assert lifecycle.state is ReopeningState.PENDING


def test_pending_lifecycle_is_not_terminal(lifecycle):
    assert lifecycle.is_terminal is False


def test_accept_changes_state(lifecycle):
    lifecycle.accept()

    assert lifecycle.state is ReopeningState.ACCEPTED


def test_accepting_reopening_is_not_terminal(lifecycle):
    lifecycle.accept()

    assert lifecycle.is_terminal is False


def test_reject_changes_state(lifecycle):
    lifecycle.reject()

    assert lifecycle.state is ReopeningState.REJECTED


def test_rejected_reopening_is_terminal(lifecycle):
    lifecycle.reject()

    assert lifecycle.is_terminal is True


def test_accepted_reopening_can_complete(lifecycle):
    lifecycle.accept()
    lifecycle.complete()

    assert lifecycle.state is ReopeningState.COMPLETED


def test_completed_reopening_is_terminal(lifecycle):
    lifecycle.accept()
    lifecycle.complete()

    assert lifecycle.is_terminal is True


def test_pending_reopening_cannot_complete(lifecycle):
    with pytest.raises(ValueError):
        lifecycle.complete()


def test_accepted_reopening_cannot_be_accepted_again(lifecycle):
    lifecycle.accept()

    with pytest.raises(ValueError):
        lifecycle.accept()


def test_pending_reopening_cannot_be_rejected_after_acceptance(
    lifecycle,
):
    lifecycle.accept()

    with pytest.raises(ValueError):
        lifecycle.reject()


def test_rejected_reopening_cannot_be_accepted(lifecycle):
    lifecycle.reject()

    with pytest.raises(ValueError):
        lifecycle.accept()


def test_completed_reopening_cannot_be_completed_again(lifecycle):
    lifecycle.accept()
    lifecycle.complete()

    with pytest.raises(ValueError):
        lifecycle.complete()


def test_rejected_reopening_cannot_be_completed(lifecycle):
    lifecycle.reject()

    with pytest.raises(ValueError):
        lifecycle.complete()


def test_reopening_lifecycle_does_not_change_workflow(
    lifecycle,
    resolved_workflow,
):
    original_history = resolved_workflow.history

    lifecycle.accept()

    assert resolved_workflow.state is WorkflowState.RESOLVED
    assert resolved_workflow.history == original_history