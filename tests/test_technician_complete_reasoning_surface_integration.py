from engine.diagnostic_case import DiagnosticCase
from engine.recommendation import Recommendation
from engine.technician_case_notes import TechnicianCaseNotes
from engine.technician_case_summary import TechnicianCaseSummary
from engine.technician_decision import (
    TechnicianDecision,
    TechnicianDecisionType,
)
from engine.technician_recovery_cycle import TechnicianRecoveryCycle
from engine.technician_recovery_cycle_history import (
    TechnicianRecoveryCycleHistory,
)
from engine.technician_reasoning_summary import TechnicianReasoningSummary
from engine.technician_workflow import TechnicianWorkflow


def build_workflow():
    return TechnicianWorkflow(DiagnosticCase())


def build_recommendation(identifier):
    return Recommendation(
        identifier,
        "Test recommendation",
        "MEDIUM",
        "Test recommendation description",
        "Test recommendation rationale",
    )


def build_decision(workflow, decision_type, identifier):
    return TechnicianDecision(
        workflow,
        build_recommendation(identifier),
        decision_type,
        f"Decision notes for {identifier}.",
    )


def record_recovery_cycle(history, workflow):
    cycle = TechnicianRecoveryCycle(
        workflow,
        cycle_number=history.cycle_count,
    )
    history.record_cycle(cycle)
    return cycle


def build_reasoning_surface(workflow, history):
    summary = TechnicianCaseSummary(workflow)
    reasoning_summary = TechnicianReasoningSummary(
        workflow,
        history,
    )
    summary.set_reasoning_summary(reasoning_summary)
    return summary, reasoning_summary


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


def test_complete_reasoning_surface_exposes_expected_workflow_identity():
    workflow = build_workflow()
    history = TechnicianRecoveryCycleHistory(workflow)

    summary, reasoning_summary = build_reasoning_surface(
        workflow,
        history,
    )

    assert summary.workflow is workflow
    assert reasoning_summary.workflow is workflow
    assert summary.reasoning_summary is reasoning_summary
    assert reasoning_summary.cycle_history is history


def test_complete_reasoning_surface_can_coexist_with_notes_recovery_and_decision():
    workflow = build_workflow()
    history = TechnicianRecoveryCycleHistory(workflow)
    notes = TechnicianCaseNotes(workflow)

    notes.add_note("Initial technician observation.")
    cycle = record_recovery_cycle(history, workflow)

    decision = build_decision(
        workflow,
        TechnicianDecisionType.INVESTIGATE_FURTHER,
        "decision-1",
    )

    summary, reasoning_summary = build_reasoning_surface(
        workflow,
        history,
    )

    assert summary.workflow is workflow
    assert summary.reasoning_summary is reasoning_summary
    assert reasoning_summary.cycle_history is history

    assert notes.notes[0].text == "Initial technician observation."
    assert reasoning_summary.cycle_history.cycles[-1] is cycle

    assert decision.workflow is workflow
    assert decision.decision_type is TechnicianDecisionType.INVESTIGATE_FURTHER


def test_summary_reads_do_not_replace_underlying_records():
    workflow = build_workflow()
    history = TechnicianRecoveryCycleHistory(workflow)
    notes = TechnicianCaseNotes(workflow)

    notes.add_note("Stable observation.")
    cycle = record_recovery_cycle(history, workflow)

    decision = build_decision(
        workflow,
        TechnicianDecisionType.ACCEPT,
        "decision-1",
    )

    summary, reasoning_summary = build_reasoning_surface(
        workflow,
        history,
    )

    original_history = reasoning_summary.cycle_history
    original_notes = notes.notes
    original_decision = decision

    for _ in range(5):
        assert summary.workflow is workflow
        assert summary.reasoning_summary is reasoning_summary
        assert reasoning_summary.cycle_history is original_history
        assert notes.notes == original_notes
        assert decision is original_decision

    assert reasoning_summary.cycle_history.cycles[-1] is cycle


def test_lifecycle_preserves_complete_reasoning_surface():
    workflow = build_workflow()
    history = TechnicianRecoveryCycleHistory(workflow)
    notes = TechnicianCaseNotes(workflow)

    notes.add_note("Lifecycle observation.")
    cycle = record_recovery_cycle(history, workflow)

    decision = build_decision(
        workflow,
        TechnicianDecisionType.ACCEPT,
        "decision-1",
    )

    summary, reasoning_summary = build_reasoning_surface(
        workflow,
        history,
    )

    complete_lifecycle(workflow)

    assert workflow.is_terminal
    assert summary.workflow_state == workflow.state
    assert summary.is_terminal is True

    assert notes.notes[0].text == "Lifecycle observation."
    assert reasoning_summary.cycle_history.cycles[-1] is cycle

    assert decision.workflow is workflow
    assert decision.decision_type is TechnicianDecisionType.ACCEPT


