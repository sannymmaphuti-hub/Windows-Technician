from engine.diagnostic_case import DiagnosticCase
from engine.technician_recovery_cycle import TechnicianRecoveryCycle
from engine.technician_recovery_cycle_history import TechnicianRecoveryCycleHistory
from engine.technician_workflow import TechnicianWorkflow, WorkflowState


def build_workflow():
    return TechnicianWorkflow(DiagnosticCase())


def build_history(workflow):
    return TechnicianRecoveryCycleHistory(workflow)


def prepare_workflow(workflow):
    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()


def continue_investigation(workflow):
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()


def record_cycle(workflow, history, cycle_number):
    cycle = TechnicianRecoveryCycle(
        workflow,
        cycle_number=cycle_number,
    )
    history.record_cycle(cycle)
    return cycle


def complete_workflow(workflow):
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()


def test_reopening_after_recovery_preserves_recovery_history():
    workflow = build_workflow()
    history = build_history(workflow)

    prepare_workflow(workflow)

    cycle = record_cycle(
        workflow,
        history,
        cycle_number=1,
    )

    workflow.resolve()
    workflow.reopen()

    assert workflow.state == WorkflowState.INVESTIGATING
    assert cycle in history.cycles
    assert history.cycles[-1] is cycle


def test_reopening_after_recovery_does_not_duplicate_cycles():
    workflow = build_workflow()
    history = build_history(workflow)

    prepare_workflow(workflow)

    cycle = record_cycle(
        workflow,
        history,
        cycle_number=1,
    )

    cycles_before = list(history.cycles)

    workflow.resolve()
    workflow.reopen()

    assert history.cycles == cycles_before
    assert history.cycles.count(cycle) == 1


def test_reinvestigation_does_not_modify_previous_recovery_cycle():
    workflow = build_workflow()
    history = build_history(workflow)

    prepare_workflow(workflow)

    first_cycle = record_cycle(
        workflow,
        history,
        cycle_number=1,
    )

    workflow.resolve()
    workflow.reopen()

    assert first_cycle.workflow is workflow
    assert first_cycle.cycle_number == 1
    assert history.cycles[-1] is first_cycle


def test_new_recovery_cycle_after_reinvestigation_is_distinct():
    workflow = build_workflow()
    history = build_history(workflow)

    prepare_workflow(workflow)

    first_cycle = record_cycle(
        workflow,
        history,
        cycle_number=1,
    )

    workflow.resolve()
    workflow.reopen()

    continue_investigation(workflow)

    second_cycle = record_cycle(
        workflow,
        history,
        cycle_number=2,
    )

    assert second_cycle is not first_cycle
    assert second_cycle.cycle_number == 2
    assert history.cycles[-2] is first_cycle
    assert history.cycles[-1] is second_cycle


def test_reinvestigation_preserves_recovery_cycle_order():
    workflow = build_workflow()
    history = build_history(workflow)

    prepare_workflow(workflow)

    first_cycle = record_cycle(
        workflow,
        history,
        cycle_number=1,
    )

    workflow.resolve()
    workflow.reopen()

    continue_investigation(workflow)

    second_cycle = record_cycle(
        workflow,
        history,
        cycle_number=2,
    )

    workflow.resolve()

    assert [cycle.cycle_number for cycle in history.cycles[1:]] == [1, 2]
    assert history.cycles[-2] is first_cycle
    assert history.cycles[-1] is second_cycle


def test_recovery_history_survives_second_resolution_after_reinvestigation():
    workflow = build_workflow()
    history = build_history(workflow)

    prepare_workflow(workflow)

    first_cycle = record_cycle(
        workflow,
        history,
        cycle_number=1,
    )

    workflow.resolve()
    workflow.reopen()

    continue_investigation(workflow)

    second_cycle = record_cycle(
        workflow,
        history,
        cycle_number=2,
    )

    workflow.resolve()

    assert workflow.state == WorkflowState.RESOLVED
    assert first_cycle in history.cycles
    assert second_cycle in history.cycles
    assert history.cycles[-2] is first_cycle
    assert history.cycles[-1] is second_cycle


def test_reinvestigation_workflow_history_is_separate_from_recovery_history():
    workflow = build_workflow()
    history = build_history(workflow)

    prepare_workflow(workflow)

    cycle = record_cycle(
        workflow,
        history,
        cycle_number=1,
    )

    workflow.resolve()
    workflow.reopen()

    workflow_history_after_reopen = list(workflow.history)

    assert cycle not in workflow_history_after_reopen
    assert cycle in history.cycles
    assert workflow.state == WorkflowState.INVESTIGATING


def test_reinvestigation_can_complete_without_changing_old_recovery_cycle():
    workflow = build_workflow()
    history = build_history(workflow)

    prepare_workflow(workflow)

    cycle = record_cycle(
        workflow,
        history,
        cycle_number=1,
    )

    workflow.resolve()
    workflow.reopen()

    complete_workflow(workflow)

    assert workflow.state == WorkflowState.RESOLVED
    assert history.cycles[-1] is cycle
    assert cycle.cycle_number == 1


def test_multiple_reinvestigations_preserve_all_recovery_cycles():
    workflow = build_workflow()
    history = build_history(workflow)

    prepare_workflow(workflow)

    first_cycle = record_cycle(
        workflow,
        history,
        cycle_number=1,
    )

    workflow.resolve()
    workflow.reopen()

    continue_investigation(workflow)

    second_cycle = record_cycle(
        workflow,
        history,
        cycle_number=2,
    )

    workflow.resolve()
    workflow.reopen()

    continue_investigation(workflow)

    third_cycle = record_cycle(
        workflow,
        history,
        cycle_number=3,
    )

    assert [cycle.cycle_number for cycle in history.cycles[1:]] == [1, 2, 3]
    assert history.cycles[-3] is first_cycle
    assert history.cycles[-2] is second_cycle
    assert history.cycles[-1] is third_cycle


def test_recovery_history_remains_attached_to_same_workflow_across_reinvestigation():
    workflow = build_workflow()
    history = build_history(workflow)

    prepare_workflow(workflow)

    first_cycle = record_cycle(
        workflow,
        history,
        cycle_number=1,
    )

    workflow.resolve()
    workflow.reopen()

    continue_investigation(workflow)

    second_cycle = record_cycle(
        workflow,
        history,
        cycle_number=2,
    )

    assert first_cycle.workflow is workflow
    assert second_cycle.workflow is workflow
    assert history.cycles[-2].workflow is workflow
    assert history.cycles[-1].workflow is workflow