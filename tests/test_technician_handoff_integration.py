import pytest

from engine.technician_activity_log import TechnicianActivityLog
from engine.technician_case_handoff import TechnicianCaseHandoff
from engine.technician_handoff_lifecycle import (
    HandoffState,
    TechnicianHandoffLifecycle,
)
from engine.technician_handoff_manager import TechnicianHandoffManager
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
def manager(workflow):
    return TechnicianHandoffManager(workflow)


@pytest.fixture
def activity_log(workflow):
    return TechnicianActivityLog(workflow)


def create_handoff(workflow):
    return TechnicianCaseHandoff(
        workflow,
        "tech-001",
        "tech-002",
        "Further investigation required.",
    )


def test_handoff_can_be_registered_and_managed(
    manager,
    workflow,
):
    handoff = create_handoff(workflow)

    manager.add_handoff(handoff)

    lifecycle = TechnicianHandoffLifecycle(handoff)

    assert manager.latest_handoff is handoff
    assert lifecycle.state is HandoffState.PENDING


def test_accepted_handoff_can_be_completed(
    manager,
    workflow,
):
    handoff = create_handoff(workflow)
    manager.add_handoff(handoff)

    lifecycle = TechnicianHandoffLifecycle(handoff)

    lifecycle.accept()
    lifecycle.complete()

    assert lifecycle.state is HandoffState.COMPLETED
    assert lifecycle.is_terminal is True
    assert manager.latest_handoff is handoff


def test_rejected_handoff_remains_recorded(
    manager,
    workflow,
):
    handoff = create_handoff(workflow)
    manager.add_handoff(handoff)

    lifecycle = TechnicianHandoffLifecycle(handoff)
    lifecycle.reject()

    assert lifecycle.state is HandoffState.REJECTED
    assert manager.handoffs == [handoff]


def test_handoff_can_be_recorded_in_activity_log(
    manager,
    activity_log,
    workflow,
):
    handoff = create_handoff(workflow)
    manager.add_handoff(handoff)

    activity_log.record_note(
        handoff.reason
    )

    assert len(activity_log.entries) == 1
    assert activity_log.entries[0]["type"] == "NOTE"


def test_multiple_handoffs_preserve_history(
    manager,
    workflow,
):
    first = TechnicianCaseHandoff(
        workflow,
        "tech-001",
        "tech-002",
        "Initial escalation.",
    )

    second = TechnicianCaseHandoff(
        workflow,
        "tech-002",
        "tech-003",
        "Requires specialist review.",
    )

    manager.add_handoff(first)
    manager.add_handoff(second)

    assert manager.handoffs == [first, second]
    assert manager.latest_handoff is second


def test_handoff_integration_does_not_change_workflow(
    manager,
    workflow,
):
    original_state = workflow.state
    original_history = workflow.history

    handoff = create_handoff(workflow)
    manager.add_handoff(handoff)

    lifecycle = TechnicianHandoffLifecycle(handoff)
    lifecycle.accept()
    lifecycle.complete()

    assert workflow.state is original_state
    assert workflow.history == original_history


def test_handoff_manager_and_lifecycle_share_same_record(
    manager,
    workflow,
):
    handoff = create_handoff(workflow)
    manager.add_handoff(handoff)

    lifecycle = TechnicianHandoffLifecycle(
        manager.latest_handoff
    )

    assert lifecycle.handoff is handoff


def test_handoff_completion_is_terminal(
    manager,
    workflow,
):
    handoff = create_handoff(workflow)
    manager.add_handoff(handoff)

    lifecycle = TechnicianHandoffLifecycle(handoff)
    lifecycle.accept()
    lifecycle.complete()

    assert lifecycle.is_terminal
    assert manager.latest_handoff is handoff