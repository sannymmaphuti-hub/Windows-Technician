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


def test_recovery_history_survives_repeated_completed_lifecycles():
    workflow = build_workflow()
    history = build_history(workflow)

    first_cycle = record_cycle(workflow, history, 1)

    complete_lifecycle(workflow)

    second_cycle = record_cycle(workflow, history, 2)

    complete_reopened_lifecycle(workflow)

    assert [cycle.cycle_number for cycle in history.cycles] == [0, 1, 2]
    assert history.cycles[1] is first_cycle
    assert history.cycles[2] is second_cycle


def test_recovery_history_survives_repeated_reopen_operations():
    workflow = build_workflow()
    history = build_history(workflow)

    first_cycle = record_cycle(workflow, history, 1)

    complete_lifecycle(workflow)
    complete_reopened_lifecycle(workflow)

    second_cycle = record_cycle(workflow, history, 2)

    complete_reopened_lifecycle(workflow)

    assert [cycle.cycle_number for cycle in history.cycles] == [0, 1, 2]
    assert history.cycles[1] is first_cycle
    assert history.cycles[2] is second_cycle


def test_workflow_history_can_grow_without_changing_recovery_history():
    workflow = build_workflow()
    history = build_history(workflow)

    first_cycle = record_cycle(workflow, history, 1)

    recovery_snapshot = list(history.cycles)

    complete_lifecycle(workflow)
    complete_reopened_lifecycle(workflow)

    assert list(history.cycles) == recovery_snapshot
    assert history.cycles[1] is first_cycle


def test_repeated_workflow_activity_does_not_duplicate_recovery_cycles():
    workflow = build_workflow()
    history = build_history(workflow)

    first_cycle = record_cycle(workflow, history, 1)

    complete_lifecycle(workflow)
    complete_reopened_lifecycle(workflow)
    complete_reopened_lifecycle(workflow)

    assert len(history.cycles) == 2
    assert history.cycles[1] is first_cycle
    assert [cycle.cycle_number for cycle in history.cycles] == [0, 1]


def test_new_recovery_cycle_is_added_only_when_explicitly_recorded():
    workflow = build_workflow()
    history = build_history(workflow)

    first_cycle = record_cycle(workflow, history, 1)

    complete_lifecycle(workflow)
    complete_reopened_lifecycle(workflow)

    assert len(history.cycles) == 2
    assert history.cycles[1] is first_cycle

    second_cycle = record_cycle(workflow, history, 2)

    assert len(history.cycles) == 3
    assert history.cycles[1] is first_cycle
    assert history.cycles[2] is second_cycle


def test_recovery_cycle_identity_survives_long_workflow_activity():
    workflow = build_workflow()
    history = build_history(workflow)

    cycle = record_cycle(workflow, history, 1)

    complete_lifecycle(workflow)

    for _ in range(3):
        complete_reopened_lifecycle(workflow)

    assert history.cycles[1] is cycle
    assert cycle.workflow is workflow
    assert cycle.cycle_number == 1


def test_recovery_cycles_remain_ordered_when_activity_occurs_between_records():
    workflow = build_workflow()
    history = build_history(workflow)

    first_cycle = record_cycle(workflow, history, 1)

    complete_lifecycle(workflow)

    second_cycle = record_cycle(workflow, history, 2)

    complete_reopened_lifecycle(workflow)

    third_cycle = record_cycle(workflow, history, 3)

    assert [cycle.cycle_number for cycle in history.cycles] == [0, 1, 2, 3]
    assert history.cycles[1] is first_cycle
    assert history.cycles[2] is second_cycle
    assert history.cycles[3] is third_cycle


def test_recovery_history_remains_separate_after_repeated_activity():
    workflow = build_workflow()
    history = build_history(workflow)

    first_cycle = record_cycle(workflow, history, 1)

    complete_lifecycle(workflow)
    complete_reopened_lifecycle(workflow)

    second_cycle = record_cycle(workflow, history, 2)

    assert first_cycle not in workflow.history
    assert second_cycle not in workflow.history
    assert first_cycle in history.cycles
    assert second_cycle in history.cycles


def test_repeated_activity_does_not_rewrite_existing_cycle_numbers():
    workflow = build_workflow()
    history = build_history(workflow)

    first_cycle = record_cycle(workflow, history, 1)
    second_cycle = record_cycle(workflow, history, 2)

    complete_lifecycle(workflow)
    complete_reopened_lifecycle(workflow)

    third_cycle = record_cycle(workflow, history, 3)

    assert first_cycle.cycle_number == 1
    assert second_cycle.cycle_number == 2
    assert third_cycle.cycle_number == 3


def test_recovery_history_remains_stable_after_multiple_records_and_lifecycles():
    workflow = build_workflow()
    history = build_history(workflow)

    first_cycle = record_cycle(workflow, history, 1)

    complete_lifecycle(workflow)

    second_cycle = record_cycle(workflow, history, 2)

    complete_reopened_lifecycle(workflow)

    third_cycle = record_cycle(workflow, history, 3)

    complete_reopened_lifecycle(workflow)

    assert [cycle.cycle_number for cycle in history.cycles] == [0, 1, 2, 3]
    assert history.cycles[1] is first_cycle
    assert history.cycles[2] is second_cycle
    assert history.cycles[3] is third_cycle

    assert first_cycle.workflow is workflow
    assert second_cycle.workflow is workflow
    assert third_cycle.workflow is workflow