def test_reopen_preserves_complete_reasoning_surface():
    workflow = build_workflow()
    history = TechnicianRecoveryCycleHistory(workflow)
    notes = TechnicianCaseNotes(workflow)

    notes.add_note("Original investigation.")
    cycle = record_recovery_cycle(history, workflow)

    decision = build_decision(
        workflow,
        TechnicianDecisionType.DEFER,
        "decision-1",
    )

    summary, reasoning_summary = build_reasoning_surface(
        workflow,
        history,
    )

    complete_lifecycle(workflow)
    workflow.reopen()

    assert summary.workflow_state == workflow.state
    assert summary.is_terminal is False

    assert notes.notes[0].text == "Original investigation."
    assert reasoning_summary.cycle_history.cycles[-1] is cycle

    assert decision.workflow is workflow
    assert decision.decision_type is TechnicianDecisionType.DEFER


def test_reinvestigation_can_extend_complete_reasoning_surface():
    workflow = build_workflow()
    history = TechnicianRecoveryCycleHistory(workflow)
    notes = TechnicianCaseNotes(workflow)

    notes.add_note("First investigation.")
    first_cycle = record_recovery_cycle(history, workflow)

    first_decision = build_decision(
        workflow,
        TechnicianDecisionType.INVESTIGATE_FURTHER,
        "decision-1",
    )

    summary, reasoning_summary = build_reasoning_surface(
        workflow,
        history,
    )

    complete_lifecycle(workflow)
    workflow.reopen()

    notes.add_note("Second investigation.")
    second_cycle = record_recovery_cycle(history, workflow)

    second_decision = build_decision(
        workflow,
        TechnicianDecisionType.ACCEPT,
        "decision-2",
    )

    continue_reinvestigation(workflow)

    assert [note.text for note in notes.notes] == [
        "First investigation.",
        "Second investigation.",
    ]

    assert reasoning_summary.cycle_history.cycles[-2:] == [
        first_cycle,
        second_cycle,
    ]

    assert first_decision.decision_type is (
        TechnicianDecisionType.INVESTIGATE_FURTHER
    )
    assert second_decision.decision_type is (
        TechnicianDecisionType.ACCEPT
    )

    assert summary.workflow_state == workflow.state
    assert summary.is_terminal is True


def test_escalation_preserves_complete_reasoning_surface():
    workflow = build_workflow()
    history = TechnicianRecoveryCycleHistory(workflow)
    notes = TechnicianCaseNotes(workflow)

    workflow.start_investigation()

    notes.add_note("Escalation observation.")
    cycle = record_recovery_cycle(history, workflow)

    decision = build_decision(
        workflow,
        TechnicianDecisionType.ESCALATE,
        "decision-1",
    )

    summary, reasoning_summary = build_reasoning_surface(
        workflow,
        history,
    )

    workflow.escalate()

    assert workflow.state.name == "ESCALATED"
    assert summary.workflow_state == workflow.state
    assert summary.is_terminal is True

    assert notes.notes[0].text == "Escalation observation."
    assert reasoning_summary.cycle_history.cycles[-1] is cycle

    assert decision.workflow is workflow
    assert decision.decision_type is TechnicianDecisionType.ESCALATE


def test_failed_operation_preserves_complete_reasoning_surface():
    workflow = build_workflow()
    history = TechnicianRecoveryCycleHistory(workflow)
    notes = TechnicianCaseNotes(workflow)

    notes.add_note("Before invalid transition.")
    cycle = record_recovery_cycle(history, workflow)

    decision = build_decision(
        workflow,
        TechnicianDecisionType.REJECT,
        "decision-1",
    )

    summary, reasoning_summary = build_reasoning_surface(
        workflow,
        history,
    )

    try:
        workflow.resolve()
    except ValueError:
        pass

    assert workflow.state.name == "OPEN"
    assert summary.workflow_state == workflow.state

    assert notes.notes[0].text == "Before invalid transition."
    assert reasoning_summary.cycle_history.cycles[-1] is cycle

    assert decision.workflow is workflow
    assert decision.decision_type is TechnicianDecisionType.REJECT


