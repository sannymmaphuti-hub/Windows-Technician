from engine.diagnostic_case import DiagnosticCase
from engine.technician_recovery_cycle import TechnicianRecoveryCycle
from engine.technician_recovery_cycle_history import (
    TechnicianRecoveryCycleHistory,
)
from engine.technician_reasoning_summary import TechnicianReasoningSummary
from engine.technician_workflow import TechnicianWorkflow


def build_workflow():
    return TechnicianWorkflow(DiagnosticCase())


def build_history(workflow):
    return TechnicianRecoveryCycleHistory(workflow)


def build_summary(workflow, history):
    return TechnicianReasoningSummary(
        workflow,
        history,
    )


def record_cycle(workflow, history, cycle_number):
    cycle = TechnicianRecoveryCycle(
        workflow,
        cycle_number=cycle_number,
    )
    history.record_cycle(cycle)
    return cycle


def resolve_workflow(workflow):
    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()


def test_recovery_history_survives_investigation_start():
    workflow = build_workflow()
    history = build_history(workflow)

    workflow.start_investigation()

    cycle = record_cycle(workflow, history, 1)

    assert history.latest_cycle is cycle
    assert history.cycle_count == 2
    assert workflow.state.value == "INVESTIGATING"


def test_recovery_history_survives_diagnosis():
    workflow = build_workflow()
    history = build_history(workflow)

    workflow.start_investigation()
    workflow.mark_diagnosed()

    cycle = record_cycle(workflow, history, 1)

    assert history.latest_cycle is cycle
    assert workflow.state.value == "DIAGNOSED"


def test_recovery_history_survives_remediation():
    workflow = build_workflow()
    history = build_history(workflow)

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()

    cycle = record_cycle(workflow, history, 1)

    assert history.latest_cycle is cycle
    assert workflow.state.value == "REMEDIATING"


def test_recovery_history_survives_verification():
    workflow = build_workflow()
    history = build_history(workflow)

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()

    cycle = record_cycle(workflow, history, 1)

    assert history.latest_cycle is cycle
    assert workflow.state.value == "VERIFYING"


def test_recovery_history_survives_resolution():
    workflow = build_workflow()
    history = build_history(workflow)

    resolve_workflow(workflow)

    cycle = record_cycle(workflow, history, 1)

    assert history.latest_cycle is cycle
    assert history.cycle_count == 2
    assert workflow.state.value == "RESOLVED"


def test_recovery_history_survives_reopening():
    workflow = build_workflow()
    history = build_history(workflow)

    resolve_workflow(workflow)

    cycle = record_cycle(workflow, history, 1)

    workflow.reopen()

    assert history.latest_cycle is cycle
    assert history.cycle_count == 2
    assert workflow.state.value == "INVESTIGATING"


def test_recovery_history_remains_ordered_across_reopen():
    workflow = build_workflow()
    history = build_history(workflow)

    resolve_workflow(workflow)

    first = record_cycle(workflow, history, 1)

    workflow.reopen()

    second = record_cycle(workflow, history, 2)

    assert history.cycles[1] is first
    assert history.cycles[2] is second
    assert [
        cycle.cycle_number
        for cycle in history.cycles
    ] == [0, 1, 2]


def test_recovery_history_does_not_change_workflow_history():
    workflow = build_workflow()
    history = build_history(workflow)

    workflow.start_investigation()
    workflow.mark_diagnosed()

    workflow_history_before = list(workflow.history)

    record_cycle(workflow, history, 1)

    assert workflow.history == workflow_history_before


def test_recovery_history_does_not_change_workflow_state():
    workflow = build_workflow()
    history = build_history(workflow)

    workflow.start_investigation()
    workflow.mark_diagnosed()

    state_before = workflow.state

    record_cycle(workflow, history, 1)

    assert workflow.state is state_before


def test_recovery_history_keeps_same_workflow_after_reopen():
    workflow = build_workflow()
    history = build_history(workflow)

    resolve_workflow(workflow)

    record_cycle(workflow, history, 1)

    workflow.reopen()

    assert history.workflow is workflow
    assert history.latest_cycle.workflow is workflow


def test_reasoning_summary_keeps_recovery_history_after_reopen():
    workflow = build_workflow()
    history = build_history(workflow)
    summary = build_summary(workflow, history)

    resolve_workflow(workflow)

    cycle = record_cycle(workflow, history, 1)

    workflow.reopen()

    assert summary.cycle_history is history
    assert summary.cycle_history.latest_cycle is cycle
    assert summary.cycle_history.cycle_count == 2


def test_recovery_history_does_not_replace_reasoning_summary():
    workflow = build_workflow()
    history = build_history(workflow)
    summary = build_summary(workflow, history)

    summary_identity = id(summary)

    record_cycle(workflow, history, 1)

    assert id(summary) == summary_identity
    assert summary.cycle_history is history


def test_multiple_lifecycle_transitions_preserve_all_cycles():
    workflow = build_workflow()
    history = build_history(workflow)

    workflow.start_investigation()
    first = record_cycle(workflow, history, 1)

    workflow.mark_diagnosed()
    second = record_cycle(workflow, history, 2)

    workflow.require_action()
    workflow.start_remediation()
    third = record_cycle(workflow, history, 3)

    workflow.start_verification()
    workflow.resolve()

    assert [
        cycle.cycle_number
        for cycle in history.cycles
    ] == [0, 1, 2, 3]

    assert history.cycles[1] is first
    assert history.cycles[2] is second
    assert history.cycles[3] is third


def test_recovery_history_is_not_added_to_workflow_history():
    workflow = build_workflow()
    history = build_history(workflow)

    workflow.start_investigation()

    workflow_history_before = list(workflow.history)

    cycle = record_cycle(workflow, history, 1)

    assert cycle not in workflow.history
    assert workflow.history == workflow_history_before