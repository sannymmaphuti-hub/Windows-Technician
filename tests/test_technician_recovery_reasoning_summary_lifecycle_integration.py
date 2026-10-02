from engine.diagnostic_case import DiagnosticCase
from engine.technician_case_summary import TechnicianCaseSummary
from engine.technician_recovery_cycle import TechnicianRecoveryCycle
from engine.technician_recovery_cycle_history import (
    TechnicianRecoveryCycleHistory,
)
from engine.technician_reasoning_summary import TechnicianReasoningSummary
from engine.technician_workflow import TechnicianWorkflow


def build_workflow():
    return TechnicianWorkflow(DiagnosticCase())


def build_reasoning_summary(workflow, history):
    summary = TechnicianCaseSummary(workflow)
    reasoning_summary = TechnicianReasoningSummary(workflow, history)
    summary.set_reasoning_summary(reasoning_summary)
    return summary, reasoning_summary


def record_recovery_cycle(history, workflow):
    cycle = TechnicianRecoveryCycle(
        workflow,
        cycle_number=history.cycle_count,
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


def continue_reinvestigation(workflow):
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()


def test_reasoning_summary_exposes_recovery_history():
    workflow = build_workflow()
    history = TechnicianRecoveryCycleHistory(workflow)

    cycle = record_recovery_cycle(history, workflow)

    summary, reasoning_summary = build_reasoning_summary(
        workflow,
        history,
    )

    assert summary.workflow is workflow
    assert summary.reasoning_summary is reasoning_summary
    assert reasoning_summary.workflow is workflow
    assert reasoning_summary.cycle_history is history
    assert reasoning_summary.cycle_history.cycles[-1] is cycle


def test_reasoning_summary_preserves_recovery_history_through_lifecycle():
    workflow = build_workflow()
    history = TechnicianRecoveryCycleHistory(workflow)

    cycle = record_recovery_cycle(history, workflow)

    _, reasoning_summary = build_reasoning_summary(
        workflow,
        history,
    )

    complete_lifecycle(workflow)

    assert workflow.is_terminal
    assert reasoning_summary.cycle_history is history
    assert reasoning_summary.cycle_history.cycles[-1] is cycle


def test_recovery_record_after_summary_creation_is_visible():
    workflow = build_workflow()
    history = TechnicianRecoveryCycleHistory(workflow)

    _, reasoning_summary = build_reasoning_summary(
        workflow,
        history,
    )

    first_cycle = record_recovery_cycle(history, workflow)
    second_cycle = record_recovery_cycle(history, workflow)

    assert reasoning_summary.cycle_history is history
    assert reasoning_summary.cycle_history.cycles[-2:] == [
        first_cycle,
        second_cycle,
    ]


def test_reopen_preserves_reasoning_summary_recovery_history():
    workflow = build_workflow()
    history = TechnicianRecoveryCycleHistory(workflow)

    first_cycle = record_recovery_cycle(history, workflow)

    _, reasoning_summary = build_reasoning_summary(
        workflow,
        history,
    )

    complete_lifecycle(workflow)
    workflow.reopen()

    assert workflow.state.name == "INVESTIGATING"
    assert reasoning_summary.cycle_history is history
    assert reasoning_summary.cycle_history.cycles[-1] is first_cycle


def test_reinvestigation_adds_recovery_cycle_to_existing_reasoning_summary():
    workflow = build_workflow()
    history = TechnicianRecoveryCycleHistory(workflow)

    first_cycle = record_recovery_cycle(history, workflow)

    _, reasoning_summary = build_reasoning_summary(
        workflow,
        history,
    )

    complete_lifecycle(workflow)

    workflow.reopen()

    second_cycle = record_recovery_cycle(history, workflow)

    continue_reinvestigation(workflow)

    assert reasoning_summary.cycle_history is history
    assert reasoning_summary.cycle_history.cycles[-2:] == [
        first_cycle,
        second_cycle,
    ]
    assert workflow.is_terminal


def test_escalation_preserves_reasoning_summary_recovery_history():
    workflow = build_workflow()
    history = TechnicianRecoveryCycleHistory(workflow)

    workflow.start_investigation()

    cycle = record_recovery_cycle(history, workflow)

    _, reasoning_summary = build_reasoning_summary(
        workflow,
        history,
    )

    workflow.escalate()

    assert workflow.state.name == "ESCALATED"
    assert reasoning_summary.cycle_history is history
    assert reasoning_summary.cycle_history.cycles[-1] is cycle


def test_failed_workflow_operation_does_not_corrupt_reasoning_summary():
    workflow = build_workflow()
    history = TechnicianRecoveryCycleHistory(workflow)

    cycle = record_recovery_cycle(history, workflow)

    _, reasoning_summary = build_reasoning_summary(
        workflow,
        history,
    )

    try:
        workflow.resolve()
    except ValueError:
        pass

    assert workflow.state.name == "OPEN"
    assert reasoning_summary.cycle_history is history
    assert reasoning_summary.cycle_history.cycles[-1] is cycle


def test_multiple_recovery_cycles_remain_ordered_in_reasoning_summary():
    workflow = build_workflow()
    history = TechnicianRecoveryCycleHistory(workflow)

    _, reasoning_summary = build_reasoning_summary(
        workflow,
        history,
    )

    cycles = [
        record_recovery_cycle(history, workflow)
        for _ in range(5)
    ]

    assert reasoning_summary.cycle_history.cycles[-5:] == cycles
    assert [
        cycle.cycle_number
        for cycle in reasoning_summary.cycle_history.cycles
    ] == [0, 1, 2, 3, 4, 5]


def test_reasoning_summary_does_not_convert_recovery_cycles_into_diagnostics():
    workflow = build_workflow()
    history = TechnicianRecoveryCycleHistory(workflow)

    record_recovery_cycle(history, workflow)

    _, reasoning_summary = build_reasoning_summary(
        workflow,
        history,
    )

    assert reasoning_summary.cycle_history is history
    assert workflow.case.findings == []
    assert workflow.case.root_causes == []
    assert workflow.case.recommendations == []
    assert workflow.case.correlations == []


def test_reasoning_summary_recovery_history_remains_separate_from_workflow_history():
    workflow = build_workflow()
    history = TechnicianRecoveryCycleHistory(workflow)

    workflow.start_investigation()

    cycle = record_recovery_cycle(history, workflow)

    _, reasoning_summary = build_reasoning_summary(
        workflow,
        history,
    )

    workflow.mark_diagnosed()

    assert len(workflow.history) == 2
    assert reasoning_summary.cycle_history is history
    assert len(reasoning_summary.cycle_history.cycles) == 2
    assert cycle not in workflow.history


def test_repeated_reasoning_summary_reads_do_not_create_recovery_cycles():
    workflow = build_workflow()
    history = TechnicianRecoveryCycleHistory(workflow)

    cycle = record_recovery_cycle(history, workflow)

    _, reasoning_summary = build_reasoning_summary(
        workflow,
        history,
    )

    initial_cycles = reasoning_summary.cycle_history.cycles

    for _ in range(5):
        assert reasoning_summary.cycle_history is history
        assert reasoning_summary.cycle_history.cycles == initial_cycles

    assert len(reasoning_summary.cycle_history.cycles) == 2
    assert reasoning_summary.cycle_history.cycles[-1] is cycle


def test_long_recovery_sequence_remains_visible_through_reasoning_summary():
    workflow = build_workflow()
    history = TechnicianRecoveryCycleHistory(workflow)

    _, reasoning_summary = build_reasoning_summary(
        workflow,
        history,
    )

    cycles = [
        record_recovery_cycle(history, workflow)
        for _ in range(10)
    ]

    assert len(reasoning_summary.cycle_history.cycles) == 11
    assert reasoning_summary.cycle_history.cycles[-10:] == cycles
    assert [
        cycle.cycle_number
        for cycle in reasoning_summary.cycle_history.cycles
    ] == list(range(11))


def test_reasoning_summary_keeps_same_recovery_history_identity_after_lifecycle_activity():
    workflow = build_workflow()
    history = TechnicianRecoveryCycleHistory(workflow)

    _, reasoning_summary = build_reasoning_summary(
        workflow,
        history,
    )

    original_history = reasoning_summary.cycle_history

    record_recovery_cycle(history, workflow)
    complete_lifecycle(workflow)

    assert reasoning_summary.cycle_history is original_history
    assert reasoning_summary.cycle_history is history

    workflow.reopen()
    record_recovery_cycle(history, workflow)
    continue_reinvestigation(workflow)

    assert reasoning_summary.cycle_history is original_history
    assert reasoning_summary.cycle_history is history