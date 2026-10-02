import pytest

from engine.diagnostic_case import DiagnosticCase
from engine.technician_recovery_cycle import (
    TechnicianRecoveryCycle,
)
from engine.technician_workflow import (
    TechnicianWorkflow,
    WorkflowState,
)


@pytest.fixture
def workflow():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)

    workflow.start_investigation()

    return workflow


def test_history_requires_workflow():
    from engine.technician_recovery_cycle_history import (
        TechnicianRecoveryCycleHistory,
    )

    with pytest.raises(ValueError):
        TechnicianRecoveryCycleHistory(None)


def test_history_starts_with_original_cycle(
    workflow,
):
    from engine.technician_recovery_cycle_history import (
        TechnicianRecoveryCycleHistory,
    )

    history = TechnicianRecoveryCycleHistory(
        workflow
    )

    assert len(history.cycles) == 1
    assert history.cycles[0].cycle_number == 0


def test_original_cycle_uses_same_workflow(
    workflow,
):
    from engine.technician_recovery_cycle_history import (
        TechnicianRecoveryCycleHistory,
    )

    history = TechnicianRecoveryCycleHistory(
        workflow
    )

    assert history.cycles[0].workflow is workflow


def test_record_recovery_cycle(
    workflow,
):
    from engine.technician_recovery_cycle_history import (
        TechnicianRecoveryCycleHistory,
    )

    history = TechnicianRecoveryCycleHistory(
        workflow
    )

    cycle = TechnicianRecoveryCycle(
        workflow,
        cycle_number=1,
    )

    recorded = history.record_cycle(cycle)

    assert recorded is cycle
    assert len(history.cycles) == 2
    assert history.cycles[-1].cycle_number == 1


def test_cycle_must_use_same_workflow(
    workflow,
):
    from engine.technician_recovery_cycle_history import (
        TechnicianRecoveryCycleHistory,
    )

    other_case = DiagnosticCase()
    other_workflow = TechnicianWorkflow(
        other_case
    )

    history = TechnicianRecoveryCycleHistory(
        workflow
    )

    cycle = TechnicianRecoveryCycle(
        other_workflow,
        cycle_number=1,
    )

    with pytest.raises(ValueError):
        history.record_cycle(cycle)


def test_cycle_numbers_must_be_sequential(
    workflow,
):
    from engine.technician_recovery_cycle_history import (
        TechnicianRecoveryCycleHistory,
    )

    history = TechnicianRecoveryCycleHistory(
        workflow
    )

    cycle = TechnicianRecoveryCycle(
        workflow,
        cycle_number=2,
    )

    with pytest.raises(ValueError):
        history.record_cycle(cycle)


def test_duplicate_cycle_cannot_be_recorded(
    workflow,
):
    from engine.technician_recovery_cycle_history import (
        TechnicianRecoveryCycleHistory,
    )

    history = TechnicianRecoveryCycleHistory(
        workflow
    )

    cycle = TechnicianRecoveryCycle(
        workflow,
        cycle_number=1,
    )

    history.record_cycle(cycle)

    with pytest.raises(ValueError):
        history.record_cycle(cycle)


def test_latest_cycle(
    workflow,
):
    from engine.technician_recovery_cycle_history import (
        TechnicianRecoveryCycleHistory,
    )

    history = TechnicianRecoveryCycleHistory(
        workflow
    )

    cycle = TechnicianRecoveryCycle(
        workflow,
        cycle_number=1,
    )

    history.record_cycle(cycle)

    assert history.latest_cycle is cycle


def test_history_is_read_only(
    workflow,
):
    from engine.technician_recovery_cycle_history import (
        TechnicianRecoveryCycleHistory,
    )

    history = TechnicianRecoveryCycleHistory(
        workflow
    )

    cycles = history.cycles

    cycles.clear()

    assert len(history.cycles) == 1


def test_workflow_history_remains_unchanged(
    workflow,
):
    from engine.technician_recovery_cycle_history import (
        TechnicianRecoveryCycleHistory,
    )

    history = TechnicianRecoveryCycleHistory(
        workflow
    )

    original_workflow_history = workflow.history

    cycle = TechnicianRecoveryCycle(
        workflow,
        cycle_number=1,
    )

    history.record_cycle(cycle)

    assert workflow.history == original_workflow_history
    assert workflow.state is WorkflowState.INVESTIGATING