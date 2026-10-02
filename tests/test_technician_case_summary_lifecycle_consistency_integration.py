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


def build_summary(workflow, history):
    summary = TechnicianCaseSummary(workflow)

    reasoning_summary = TechnicianReasoningSummary(
        workflow,
        history,
    )

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


def test_summary_initial_state_matches_workflow():
    workflow = build_workflow()
    history = TechnicianRecoveryCycleHistory(workflow)

    summary, reasoning_summary = build_summary(
        workflow,
        history,
    )

    assert summary.workflow is workflow
    assert summary.case_id == workflow.case.case_id
    assert summary.workflow_id == workflow.workflow_id
    assert summary.workflow_state == workflow.state
    assert summary.is_terminal is False

    assert summary.findings == []
    assert summary.root_causes == []
    assert summary.recommendations == []

    assert summary.workflow_history == workflow.history
    assert summary.reasoning_summary is reasoning_summary
    assert reasoning_summary.cycle_history is history


def test_summary_tracks_initial_lifecycle_progression():
    workflow = build_workflow()
    history = TechnicianRecoveryCycleHistory(workflow)

    summary, _ = build_summary(
        workflow,
        history,
    )

    workflow.start_investigation()

    assert summary.workflow_state == workflow.state
    assert summary.is_terminal is False

    workflow.mark_diagnosed()

    assert summary.workflow_state == workflow.state
    assert summary.is_terminal is False

    workflow.require_action()

    assert summary.workflow_state == workflow.state
    assert summary.is_terminal is False


def test_summary_tracks_remediation_and_verification():
    workflow = build_workflow()
    history = TechnicianRecoveryCycleHistory(workflow)

    summary, _ = build_summary(
        workflow,
        history,
    )

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()

    workflow.start_remediation()

    assert summary.workflow_state == workflow.state
    assert summary.is_terminal is False

    workflow.start_verification()

    assert summary.workflow_state == workflow.state
    assert summary.is_terminal is False


def test_summary_reflects_resolution():
    workflow = build_workflow()
    history = TechnicianRecoveryCycleHistory(workflow)

    summary, _ = build_summary(
        workflow,
        history,
    )

    complete_lifecycle(workflow)

    assert summary.workflow_state == workflow.state
    assert summary.is_terminal is True
    assert workflow.is_terminal


def test_summary_preserves_case_identity_through_lifecycle():
    workflow = build_workflow()
    history = TechnicianRecoveryCycleHistory(workflow)

    summary, reasoning_summary = build_summary(
        workflow,
        history,
    )

    original_case_id = summary.case_id
    original_workflow_id = summary.workflow_id

    complete_lifecycle(workflow)

    assert summary.case_id == original_case_id
    assert summary.workflow_id == original_workflow_id
    assert summary.workflow is workflow
    assert reasoning_summary.workflow is workflow


def test_summary_tracks_workflow_history_as_content_changes():
    workflow = build_workflow()
    history = TechnicianRecoveryCycleHistory(workflow)

    summary, _ = build_summary(
        workflow,
        history,
    )

    assert summary.workflow_history == []

    workflow.start_investigation()

    assert summary.workflow_history == workflow.history
    assert len(summary.workflow_history) == 1

    workflow.mark_diagnosed()

    assert summary.workflow_history == workflow.history
    assert len(summary.workflow_history) == 2

    workflow.require_action()

    assert summary.workflow_history == workflow.history
    assert len(summary.workflow_history) == 3


def test_summary_exposes_recovery_history_through_reasoning_summary():
    workflow = build_workflow()
    history = TechnicianRecoveryCycleHistory(workflow)

    summary, reasoning_summary = build_summary(
        workflow,
        history,
    )

    first_cycle = record_recovery_cycle(history, workflow)
    second_cycle = record_recovery_cycle(history, workflow)

    assert summary.reasoning_summary is reasoning_summary
    assert reasoning_summary.cycle_history is history
    assert reasoning_summary.cycle_history.cycles[-2:] == [
        first_cycle,
        second_cycle,
    ]


def test_summary_preserves_recovery_history_after_resolution():
    workflow = build_workflow()
    history = TechnicianRecoveryCycleHistory(workflow)

    first_cycle = record_recovery_cycle(history, workflow)

    summary, reasoning_summary = build_summary(
        workflow,
        history,
    )

    complete_lifecycle(workflow)

    assert summary.is_terminal is True
    assert reasoning_summary.cycle_history.cycles[-1] is first_cycle
    assert reasoning_summary.cycle_history is history


def test_summary_preserves_recovery_history_after_reopen():
    workflow = build_workflow()
    history = TechnicianRecoveryCycleHistory(workflow)

    first_cycle = record_recovery_cycle(history, workflow)

    summary, reasoning_summary = build_summary(
        workflow,
        history,
    )

    complete_lifecycle(workflow)
    workflow.reopen()

    assert summary.workflow_state == workflow.state
    assert summary.is_terminal is False

    assert reasoning_summary.cycle_history is history
    assert reasoning_summary.cycle_history.cycles[-1] is first_cycle


