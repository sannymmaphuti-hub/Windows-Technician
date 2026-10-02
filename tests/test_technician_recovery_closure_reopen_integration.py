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


def record_cycle(workflow, history, cycle_number):
    cycle = TechnicianRecoveryCycle(workflow, cycle_number=cycle_number)
    history.record_cycle(cycle)
    return cycle


def test_recovery_history_survives_resolution():
    workflow = build_workflow()
    history = build_history(workflow)

    prepare_workflow(workflow)

    cycle = record_cycle(
        workflow,
        history,
        cycle_number=1,
    )

    workflow.resolve()

    assert workflow.state == WorkflowState.RESOLVED
    assert cycle in history.cycles
    assert history.cycles[-1] is cycle


def test_resolution_does_not_remove_recovery_history():
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

    assert history.cycles == cycles_before
    assert history.cycles[-1] is cycle


def test_reopening_preserves_recovery_history():
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


def test_reopening_does_not_duplicate_recovery_history():
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


def test_recovery_history_remains_ordered_after_reopen():
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

    second_cycle = record_cycle(
        workflow,
        history,
        cycle_number=2,
    )

    assert [cycle.cycle_number for cycle in history.cycles[1:]] == [1, 2]
    assert history.cycles[-2] is first_cycle
    assert history.cycles[-1] is second_cycle


def test_reopening_does_not_reuse_previous_recovery_cycle():
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

    second_cycle = record_cycle(
        workflow,
        history,
        cycle_number=2,
    )

    assert second_cycle is not first_cycle
    assert second_cycle.cycle_number != first_cycle.cycle_number
    assert history.cycles[-2] is first_cycle
    assert history.cycles[-1] is second_cycle


def test_recovery_cycle_workflow_identity_survives_resolution_and_reopen():
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

    assert cycle.workflow is workflow
    assert history.cycles[-1].workflow is workflow


def test_resolution_does_not_change_recovery_cycle_identity():
    workflow = build_workflow()
    history = build_history(workflow)

    prepare_workflow(workflow)

    cycle = record_cycle(
        workflow,
        history,
        cycle_number=1,
    )

    workflow.resolve()

    assert history.cycles[-1] is cycle


def test_reopening_does_not_change_recovery_cycle_identity():
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

    assert history.cycles[-1] is cycle


def test_multiple_closure_reopen_cycles_preserve_recovery_history():
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

    second_cycle = record_cycle(
        workflow,
        history,
        cycle_number=2,
    )

    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    assert workflow.state == WorkflowState.RESOLVED
    assert [cycle.cycle_number for cycle in history.cycles[1:]] == [1, 2]
    assert history.cycles[-2] is first_cycle
    assert history.cycles[-1] is second_cycle


def test_recovery_history_survives_final_resolution():
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

    second_cycle = record_cycle(
        workflow,
        history,
        cycle_number=2,
    )

    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    assert workflow.state == WorkflowState.RESOLVED
    assert first_cycle in history.cycles
    assert second_cycle in history.cycles
    assert history.cycles[-2] is first_cycle
    assert history.cycles[-1] is second_cycle


def test_recovery_history_does_not_change_workflow_history():
    workflow = build_workflow()
    history = build_history(workflow)

    prepare_workflow(workflow)

    cycle = record_cycle(
        workflow,
        history,
        cycle_number=1,
    )

    workflow_history_before = list(workflow.history)

    workflow.resolve()
    workflow.reopen()

    assert workflow.history != workflow_history_before
    assert history.cycles[0].cycle_number == 0
    assert cycle in history.cycles


def test_recovery_history_remains_separate_from_workflow_history_after_reopen():
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

    assert cycle not in workflow.history
    assert cycle in history.cycles
    assert history.cycles[-1] is cycle