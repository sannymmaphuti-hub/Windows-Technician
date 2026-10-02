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
    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()


def complete_reopened_lifecycle(workflow):
    workflow.reopen()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()


def cycle_numbers(history):
    return [cycle.cycle_number for cycle in history.cycles]


def test_repeated_reads_return_same_recovery_sequence():
    workflow = build_workflow()
    history = build_history(workflow)

    record_cycle(workflow, history, 1)
    record_cycle(workflow, history, 2)

    first_read = cycle_numbers(history)
    second_read = cycle_numbers(history)
    third_read = cycle_numbers(history)

    assert first_read == [0, 1, 2]
    assert second_read == first_read
    assert third_read == first_read


def test_snapshot_remains_stable_when_no_new_cycle_is_recorded():
    workflow = build_workflow()
    history = build_history(workflow)

    record_cycle(workflow, history, 1)

    snapshot = list(history.cycles)

    complete_lifecycle(workflow)

    assert list(history.cycles) == snapshot
    assert history.cycles[0] is snapshot[0]
    assert history.cycles[1] is snapshot[1]


def test_new_cycle_changes_read_result_only_after_explicit_recording():
    workflow = build_workflow()
    history = build_history(workflow)

    first_cycle = record_cycle(workflow, history, 1)

    before_recording = list(history.cycles)

    complete_lifecycle(workflow)

    assert list(history.cycles) == before_recording

    second_cycle = record_cycle(workflow, history, 2)

    after_recording = list(history.cycles)

    assert after_recording[:2] == before_recording
    assert after_recording[2] is second_cycle
    assert history.cycles[1] is first_cycle


def test_old_snapshot_objects_remain_identical_after_new_cycle():
    workflow = build_workflow()
    history = build_history(workflow)

    first_cycle = record_cycle(workflow, history, 1)
    second_cycle = record_cycle(workflow, history, 2)

    snapshot = list(history.cycles)

    third_cycle = record_cycle(workflow, history, 3)

    assert snapshot[0] is history.cycles[0]
    assert snapshot[1] is first_cycle
    assert snapshot[2] is second_cycle
    assert history.cycles[3] is third_cycle


def test_workflow_reopening_does_not_change_recovery_read_sequence():
    workflow = build_workflow()
    history = build_history(workflow)

    first_cycle = record_cycle(workflow, history, 1)

    complete_lifecycle(workflow)

    before_reopen = cycle_numbers(history)

    workflow.reopen()

    after_reopen = cycle_numbers(history)

    assert before_reopen == [0, 1]
    assert after_reopen == before_reopen
    assert history.cycles[1] is first_cycle


def test_repeated_lifecycle_activity_does_not_change_existing_snapshot():
    workflow = build_workflow()
    history = build_history(workflow)

    first_cycle = record_cycle(workflow, history, 1)
    second_cycle = record_cycle(workflow, history, 2)

    snapshot = list(history.cycles)

    complete_lifecycle(workflow)
    complete_reopened_lifecycle(workflow)
    complete_reopened_lifecycle(workflow)

    assert list(history.cycles) == snapshot
    assert history.cycles[1] is first_cycle
    assert history.cycles[2] is second_cycle


def test_read_consistency_is_preserved_across_multiple_new_cycles():
    workflow = build_workflow()
    history = build_history(workflow)

    first_cycle = record_cycle(workflow, history, 1)

    snapshot_one = list(history.cycles)

    complete_lifecycle(workflow)

    second_cycle = record_cycle(workflow, history, 2)

    snapshot_two = list(history.cycles)

    complete_reopened_lifecycle(workflow)

    third_cycle = record_cycle(workflow, history, 3)

    snapshot_three = list(history.cycles)

    assert snapshot_one == [snapshot_one[0], first_cycle]
    assert snapshot_two == [snapshot_two[0], first_cycle, second_cycle]
    assert snapshot_three == [
        snapshot_three[0],
        first_cycle,
        second_cycle,
        third_cycle,
    ]

    assert snapshot_one[1] is first_cycle
    assert snapshot_two[1] is first_cycle
    assert snapshot_two[2] is second_cycle
    assert snapshot_three[1] is first_cycle
    assert snapshot_three[2] is second_cycle
    assert snapshot_three[3] is third_cycle


def test_recovery_history_reads_remain_separate_from_workflow_history_reads():
    workflow = build_workflow()
    history = build_history(workflow)

    first_cycle = record_cycle(workflow, history, 1)

    workflow.start_investigation()

    recovery_snapshot = list(history.cycles)
    workflow_snapshot = list(workflow.history)

    assert recovery_snapshot[1] is first_cycle
    assert first_cycle not in workflow_snapshot

    workflow.mark_diagnosed()
    workflow.require_action()

    assert list(history.cycles) == recovery_snapshot


def test_reading_history_does_not_create_or_duplicate_cycles():
    workflow = build_workflow()
    history = build_history(workflow)

    first_cycle = record_cycle(workflow, history, 1)

    for _ in range(5):
        _ = history.cycles
        _ = list(history.cycles)
        _ = cycle_numbers(history)

    assert len(history.cycles) == 2
    assert history.cycles[1] is first_cycle
    assert cycle_numbers(history) == [0, 1]


def test_final_history_read_reflects_all_explicitly_recorded_cycles_in_order():
    workflow = build_workflow()
    history = build_history(workflow)

    first_cycle = record_cycle(workflow, history, 1)

    complete_lifecycle(workflow)

    second_cycle = record_cycle(workflow, history, 2)

    complete_reopened_lifecycle(workflow)

    third_cycle = record_cycle(workflow, history, 3)

    final_read = list(history.cycles)

    assert len(final_read) == 4
    assert final_read[0].cycle_number == 0
    assert final_read[1] is first_cycle
    assert final_read[2] is second_cycle
    assert final_read[3] is third_cycle
    assert [cycle.cycle_number for cycle in final_read] == [0, 1, 2, 3]