def test_summary_tracks_reinvestigation():
    workflow = build_workflow()
    history = TechnicianRecoveryCycleHistory(workflow)

    first_cycle = record_recovery_cycle(history, workflow)

    summary, reasoning_summary = build_summary(
        workflow,
        history,
    )

    complete_lifecycle(workflow)

    workflow.reopen()

    second_cycle = record_recovery_cycle(history, workflow)

    assert summary.workflow_state == workflow.state
    assert summary.is_terminal is False

    assert reasoning_summary.cycle_history.cycles[-2:] == [
        first_cycle,
        second_cycle,
    ]

    continue_reinvestigation(workflow)

    assert summary.workflow_state == workflow.state
    assert summary.is_terminal is True

    assert reasoning_summary.cycle_history.cycles[-2:] == [
        first_cycle,
        second_cycle,
    ]


def test_summary_preserves_state_after_escalation():
    workflow = build_workflow()
    history = TechnicianRecoveryCycleHistory(workflow)

    summary, reasoning_summary = build_summary(
        workflow,
        history,
    )

    workflow.start_investigation()

    cycle = record_recovery_cycle(history, workflow)

    workflow.escalate()

    assert summary.workflow_state == workflow.state
    assert summary.is_terminal is True
    assert workflow.state.name == "ESCALATED"

    assert reasoning_summary.cycle_history.cycles[-1] is cycle


def test_failed_transition_does_not_corrupt_summary():
    workflow = build_workflow()
    history = TechnicianRecoveryCycleHistory(workflow)

    summary, reasoning_summary = build_summary(
        workflow,
        history,
    )

    cycle = record_recovery_cycle(history, workflow)

    try:
        workflow.resolve()
    except ValueError:
        pass

    assert summary.workflow_state == workflow.state
    assert summary.workflow_state.name == "OPEN"
    assert summary.is_terminal is False

    assert summary.workflow_history == workflow.history
    assert reasoning_summary.cycle_history.cycles[-1] is cycle


def test_summary_diagnostic_collections_remain_separate_from_recovery_history():
    workflow = build_workflow()
    history = TechnicianRecoveryCycleHistory(workflow)

    cycle = record_recovery_cycle(history, workflow)

    summary, reasoning_summary = build_summary(
        workflow,
        history,
    )

    assert summary.findings == []
    assert summary.root_causes == []
    assert summary.recommendations == []

    assert reasoning_summary.cycle_history.cycles[-1] is cycle
    assert cycle not in summary.findings
    assert cycle not in summary.root_causes
    assert cycle not in summary.recommendations


def test_repeated_summary_reads_do_not_change_case_state():
    workflow = build_workflow()
    history = TechnicianRecoveryCycleHistory(workflow)

    record_recovery_cycle(history, workflow)

    summary, reasoning_summary = build_summary(
        workflow,
        history,
    )

    initial_state = summary.workflow_state
    initial_history = summary.workflow_history
    initial_cycles = reasoning_summary.cycle_history.cycles

    for _ in range(5):
        assert summary.workflow_state == initial_state
        assert summary.workflow_history == initial_history
        assert summary.reasoning_summary is reasoning_summary
        assert reasoning_summary.cycle_history.cycles == initial_cycles

    assert workflow.state == initial_state
    assert workflow.history == initial_history
    assert history.cycles == initial_cycles


def test_long_lifecycle_sequence_keeps_summary_consistent():
    workflow = build_workflow()
    history = TechnicianRecoveryCycleHistory(workflow)

    summary, reasoning_summary = build_summary(
        workflow,
        history,
    )

    cycles = []

    workflow.start_investigation()

    for _ in range(10):
        cycles.append(
            record_recovery_cycle(history, workflow)
        )

    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    assert summary.workflow is workflow
    assert summary.case_id == workflow.case.case_id
    assert summary.workflow_id == workflow.workflow_id
    assert summary.workflow_state == workflow.state
    assert summary.is_terminal is True

    assert summary.workflow_history == workflow.history

    assert reasoning_summary.cycle_history is history
    assert reasoning_summary.cycle_history.cycles[-10:] == cycles
    assert len(reasoning_summary.cycle_history.cycles) == 11


def test_summary_remains_consistent_after_multiple_reopen_cycles():
    workflow = build_workflow()
    history = TechnicianRecoveryCycleHistory(workflow)

    summary, reasoning_summary = build_summary(
        workflow,
        history,
    )

    cycles = []

    for _ in range(3):
        cycles.append(
            record_recovery_cycle(history, workflow)
        )

        if workflow.state.name == "OPEN":
            complete_lifecycle(workflow)
        else:
            workflow.reopen()
            continue_reinvestigation(workflow)

    assert summary.workflow is workflow
    assert summary.case_id == workflow.case.case_id
    assert summary.workflow_id == workflow.workflow_id
    assert summary.workflow_state == workflow.state
    assert summary.is_terminal is True

    assert reasoning_summary.cycle_history is history
    assert reasoning_summary.cycle_history.cycles[-3:] == cycles
    assert len(reasoning_summary.cycle_history.cycles) == 4