def test_complete_reasoning_surface_does_not_contaminate_diagnostic_case():
    workflow = build_workflow()
    history = TechnicianRecoveryCycleHistory(workflow)
    notes = TechnicianCaseNotes(workflow)

    notes.add_note("Operational note.")
    record_recovery_cycle(history, workflow)

    build_decision(
        workflow,
        TechnicianDecisionType.DEFER,
        "decision-1",
    )

    summary, reasoning_summary = build_reasoning_surface(
        workflow,
        history,
    )

    assert summary.reasoning_summary is reasoning_summary
    assert reasoning_summary.cycle_history is history

    assert workflow.case.findings == []
    assert workflow.case.root_causes == []
    assert workflow.case.recommendations == []
    assert workflow.case.correlations == []


def test_complete_reasoning_surface_remains_separate_from_workflow_history():
    workflow = build_workflow()
    history = TechnicianRecoveryCycleHistory(workflow)
    notes = TechnicianCaseNotes(workflow)

    workflow.start_investigation()

    notes.add_note("Investigation note.")
    cycle = record_recovery_cycle(history, workflow)

    decision = build_decision(
        workflow,
        TechnicianDecisionType.INVESTIGATE_FURTHER,
        "decision-1",
    )

    summary, reasoning_summary = build_reasoning_surface(
        workflow,
        history,
    )

    workflow.mark_diagnosed()

    assert len(workflow.history) == 2
    assert cycle not in workflow.history
    assert decision not in workflow.history

    assert summary.workflow_history == workflow.history
    assert reasoning_summary.cycle_history is history


def test_multiple_records_remain_ordered_across_complete_surface():
    workflow = build_workflow()
    history = TechnicianRecoveryCycleHistory(workflow)
    notes = TechnicianCaseNotes(workflow)

    decisions = []
    cycles = []

    for index in range(5):
        notes.add_note(f"Note {index}.")
        cycles.append(record_recovery_cycle(history, workflow))

        decisions.append(
            build_decision(
                workflow,
                TechnicianDecisionType.INVESTIGATE_FURTHER,
                f"decision-{index}",
            )
        )

    summary, reasoning_summary = build_reasoning_surface(
        workflow,
        history,
    )

    assert [note.text for note in notes.notes] == [
        "Note 0.",
        "Note 1.",
        "Note 2.",
        "Note 3.",
        "Note 4.",
    ]

    assert reasoning_summary.cycle_history.cycles[-5:] == cycles

    assert len(decisions) == 5
    assert all(decision.workflow is workflow for decision in decisions)

    assert summary.workflow is workflow
    assert summary.reasoning_summary is reasoning_summary


def test_complete_reasoning_surface_preserves_record_identity_after_new_records():
    workflow = build_workflow()
    history = TechnicianRecoveryCycleHistory(workflow)
    notes = TechnicianCaseNotes(workflow)

    notes.add_note("Original note.")
    first_cycle = record_recovery_cycle(history, workflow)

    first_decision = build_decision(
        workflow,
        TechnicianDecisionType.DEFER,
        "decision-1",
    )

    summary, reasoning_summary = build_reasoning_surface(
        workflow,
        history,
    )

    notes.add_note("New note.")
    second_cycle = record_recovery_cycle(history, workflow)

    second_decision = build_decision(
        workflow,
        TechnicianDecisionType.ACCEPT,
        "decision-2",
    )

    assert notes.notes[0].text == "Original note."
    assert notes.notes[1].text == "New note."

    assert reasoning_summary.cycle_history.cycles[-2:] == [
        first_cycle,
        second_cycle,
    ]

    assert first_decision is not second_decision
    assert first_decision.decision_type is TechnicianDecisionType.DEFER
    assert second_decision.decision_type is TechnicianDecisionType.ACCEPT

    assert summary.workflow is workflow
    assert summary.reasoning_summary is reasoning_summary


def test_long_sequence_keeps_complete_reasoning_surface_consistent():
    workflow = build_workflow()
    history = TechnicianRecoveryCycleHistory(workflow)
    notes = TechnicianCaseNotes(workflow)

    decisions = []
    cycles = []

    workflow.start_investigation()

    for index in range(10):
        notes.add_note(f"Long sequence note {index}.")
        cycles.append(record_recovery_cycle(history, workflow))

        decisions.append(
            build_decision(
                workflow,
                TechnicianDecisionType.INVESTIGATE_FURTHER,
                f"long-decision-{index}",
            )
        )

    summary, reasoning_summary = build_reasoning_surface(
        workflow,
        history,
    )

    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    assert workflow.is_terminal

    assert len(notes.notes) == 10
    assert len(decisions) == 10
    assert len(reasoning_summary.cycle_history.cycles) == 11

    assert reasoning_summary.cycle_history.cycles[-10:] == cycles
    assert all(decision.workflow is workflow for decision in decisions)

    assert summary.workflow is workflow
    assert summary.reasoning_summary is reasoning_summary
    assert summary.workflow_state == workflow.state
    assert summary.is_terminal is True