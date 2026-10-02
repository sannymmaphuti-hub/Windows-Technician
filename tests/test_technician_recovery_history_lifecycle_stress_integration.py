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


def complete_lifecycle(workflow):
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()


def complete_reopened_lifecycle(workflow):
    workflow.reopen()
    complete_lifecycle(workflow)


def test_history_survives_multiple_complete_lifecycles():
    workflow = build_workflow()
    history = build_history(workflow)

    cycles = [
        record_cycle(workflow, history, 1),
        record_cycle(workflow, history, 2),
        record_cycle(workflow, history, 3),
    ]

    workflow.start_investigation()
    complete_lifecycle(workflow)
    complete_reopened_lifecycle(workflow)
    complete_reopened_lifecycle(workflow)

    assert history.cycles[0].cycle_number == 0
    assert history.cycles[1] is cycles[0]
    assert history.cycles[2] is cycles[1]
    assert history.cycles[3] is cycles[2]
    assert [cycle.cycle_number for cycle in history.cycles] == [0, 1, 2, 3]


def test_history_survives_repeated_reopen_and_resolve_sequences():
    workflow = build_workflow()
    history = build_history(workflow)

    cycle = record_cycle(workflow, history, 1)

    workflow.start_investigation()
    complete_lifecycle(workflow)

    for _ in range(5):
        complete_reopened_lifecycle(workflow)

    assert len(history.cycles) == 2
    assert history.cycles[1] is cycle
    assert history.cycles[1].cycle_number == 1


def test_history_remains_separate_from_large_workflow_history():
    workflow = build_workflow()
    history = build_history(workflow)

    cycle = record_cycle(workflow, history, 1)

    workflow.start_investigation()
    complete_lifecycle(workflow)

    for _ in range(4):
        complete_reopened_lifecycle(workflow)

    assert history.cycles[1] is cycle
    assert len(history.cycles) == 2
    assert len(workflow.history) > len(history.cycles)


def test_explicit_recovery_records_are_the_only_source_of_new_cycles():
    workflow = build_workflow()
    history = build_history(workflow)

    workflow.start_investigation()
    complete_lifecycle(workflow)

    assert len(history.cycles) == 1

    workflow.reopen()
    assert len(history.cycles) == 1

    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()

    assert len(history.cycles) == 1

    workflow.resolve()

    assert len(history.cycles) == 1


def test_multiple_records_remain_ordered_after_long_lifecycle_activity():
    workflow = build_workflow()
    history = build_history(workflow)

    cycles = []

    workflow.start_investigation()
    complete_lifecycle(workflow)

    cycles.append(record_cycle(workflow, history, 1))

    for _ in range(3):
        complete_reopened_lifecycle(workflow)

    cycles.append(record_cycle(workflow, history, 2))

    for _ in range(3):
        complete_reopened_lifecycle(workflow)

    cycles.append(record_cycle(workflow, history, 3))

    assert [cycle.cycle_number for cycle in history.cycles] == [0, 1, 2, 3]
    assert history.cycles[1] is cycles[0]
    assert history.cycles[2] is cycles[1]
    assert history.cycles[3] is cycles[2]


def test_old_cycle_objects_remain_identical_after_long_activity():
    workflow = build_workflow()
    history = build_history(workflow)

    first = record_cycle(workflow, history, 1)

    workflow.start_investigation()
    complete_lifecycle(workflow)

    second = record_cycle(workflow, history, 2)

    for _ in range(5):
        complete_reopened_lifecycle(workflow)

    assert history.cycles[1] is first
    assert history.cycles[2] is second
    assert first.cycle_number == 1
    assert second.cycle_number == 2


def test_history_survives_escalation_after_previous_lifecycle_activity():
    workflow = build_workflow()
    history = build_history(workflow)

    first = record_cycle(workflow, history, 1)

    workflow.start_investigation()
    complete_lifecycle(workflow)

    second = record_cycle(workflow, history, 2)

    workflow.reopen()
    workflow.escalate()

    assert history.cycles[1] is first
    assert history.cycles[2] is second
    assert [cycle.cycle_number for cycle in history.cycles] == [0, 1, 2]


def test_terminal_escalation_does_not_modify_existing_history():
    workflow = build_workflow()
    history = build_history(workflow)

    first = record_cycle(workflow, history, 1)
    second = record_cycle(workflow, history, 2)

    workflow.escalate()

    snapshot = list(history.cycles)

    with pytest.raises(ValueError):
        workflow.resolve()

    with pytest.raises(ValueError):
        workflow.start_investigation()

    assert list(history.cycles) == snapshot
    assert history.cycles[1] is first
    assert history.cycles[2] is second


def test_long_sequence_preserves_workflow_identity_for_all_cycles():
    workflow = build_workflow()
    history = build_history(workflow)

    cycles = [
        record_cycle(workflow, history, 1),
        record_cycle(workflow, history, 2),
        record_cycle(workflow, history, 3),
        record_cycle(workflow, history, 4),
        record_cycle(workflow, history, 5),
    ]

    workflow.start_investigation()
    complete_lifecycle(workflow)

    for _ in range(3):
        complete_reopened_lifecycle(workflow)

    assert all(cycle.workflow is workflow for cycle in cycles)


def test_final_history_snapshot_contains_every_explicit_recovery_record():
    workflow = build_workflow()
    history = build_history(workflow)

    workflow.start_investigation()
    complete_lifecycle(workflow)

    expected = []

    for cycle_number in range(1, 11):
        expected.append(record_cycle(workflow, history, cycle_number))

        if cycle_number < 10:
            complete_reopened_lifecycle(workflow)

    final_snapshot = list(history.cycles)

    assert len(final_snapshot) == 11
    assert final_snapshot[0].cycle_number == 0

    for index, expected_cycle in enumerate(expected, start=1):
        assert final_snapshot[index] is expected_cycle

    assert [cycle.cycle_number for cycle in final_snapshot] == list(range(11))