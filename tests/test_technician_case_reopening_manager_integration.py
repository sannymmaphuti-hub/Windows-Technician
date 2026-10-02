import pytest

from engine.technician_case_reopening import (
    TechnicianCaseReopening,
)
from engine.technician_case_reopening_lifecycle import (
    ReopeningState,
    TechnicianCaseReopeningLifecycle,
)
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
def manager(resolved_workflow):
    return TechnicianCaseReopeningManager(
        resolved_workflow
    )


@pytest.fixture
def reopening(manager):
    return manager.request_reopening(
        "tech-001",
        "New evidence received.",
    )


def test_manager_creates_reopening_lifecycle(
    manager,
    reopening,
):
    lifecycle = manager.create_lifecycle(reopening)

    assert isinstance(
        lifecycle,
        TechnicianCaseReopeningLifecycle,
    )

    assert lifecycle.reopening is reopening
    assert lifecycle.state is ReopeningState.PENDING


def test_manager_rejects_non_reopening_lifecycle_input(
    manager,
):
    with pytest.raises(ValueError):
        manager.create_lifecycle(None)


def test_manager_rejects_reopening_from_different_workflow(
    manager,
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
        manager.create_lifecycle(reopening)


def test_manager_accepts_reopening_through_lifecycle(
    manager,
    reopening,
):
    lifecycle = manager.create_lifecycle(reopening)

    manager.accept_reopening(lifecycle)

    assert lifecycle.state is ReopeningState.ACCEPTED
    assert manager.workflow.state is WorkflowState.INVESTIGATING


def test_manager_rejects_reopening_through_lifecycle(
    manager,
    reopening,
):
    lifecycle = manager.create_lifecycle(reopening)

    manager.reject_reopening(lifecycle)

    assert lifecycle.state is ReopeningState.REJECTED
    assert manager.workflow.state is WorkflowState.RESOLVED


def test_manager_completes_accepted_reopening(
    manager,
    reopening,
):
    lifecycle = manager.create_lifecycle(reopening)

    manager.accept_reopening(lifecycle)
    manager.complete_reopening(lifecycle)

    assert lifecycle.state is ReopeningState.COMPLETED


def test_manager_cannot_complete_pending_reopening(
    manager,
    reopening,
):
    lifecycle = manager.create_lifecycle(reopening)

    with pytest.raises(ValueError):
        manager.complete_reopening(lifecycle)


def test_manager_cannot_accept_rejected_reopening(
    manager,
    reopening,
):
    lifecycle = manager.create_lifecycle(reopening)

    manager.reject_reopening(lifecycle)

    with pytest.raises(ValueError):
        manager.accept_reopening(lifecycle)


def test_manager_cannot_reject_accepted_reopening(
    manager,
    reopening,
):
    lifecycle = manager.create_lifecycle(reopening)

    manager.accept_reopening(lifecycle)

    with pytest.raises(ValueError):
        manager.reject_reopening(lifecycle)


def test_manager_cannot_complete_rejected_reopening(
    manager,
    reopening,
):
    lifecycle = manager.create_lifecycle(reopening)

    manager.reject_reopening(lifecycle)

    with pytest.raises(ValueError):
        manager.complete_reopening(lifecycle)


def test_manager_rejects_unmanaged_reopening_lifecycle(
    manager,
    resolved_workflow,
):
    reopening = TechnicianCaseReopening(
        resolved_workflow,
        "tech-002",
        "Unmanaged reopening.",
    )

    lifecycle = TechnicianCaseReopeningLifecycle(
        reopening
    )

    with pytest.raises(ValueError):
        manager.accept_reopening(lifecycle)


def test_manager_preserves_reopening_records(
    manager,
):
    first = manager.request_reopening(
        "tech-001",
        "First reopening.",
    )

    second_manager = TechnicianCaseReopeningManager(
        manager.workflow
    )

    second = second_manager.request_reopening(
        "tech-002",
        "Second reopening.",
    )

    assert manager.reopenings == [first]
    assert second_manager.reopenings == [second]


def test_lifecycle_operations_do_not_create_duplicate_reopenings(
    manager,
    reopening,
):
    lifecycle = manager.create_lifecycle(reopening)

    manager.accept_reopening(lifecycle)

    assert manager.reopenings == [reopening]


def test_manager_exposes_lifecycle_for_managed_reopening(
    manager,
    reopening,
):
    lifecycle = manager.create_lifecycle(reopening)

    assert lifecycle.reopening is manager.latest_reopening