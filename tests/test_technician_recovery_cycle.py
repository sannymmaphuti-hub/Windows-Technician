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


def test_recovery_cycle_requires_workflow():
    from engine.technician_recovery_cycle import (
        TechnicianRecoveryCycle,
    )

    with pytest.raises(ValueError):
        TechnicianRecoveryCycle(None)


def test_first_cycle_is_zero_based(
    resolved_workflow,
):
    from engine.technician_recovery_cycle import (
        TechnicianRecoveryCycle,
    )

    cycle = TechnicianRecoveryCycle(
        resolved_workflow
    )

    assert cycle.cycle_number == 0


def test_cycle_exposes_workflow(
    resolved_workflow,
):
    from engine.technician_recovery_cycle import (
        TechnicianRecoveryCycle,
    )

    cycle = TechnicianRecoveryCycle(
        resolved_workflow
    )

    assert cycle.workflow is resolved_workflow


def test_recovery_creates_next_cycle(
    resolved_workflow,
    manager,
):
    from engine.technician_recovery_cycle import (
        TechnicianRecoveryCycle,
    )

    cycle = TechnicianRecoveryCycle(
        resolved_workflow
    )

    reopening = manager.request_reopening(
        "Technician B",
        "Issue returned.",
    )

    manager.accept_reopening(reopening)

    next_cycle = cycle.start_recovery_cycle()

    assert next_cycle.cycle_number == 1


def test_recovery_cycle_uses_same_workflow(
    resolved_workflow,
    manager,
):
    from engine.technician_recovery_cycle import (
        TechnicianRecoveryCycle,
    )

    cycle = TechnicianRecoveryCycle(
        resolved_workflow
    )

    reopening = manager.request_reopening(
        "Technician B",
        "Issue returned.",
    )

    manager.accept_reopening(reopening)

    next_cycle = cycle.start_recovery_cycle()

    assert next_cycle.workflow is resolved_workflow
    assert (
        next_cycle.workflow.workflow_id
        == resolved_workflow.workflow_id
    )


def test_recovery_cycle_requires_investigating(
    resolved_workflow,
):
    from engine.technician_recovery_cycle import (
        TechnicianRecoveryCycle,
    )

    cycle = TechnicianRecoveryCycle(
        resolved_workflow
    )

    with pytest.raises(ValueError):
        cycle.start_recovery_cycle()


def test_cycle_numbers_increment(
    resolved_workflow,
    manager,
):
    from engine.technician_recovery_cycle import (
        TechnicianRecoveryCycle,
    )

    cycle = TechnicianRecoveryCycle(
        resolved_workflow
    )

    reopening = manager.request_reopening(
        "Technician B",
        "Issue returned.",
    )

    manager.accept_reopening(reopening)

    cycle_one = cycle.start_recovery_cycle()

    assert cycle_one.cycle_number == 1

    resolved_workflow.mark_diagnosed()
    resolved_workflow.require_action()
    resolved_workflow.start_remediation()
    resolved_workflow.start_verification()
    resolved_workflow.resolve()

    second_reopening = manager.request_reopening(
        "Technician C",
        "Issue returned again.",
    )

    manager.accept_reopening(second_reopening)

    cycle_two = cycle_one.start_recovery_cycle()

    assert cycle_two.cycle_number == 2


def test_cycle_is_read_only(
    resolved_workflow,
    manager,
):
    from engine.technician_recovery_cycle import (
        TechnicianRecoveryCycle,
    )

    cycle = TechnicianRecoveryCycle(
        resolved_workflow
    )

    reopening = manager.request_reopening(
        "Technician B",
        "Issue returned.",
    )

    manager.accept_reopening(reopening)

    next_cycle = cycle.start_recovery_cycle()

    assert next_cycle.cycle_number == 1
    assert resolved_workflow.state is (
        WorkflowState.INVESTIGATING
    )