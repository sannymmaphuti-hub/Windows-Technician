import pytest

from engine.technician_case_handoff import TechnicianCaseHandoff
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


def create_handoff(workflow, sender, receiver, reason):
    return TechnicianCaseHandoff(
        workflow,
        sender,
        receiver,
        reason,
    )


def test_manager_requires_workflow():
    with pytest.raises(ValueError):
        TechnicianHandoffManager(None)


def test_manager_exposes_workflow(
    manager,
    workflow,
):
    assert manager.workflow is workflow


def test_manager_starts_empty(
    manager,
):
    assert manager.handoffs == []


def test_manager_adds_handoff(
    manager,
    workflow,
):
    handoff = create_handoff(
        workflow,
        "tech-001",
        "tech-002",
        "Further investigation required.",
    )

    returned = manager.add_handoff(handoff)

    assert returned is handoff
    assert manager.handoffs == [handoff]


def test_manager_rejects_non_handoff(
    manager,
):
    with pytest.raises(ValueError):
        manager.add_handoff(None)


def test_manager_preserves_order(
    manager,
    workflow,
):
    first = create_handoff(
        workflow,
        "tech-001",
        "tech-002",
        "Reason one.",
    )

    second = create_handoff(
        workflow,
        "tech-002",
        "tech-003",
        "Reason two.",
    )

    manager.add_handoff(first)
    manager.add_handoff(second)

    assert manager.handoffs == [first, second]


def test_manager_returns_latest_handoff(
    manager,
    workflow,
):
    first = create_handoff(
        workflow,
        "tech-001",
        "tech-002",
        "Reason one.",
    )

    second = create_handoff(
        workflow,
        "tech-002",
        "tech-003",
        "Reason two.",
    )

    manager.add_handoff(first)
    manager.add_handoff(second)

    assert manager.latest_handoff is second


def test_manager_latest_handoff_is_none_when_empty(
    manager,
):
    assert manager.latest_handoff is None


def test_manager_handoffs_are_read_only(
    manager,
    workflow,
):
    handoff = create_handoff(
        workflow,
        "tech-001",
        "tech-002",
        "Further investigation required.",
    )

    manager.add_handoff(handoff)

    handoffs = manager.handoffs
    handoffs.clear()

    assert manager.handoffs == [handoff]


def test_manager_rejects_handoff_from_different_workflow(
    manager,
):
    other_workflow = TechnicianWorkflow(FakeCase())

    handoff = create_handoff(
        other_workflow,
        "tech-001",
        "tech-002",
        "Different workflow.",
    )

    with pytest.raises(ValueError):
        manager.add_handoff(handoff)


def test_manager_does_not_mutate_workflow(
    manager,
    workflow,
):
    original_state = workflow.state
    original_history = workflow.history

    handoff = create_handoff(
        workflow,
        "tech-001",
        "tech-002",
        "Further investigation required.",
    )

    manager.add_handoff(handoff)

    assert workflow.state is original_state
    assert workflow.history == original_history


def test_manager_supports_multiple_handoffs(
    manager,
    workflow,
):
    for index in range(3):
        manager.add_handoff(
            create_handoff(
                workflow,
                f"tech-{index}",
                f"tech-{index + 1}",
                f"Reason {index}.",
            )
        )

    assert len(manager.handoffs) == 3
    assert manager.latest_handoff.to_technician == "tech-3"