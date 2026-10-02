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


def test_initial_recovery_cycle_is_preserved():
    workflow = build_workflow()
    history = build_history(workflow)

    assert len(history.cycles) == 1
    assert history.cycles[0].cycle_number == 0


def test_recording_cycle_does_not_replace_initial_cycle():
    workflow = build_workflow()
    history = build_history(workflow)

    initial_cycle = history.cycles[0]

    recorded_cycle = record_cycle(
        workflow,
        history,
        cycle_number=1,
    )

    assert history.cycles[0] is initial_cycle
    assert history.cycles[0].cycle_number == 0
    assert history.cycles[-1] is recorded_cycle


def test_recording_second_cycle_does_not_mutate_first_cycle():
    workflow = build_workflow()
    history = build_history(workflow)

    first_cycle = record_cycle(
        workflow,
        history,
        cycle_number=1,
    )

    first_cycle_number_before = first_cycle.cycle_number
    first_cycle_workflow_before = first_cycle.workflow

    second_cycle = record_cycle(
        workflow,
        history,
        cycle_number=2,
    )

    assert first_cycle.cycle_number == first_cycle_number_before
    assert first_cycle.workflow is first_cycle_workflow_before
    assert history.cycles[-2] is first_cycle
    assert history.cycles[-1] is second_cycle


def test_recording_multiple_cycles_preserves_all_existing_objects():
    workflow = build_workflow()
    history = build_history(workflow)

    cycles = [
        record_cycle(workflow, history, cycle_number=1),
        record_cycle(workflow, history, cycle_number=2),
        record_cycle(workflow, history, cycle_number=3),
    ]

    assert history.cycles[1] is cycles[0]
    assert history.cycles[2] is cycles[1]
    assert history.cycles[3] is cycles[2]


def test_cycle_numbers_are_preserved_when_history_is_read_repeatedly():
    workflow = build_workflow()
    history = build_history(workflow)

    record_cycle(workflow, history, cycle_number=1)
    record_cycle(workflow, history, cycle_number=2)

    first_read = [cycle.cycle_number for cycle in history.cycles]
    second_read = [cycle.cycle_number for cycle in history.cycles]
    third_read = [cycle.cycle_number for cycle in history.cycles]

    assert first_read == [0, 1, 2]
    assert second_read == first_read
    assert third_read == first_read


def test_repeated_history_access_does_not_create_cycles():
    workflow = build_workflow()
    history = build_history(workflow)

    record_cycle(workflow, history, cycle_number=1)

    count_before = len(history.cycles)

    _ = history.cycles
    _ = history.cycles
    _ = history.cycles

    assert len(history.cycles) == count_before


def test_recovery_cycles_remain_attached_to_same_workflow():
    workflow = build_workflow()
    history = build_history(workflow)

    first_cycle = record_cycle(
        workflow,
        history,
        cycle_number=1,
    )

    second_cycle = record_cycle(
        workflow,
        history,
        cycle_number=2,
    )

    assert first_cycle.workflow is workflow
    assert second_cycle.workflow is workflow
    assert history.cycles[0].workflow is workflow


def test_recording_cycle_does_not_change_workflow_history():
    workflow = build_workflow()
    history = build_history(workflow)

    workflow.start_investigation()

    workflow_history_before = list(workflow.history)

    record_cycle(
        workflow,
        history,
        cycle_number=1,
    )

    assert workflow.history == workflow_history_before


def test_recovery_history_remains_separate_from_workflow_history():
    workflow = build_workflow()
    history = build_history(workflow)

    workflow.start_investigation()

    cycle = record_cycle(
        workflow,
        history,
        cycle_number=1,
    )

    assert cycle not in workflow.history
    assert cycle in history.cycles


def test_existing_recovery_cycles_remain_ordered_after_new_records():
    workflow = build_workflow()
    history = build_history(workflow)

    first_cycle = record_cycle(
        workflow,
        history,
        cycle_number=1,
    )

    second_cycle = record_cycle(
        workflow,
        history,
        cycle_number=2,
    )

    third_cycle = record_cycle(
        workflow,
        history,
        cycle_number=3,
    )

    assert [cycle.cycle_number for cycle in history.cycles] == [0, 1, 2, 3]
    assert history.cycles[1] is first_cycle
    assert history.cycles[2] is second_cycle
    assert history.cycles[3] is third_cycle