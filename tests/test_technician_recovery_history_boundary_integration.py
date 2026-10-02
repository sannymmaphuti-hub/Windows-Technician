import pytest

from engine.diagnostic_case import DiagnosticCase
from engine.technician_recovery_cycle import TechnicianRecoveryCycle
from engine.technician_recovery_cycle_history import TechnicianRecoveryCycleHistory
from engine.technician_workflow import TechnicianWorkflow


def build_workflow():
    return TechnicianWorkflow(DiagnosticCase())


def build_history(workflow):
    return TechnicianRecoveryCycleHistory(workflow)


def record_cycle(workflow, history, cycle_number):
    cycle = TechnicianRecoveryCycle(
        workflow,
        cycle_number=cycle_number,
    )
    history.record_cycle(cycle)
    return cycle


def test_invalid_workflow_transition_does_not_change_recovery_history():
    workflow = build_workflow()
    history = build_history(workflow)

    cycle = record_cycle(workflow, history, 1)
    snapshot = list(history.cycles)

    with pytest.raises(ValueError):
        workflow.mark_diagnosed()

    assert list(history.cycles) == snapshot
    assert history.cycles[1] is cycle
    assert cycle.cycle_number == 1


def test_invalid_second_workflow_transition_does_not_change_recovery_history():
    workflow = build_workflow()
    history = build_history(workflow)

    cycle = record_cycle(workflow, history, 1)

    workflow.start_investigation()
    snapshot = list(history.cycles)

    with pytest.raises(ValueError):
        workflow.start_investigation()

    assert list(history.cycles) == snapshot
    assert history.cycles[1] is cycle


def test_invalid_lifecycle_transition_after_recovery_does_not_corrupt_history():
    workflow = build_workflow()
    history = build_history(workflow)

    cycle = record_cycle(workflow, history, 1)

    workflow.start_investigation()
    workflow.mark_diagnosed()

    snapshot = list(history.cycles)

    with pytest.raises(ValueError):
        workflow.start_investigation()

    assert list(history.cycles) == snapshot
    assert history.cycles[1] is cycle
    assert cycle.workflow is workflow


def test_failed_transition_does_not_create_recovery_cycle():
    workflow = build_workflow()
    history = build_history(workflow)

    record_cycle(workflow, history, 1)

    count_before = len(history.cycles)

    with pytest.raises(ValueError):
        workflow.mark_diagnosed()

    assert len(history.cycles) == count_before
    assert [cycle.cycle_number for cycle in history.cycles] == [0, 1]


def test_failed_transition_between_recorded_cycles_does_not_change_order():
    workflow = build_workflow()
    history = build_history(workflow)

    first_cycle = record_cycle(workflow, history, 1)
    second_cycle = record_cycle(workflow, history, 2)

    workflow.start_investigation()
    snapshot = list(history.cycles)

    with pytest.raises(ValueError):
        workflow.start_investigation()

    assert list(history.cycles) == snapshot
    assert history.cycles[1] is first_cycle
    assert history.cycles[2] is second_cycle
    assert [cycle.cycle_number for cycle in history.cycles] == [0, 1, 2]


def test_failed_transition_does_not_rewrite_existing_cycle_numbers():
    workflow = build_workflow()
    history = build_history(workflow)

    first_cycle = record_cycle(workflow, history, 1)
    second_cycle = record_cycle(workflow, history, 2)

    workflow.start_investigation()

    with pytest.raises(ValueError):
        workflow.start_investigation()

    assert first_cycle.cycle_number == 1
    assert second_cycle.cycle_number == 2


def test_recovery_history_remains_readable_after_failed_transition():
    workflow = build_workflow()
    history = build_history(workflow)

    first_cycle = record_cycle(workflow, history, 1)

    with pytest.raises(ValueError):
        workflow.mark_diagnosed()

    assert history.cycles[0].cycle_number == 0
    assert history.cycles[1] is first_cycle
    assert history.cycles[1].workflow is workflow


def test_valid_recording_still_works_after_failed_transition():
    workflow = build_workflow()
    history = build_history(workflow)

    first_cycle = record_cycle(workflow, history, 1)

    with pytest.raises(ValueError):
        workflow.mark_diagnosed()

    second_cycle = record_cycle(workflow, history, 2)

    assert history.cycles[1] is first_cycle
    assert history.cycles[2] is second_cycle
    assert [cycle.cycle_number for cycle in history.cycles] == [0, 1, 2]


def test_recovery_history_survives_failed_transition_then_reopen():
    workflow = build_workflow()
    history = build_history(workflow)

    first_cycle = record_cycle(workflow, history, 1)

    workflow.start_investigation()

    with pytest.raises(ValueError):
        workflow.start_investigation()

    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    workflow.reopen()

    assert history.cycles[1] is first_cycle
    assert [cycle.cycle_number for cycle in history.cycles] == [0, 1]


def test_recovery_history_remains_stable_after_multiple_failed_operations():
    workflow = build_workflow()
    history = build_history(workflow)

    first_cycle = record_cycle(workflow, history, 1)
    second_cycle = record_cycle(workflow, history, 2)

    snapshot = list(history.cycles)

    with pytest.raises(ValueError):
        workflow.mark_diagnosed()

    with pytest.raises(ValueError):
        workflow.mark_diagnosed()

    assert list(history.cycles) == snapshot
    assert history.cycles[1] is first_cycle
    assert history.cycles[2] is second_cycle
    assert [cycle.cycle_number for cycle in history.cycles] == [0, 1, 2]