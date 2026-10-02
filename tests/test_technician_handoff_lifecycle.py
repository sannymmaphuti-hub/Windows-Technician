import pytest

from engine.technician_case_handoff import TechnicianCaseHandoff
from engine.technician_handoff_lifecycle import (
    HandoffState,
    TechnicianHandoffLifecycle,
)
from engine.technician_workflow import TechnicianWorkflow


class FakeCase:
    case_id = "case-001"
    findings = []
    root_causes = []
    recommendations = []


@pytest.fixture
def workflow():
    return TechnicianWorkflow(FakeCase())


@pytest.fixture
def handoff(workflow):
    return TechnicianCaseHandoff(
        workflow,
        "tech-001",
        "tech-002",
        "Further investigation required.",
    )


@pytest.fixture
def lifecycle(handoff):
    return TechnicianHandoffLifecycle(handoff)


def test_lifecycle_requires_handoff():
    with pytest.raises(ValueError):
        TechnicianHandoffLifecycle(None)


def test_lifecycle_exposes_handoff(
    lifecycle,
    handoff,
):
    assert lifecycle.handoff is handoff


def test_lifecycle_starts_pending(
    lifecycle,
):
    assert lifecycle.state is HandoffState.PENDING


def test_lifecycle_is_not_terminal_when_pending(
    lifecycle,
):
    assert lifecycle.is_terminal is False


def test_lifecycle_accepts_handoff(
    lifecycle,
):
    lifecycle.accept()

    assert lifecycle.state is HandoffState.ACCEPTED
    assert lifecycle.is_terminal is False


def test_lifecycle_completes_accepted_handoff(
    lifecycle,
):
    lifecycle.accept()
    lifecycle.complete()

    assert lifecycle.state is HandoffState.COMPLETED
    assert lifecycle.is_terminal is True


def test_lifecycle_rejects_pending_handoff(
    lifecycle,
):
    lifecycle.reject()

    assert lifecycle.state is HandoffState.REJECTED
    assert lifecycle.is_terminal is True


def test_lifecycle_cannot_complete_pending_handoff(
    lifecycle,
):
    with pytest.raises(ValueError):
        lifecycle.complete()


def test_lifecycle_cannot_accept_twice(
    lifecycle,
):
    lifecycle.accept()

    with pytest.raises(ValueError):
        lifecycle.accept()


def test_lifecycle_cannot_reject_after_accept(
    lifecycle,
):
    lifecycle.accept()

    with pytest.raises(ValueError):
        lifecycle.reject()


def test_lifecycle_cannot_accept_after_rejection(
    lifecycle,
):
    lifecycle.reject()

    with pytest.raises(ValueError):
        lifecycle.accept()


def test_lifecycle_cannot_complete_rejected_handoff(
    lifecycle,
):
    lifecycle.reject()

    with pytest.raises(ValueError):
        lifecycle.complete()


def test_lifecycle_cannot_change_terminal_state(
    lifecycle,
):
    lifecycle.accept()
    lifecycle.complete()

    with pytest.raises(ValueError):
        lifecycle.reject()


def test_lifecycle_does_not_mutate_workflow(
    lifecycle,
    handoff,
):
    original_state = handoff.workflow.state
    original_history = handoff.workflow.history

    lifecycle.accept()
    lifecycle.complete()

    assert handoff.workflow.state is original_state
    assert handoff.workflow.history == original_history