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


def test_first_cycle_remains_independent_when_second_cycle_is_recorded():
    workflow = build_workflow()
    history = build_history(workflow)

    first_cycle = record_cycle(workflow, history, 1)

    second_cycle = record_cycle(workflow, history, 2)

    assert first_cycle is not second_cycle
    assert first_cycle.cycle_number == 1
    assert second_cycle.cycle_number == 2
    assert history.cycles[1] is first_cycle
    assert history.cycles[2] is second_cycle


def test_each_recorded_cycle_is_a_distinct_object():
    workflow = build_workflow()
    history = build_history(workflow)

    first_cycle = record_cycle(workflow, history, 1)
    second_cycle = record_cycle(workflow, history, 2)
    third_cycle = record_cycle(workflow, history, 3)

    assert first_cycle is not second_cycle
    assert first_cycle is not third_cycle
    assert second_cycle is not third_cycle


def test_later_cycle_does_not_change_earlier_cycle_number():
    workflow = build_workflow()
    history = build_history(workflow)

    first_cycle = record_cycle(workflow, history, 1)
    second_cycle = record_cycle(workflow, history, 2)
    third_cycle = record_cycle(workflow, history, 3)

    assert first_cycle.cycle_number == 1
    assert second_cycle.cycle_number == 2
    assert third_cycle.cycle_number == 3


def test_earlier_cycles_remain_in_same_history_positions():
    workflow = build_workflow()
    history = build_history(workflow)

    first_cycle = record_cycle(workflow, history, 1)
    second_cycle = record_cycle(workflow, history, 2)

    assert history.cycles[1] is first_cycle
    assert history.cycles[2] is second_cycle

    third_cycle = record_cycle(workflow, history, 3)

    assert history.cycles[1] is first_cycle
    assert history.cycles[2] is second_cycle
    assert history.cycles[3] is third_cycle


def test_workflow_identity_is_independent_of_cycle_identity():
    workflow = build_workflow()
    history = build_history(workflow)

    first_cycle = record_cycle(workflow, history, 1)
    second_cycle = record_cycle(workflow, history, 2)

    assert first_cycle is not second_cycle
    assert first_cycle.workflow is workflow
    assert second_cycle.workflow is workflow
    assert first_cycle.workflow is second_cycle.workflow


def test_workflow_activity_between_cycles_does_not_merge_cycles():
    workflow = build_workflow()
    history = build_history(workflow)

    first_cycle = record_cycle(workflow, history, 1)

    complete_lifecycle(workflow)

    second_cycle = record_cycle(workflow, history, 2)

    assert first_cycle is not second_cycle
    assert first_cycle.cycle_number == 1
    assert second_cycle.cycle_number == 2
    assert history.cycles[1] is first_cycle
    assert history.cycles[2] is second_cycle


def test_reopened_workflow_does_not_merge_old_and_new_cycles():
    workflow = build_workflow()
    history = build_history(workflow)

    first_cycle = record_cycle(workflow, history, 1)

    complete_lifecycle(workflow)
    workflow.reopen()

    second_cycle = record_cycle(workflow, history, 2)

    assert first_cycle is not second_cycle
    assert first_cycle.cycle_number == 1
    assert second_cycle.cycle_number == 2
    assert first_cycle.workflow is workflow
    assert second_cycle.workflow is workflow


def test_multiple_recovery_cycles_remain_independent_after_repeated_activity():
    workflow = build_workflow()
    history = build_history(workflow)

    first_cycle = record_cycle(workflow, history, 1)

    complete_lifecycle(workflow)

    second_cycle = record_cycle(workflow, history, 2)

    complete_reopened_lifecycle(workflow)

    third_cycle = record_cycle(workflow, history, 3)

    complete_reopened_lifecycle(workflow)

    assert first_cycle is not second_cycle
    assert first_cycle is not third_cycle
    assert second_cycle is not third_cycle

    assert first_cycle.cycle_number == 1
    assert second_cycle.cycle_number == 2
    assert third_cycle.cycle_number == 3

    assert history.cycles[1] is first_cycle
    assert history.cycles[2] is second_cycle
    assert history.cycles[3] is third_cycle


def test_recovery_cycles_remain_separate_from_workflow_history():
    workflow = build_workflow()
    history = build_history(workflow)

    first_cycle = record_cycle(workflow, history, 1)

    complete_lifecycle(workflow)

    second_cycle = record_cycle(workflow, history, 2)

    complete_reopened_lifecycle(workflow)

    assert first_cycle not in workflow.history
    assert second_cycle not in workflow.history

    assert first_cycle in history.cycles
    assert second_cycle in history.cycles


def test_history_contains_exact_recorded_cycle_objects_in_order():
    workflow = build_workflow()
    history = build_history(workflow)

    first_cycle = record_cycle(workflow, history, 1)

    complete_lifecycle(workflow)

    second_cycle = record_cycle(workflow, history, 2)

    complete_reopened_lifecycle(workflow)

    third_cycle = record_cycle(workflow, history, 3)

    assert list(history.cycles) == [
        history.cycles[0],
        first_cycle,
        second_cycle,
        third_cycle,
    ]