from engine.diagnostic_case import DiagnosticCase
from engine.recommendation import Recommendation
from engine.technician_case_notes import TechnicianCaseNotes
from engine.technician_decision import (
    TechnicianDecision,
    TechnicianDecisionType,
)
from engine.technician_recovery_cycle import TechnicianRecoveryCycle
from engine.technician_recovery_cycle_history import (
    TechnicianRecoveryCycleHistory,
)
from engine.technician_workflow import TechnicianWorkflow


def build_workflow():
    return TechnicianWorkflow(DiagnosticCase())


def build_recommendation(identifier="test-recommendation"):
    return Recommendation(
        identifier,
        "Test recommendation",
        "MEDIUM",
        "Test recommendation description",
        "Test recommendation rationale",
    )


def record_recovery_cycle(history, workflow):
    cycle = TechnicianRecoveryCycle(
        workflow,
        cycle_number=history.cycle_count,
    )
    history.record_cycle(cycle)
    return cycle


def create_decision(workflow, decision_type, identifier):
    recommendation = build_recommendation(identifier)

    return TechnicianDecision(
        workflow,
        recommendation,
        decision_type,
        f"Decision note for {identifier}.",
    )


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


def test_notes_recovery_and_decision_can_coexist():
    workflow = build_workflow()
    notes = TechnicianCaseNotes(workflow)
    history = TechnicianRecoveryCycleHistory(workflow)

    notes.add_note("Initial investigation.")
    cycle = record_recovery_cycle(history, workflow)

    decision = create_decision(
        workflow,
        TechnicianDecisionType.INVESTIGATE_FURTHER,
        "decision-1",
    )

    assert notes.notes[0].text == "Initial investigation."
    assert history.cycles[-1] is cycle
    assert decision.workflow is workflow
    assert decision.decision_type is TechnicianDecisionType.INVESTIGATE_FURTHER


def test_workflow_lifecycle_preserves_notes_recovery_and_decision():
    workflow = build_workflow()
    notes = TechnicianCaseNotes(workflow)
    history = TechnicianRecoveryCycleHistory(workflow)

    notes.add_note("Before lifecycle.")
    cycle = record_recovery_cycle(history, workflow)

    decision = create_decision(
        workflow,
        TechnicianDecisionType.ACCEPT,
        "decision-1",
    )

    complete_lifecycle(workflow)

    assert workflow.is_terminal
    assert notes.notes[0].text == "Before lifecycle."
    assert history.cycles[-1] is cycle
    assert decision.workflow is workflow
    assert decision.decision_type is TechnicianDecisionType.ACCEPT


def test_recovery_does_not_mutate_decision_or_notes():
    workflow = build_workflow()
    notes = TechnicianCaseNotes(workflow)
    history = TechnicianRecoveryCycleHistory(workflow)

    notes.add_note("Original note.")

    decision = create_decision(
        workflow,
        TechnicianDecisionType.DEFER,
        "decision-1",
    )

    original_decision_id = decision.decision_id
    original_notes = notes.notes

    cycle = record_recovery_cycle(history, workflow)

    assert decision.decision_id == original_decision_id
    assert decision.decision_type is TechnicianDecisionType.DEFER
    assert notes.notes == original_notes
    assert history.cycles[-1] is cycle


def test_multiple_decisions_recovery_cycles_and_notes_remain_independent():
    workflow = build_workflow()
    notes = TechnicianCaseNotes(workflow)
    history = TechnicianRecoveryCycleHistory(workflow)

    notes.add_note("First note.")
    first_cycle = record_recovery_cycle(history, workflow)
    first_decision = create_decision(
        workflow,
        TechnicianDecisionType.INVESTIGATE_FURTHER,
        "decision-1",
    )

    notes.add_note("Second note.")
    second_cycle = record_recovery_cycle(history, workflow)
    second_decision = create_decision(
        workflow,
        TechnicianDecisionType.ACCEPT,
        "decision-2",
    )

    notes.add_note("Third note.")
    third_cycle = record_recovery_cycle(history, workflow)
    third_decision = create_decision(
        workflow,
        TechnicianDecisionType.DEFER,
        "decision-3",
    )

    assert [note.text for note in notes.notes] == [
        "First note.",
        "Second note.",
        "Third note.",
    ]

    assert history.cycles[-3:] == [
        first_cycle,
        second_cycle,
        third_cycle,
    ]

    assert first_decision is not second_decision
    assert second_decision is not third_decision
    assert first_decision.workflow is workflow
    assert second_decision.workflow is workflow
    assert third_decision.workflow is workflow


def test_reopen_preserves_notes_recovery_and_decision():
    workflow = build_workflow()
    notes = TechnicianCaseNotes(workflow)
    history = TechnicianRecoveryCycleHistory(workflow)

    notes.add_note("Initial case.")
    cycle = record_recovery_cycle(history, workflow)

    decision = create_decision(
        workflow,
        TechnicianDecisionType.REJECT,
        "decision-1",
    )

    complete_lifecycle(workflow)
    workflow.reopen()

    assert workflow.state.name == "INVESTIGATING"
    assert notes.notes[0].text == "Initial case."
    assert history.cycles[-1] is cycle
    assert decision.workflow is workflow
    assert decision.decision_type is TechnicianDecisionType.REJECT


def test_reinvestigation_can_add_new_records_without_mutating_previous_records():
    workflow = build_workflow()
    notes = TechnicianCaseNotes(workflow)
    history = TechnicianRecoveryCycleHistory(workflow)

    notes.add_note("First investigation.")
    first_cycle = record_recovery_cycle(history, workflow)

    first_decision = create_decision(
        workflow,
        TechnicianDecisionType.INVESTIGATE_FURTHER,
        "decision-1",
    )

    complete_lifecycle(workflow)

    workflow.reopen()

    notes.add_note("Reinvestigation.")
    second_cycle = record_recovery_cycle(history, workflow)

    second_decision = create_decision(
        workflow,
        TechnicianDecisionType.ACCEPT,
        "decision-2",
    )

    continue_reinvestigation(workflow)

    assert [note.text for note in notes.notes] == [
        "First investigation.",
        "Reinvestigation.",
    ]

    assert history.cycles[-2:] == [
        first_cycle,
        second_cycle,
    ]

    assert first_decision.decision_type is TechnicianDecisionType.INVESTIGATE_FURTHER
    assert second_decision.decision_type is TechnicianDecisionType.ACCEPT
    assert first_decision is not second_decision
    assert workflow.is_terminal


def test_escalation_preserves_all_three_record_types():
    workflow = build_workflow()
    notes = TechnicianCaseNotes(workflow)
    history = TechnicianRecoveryCycleHistory(workflow)

    workflow.start_investigation()

    notes.add_note("Escalation required.")
    cycle = record_recovery_cycle(history, workflow)

    decision = create_decision(
        workflow,
        TechnicianDecisionType.ESCALATE,
        "decision-1",
    )

    workflow.escalate()

    assert workflow.state.name == "ESCALATED"
    assert notes.notes[0].text == "Escalation required."
    assert history.cycles[-1] is cycle
    assert decision.workflow is workflow
    assert decision.decision_type is TechnicianDecisionType.ESCALATE


def test_failed_workflow_operation_does_not_corrupt_notes_recovery_or_decision():
    workflow = build_workflow()
    notes = TechnicianCaseNotes(workflow)
    history = TechnicianRecoveryCycleHistory(workflow)

    notes.add_note("Before invalid operation.")
    cycle = record_recovery_cycle(history, workflow)

    decision = create_decision(
        workflow,
        TechnicianDecisionType.DEFER,
        "decision-1",
    )

    try:
        workflow.resolve()
    except ValueError:
        pass

    assert workflow.state.name == "OPEN"
    assert notes.notes[0].text == "Before invalid operation."
    assert history.cycles[-1] is cycle
    assert decision.workflow is workflow
    assert decision.decision_type is TechnicianDecisionType.DEFER


def test_notes_recovery_and_decision_remain_separate_from_workflow_history():
    workflow = build_workflow()
    notes = TechnicianCaseNotes(workflow)
    history = TechnicianRecoveryCycleHistory(workflow)

    workflow.start_investigation()
    notes.add_note("Investigation.")

    cycle = record_recovery_cycle(history, workflow)

    decision = create_decision(
        workflow,
        TechnicianDecisionType.INVESTIGATE_FURTHER,
        "decision-1",
    )

    workflow.mark_diagnosed()

    assert len(workflow.history) == 2
    assert len(history.cycles) == 2

    assert cycle not in workflow.history
    assert decision not in workflow.history
    assert notes.notes[0].text == "Investigation."


def test_all_decision_types_can_coexist_with_recovery_history():
    workflow = build_workflow()
    history = TechnicianRecoveryCycleHistory(workflow)

    decision_types = [
        TechnicianDecisionType.ACCEPT,
        TechnicianDecisionType.REJECT,
        TechnicianDecisionType.DEFER,
        TechnicianDecisionType.INVESTIGATE_FURTHER,
        TechnicianDecisionType.ESCALATE,
    ]

    decisions = []

    for index, decision_type in enumerate(decision_types, start=1):
        record_recovery_cycle(history, workflow)

        decisions.append(
            create_decision(
                workflow,
                decision_type,
                f"decision-{index}",
            )
        )

    assert len(decisions) == 5
    assert [
        decision.decision_type
        for decision in decisions
    ] == decision_types

    assert len(history.cycles) == 6
    assert [cycle.cycle_number for cycle in history.cycles] == list(range(6))


def test_long_lifecycle_sequence_preserves_all_three_record_types():
    workflow = build_workflow()
    notes = TechnicianCaseNotes(workflow)
    history = TechnicianRecoveryCycleHistory(workflow)

    workflow.start_investigation()

    expected_notes = []
    expected_cycles = []
    decisions = []

    for index in range(10):
        note_text = f"Lifecycle note {index}."
        notes.add_note(note_text)
        expected_notes.append(note_text)

        expected_cycles.append(
            record_recovery_cycle(history, workflow)
        )

        decisions.append(
            create_decision(
                workflow,
                TechnicianDecisionType.INVESTIGATE_FURTHER,
                f"decision-{index}",
            )
        )

    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    assert [note.text for note in notes.notes] == expected_notes
    assert history.cycles[-10:] == expected_cycles
    assert len(decisions) == 10
    assert all(decision.workflow is workflow for decision in decisions)
    assert workflow.is_terminal


def test_repeated_reads_do_not_create_or_duplicate_records():
    workflow = build_workflow()
    notes = TechnicianCaseNotes(workflow)
    history = TechnicianRecoveryCycleHistory(workflow)

    notes.add_note("Stable note.")
    cycle = record_recovery_cycle(history, workflow)

    decision = create_decision(
        workflow,
        TechnicianDecisionType.ACCEPT,
        "decision-1",
    )

    initial_notes = notes.notes
    initial_cycles = history.cycles

    for _ in range(5):
        assert notes.notes == initial_notes
        assert history.cycles == initial_cycles

        assert decision.workflow is workflow
        assert decision.decision_type is TechnicianDecisionType.ACCEPT

    assert len(notes.notes) == 1
    assert len(history.cycles) == 2
    assert history.cycles[-1] is cycle