import pytest

from engine.technician_case_notes import TechnicianCaseNotes
from engine.technician_case_summary import TechnicianCaseSummary
from engine.technician_reasoning_summary import TechnicianReasoningSummary
from engine.technician_recovery_cycle import TechnicianRecoveryCycle
from engine.technician_recovery_cycle_history import (
    TechnicianRecoveryCycleHistory,
)
from engine.technician_workflow import TechnicianWorkflow


class FakeCase:
    case_id = "case-001"
    findings = []
    root_causes = []
    recommendations = []


@pytest.fixture
def workflow():
    workflow = TechnicianWorkflow(FakeCase())
    workflow.start_investigation()
    return workflow


@pytest.fixture
def recovery_history(workflow):
    return TechnicianRecoveryCycleHistory(workflow)


@pytest.fixture
def notes(workflow):
    return TechnicianCaseNotes(workflow)


@pytest.fixture
def summary(workflow, recovery_history):
    summary = TechnicianCaseSummary(workflow)
    summary.set_reasoning_summary(
        TechnicianReasoningSummary(
            workflow,
            recovery_history,
        )
    )
    return summary


def record_recovery_cycle(history, workflow):
    cycle = TechnicianRecoveryCycle(
        workflow,
        cycle_number=history.cycle_count,
    )

    history.record_cycle(cycle)

    return cycle


def test_notes_and_recovery_history_can_coexist(
    notes,
    recovery_history,
    workflow,
):
    note = notes.add_note(
        "Reviewed the failed diagnostic."
    )

    cycle = record_recovery_cycle(
        recovery_history,
        workflow,
    )

    assert notes.notes == [note]
    assert recovery_history.cycles[-1] is cycle


def test_recording_recovery_does_not_replace_notes(
    notes,
    recovery_history,
    workflow,
):
    note = notes.add_note(
        "Recovery investigation documented."
    )

    record_recovery_cycle(
        recovery_history,
        workflow,
    )

    assert notes.notes == [note]


def test_adding_notes_does_not_replace_recovery_history(
    notes,
    recovery_history,
    workflow,
):
    cycle = record_recovery_cycle(
        recovery_history,
        workflow,
    )

    notes.add_note(
        "Recovery cycle documented."
    )

    assert recovery_history.cycles[-1] is cycle


def test_note_and_recovery_cycle_remain_independent_records(
    notes,
    recovery_history,
    workflow,
):
    note = notes.add_note(
        "Investigated recovery context."
    )

    cycle = record_recovery_cycle(
        recovery_history,
        workflow,
    )

    assert note is not cycle
    assert notes.notes == [note]
    assert recovery_history.cycles[-1] is cycle


def test_case_summary_can_expose_reasoning_summary_with_recovery_history(
    summary,
    recovery_history,
    workflow,
):
    cycle = record_recovery_cycle(
        recovery_history,
        workflow,
    )

    assert summary.reasoning_summary is not None
    assert (
        summary.reasoning_summary.cycle_history
        is recovery_history
    )
    assert (
        summary.reasoning_summary.cycle_history.cycles[-1]
        is cycle
    )


def test_notes_do_not_change_case_summary_workflow_identity(
    notes,
    summary,
    workflow,
):
    notes.add_note(
        "Documented the current workflow."
    )

    assert summary.workflow is workflow
    assert summary.workflow_id == workflow.workflow_id
    assert summary.case_id == workflow.case.case_id


def test_recovery_does_not_change_case_summary_workflow_identity(
    summary,
    recovery_history,
    workflow,
):
    record_recovery_cycle(
        recovery_history,
        workflow,
    )

    assert summary.workflow is workflow
    assert summary.workflow_id == workflow.workflow_id
    assert summary.case_id == workflow.case.case_id


def test_multiple_notes_and_recovery_cycles_remain_ordered(
    notes,
    recovery_history,
    workflow,
):
    first_note = notes.add_note(
        "First investigation note."
    )

    first_cycle = record_recovery_cycle(
        recovery_history,
        workflow,
    )

    second_note = notes.add_note(
        "Second investigation note."
    )

    second_cycle = record_recovery_cycle(
        recovery_history,
        workflow,
    )

    assert notes.notes == [
        first_note,
        second_note,
    ]

    assert recovery_history.cycles[-2:] == [
        first_cycle,
        second_cycle,
    ]


def test_recovery_history_survives_notes_added_after_recovery(
    notes,
    recovery_history,
    workflow,
):
    first_cycle = record_recovery_cycle(
        recovery_history,
        workflow,
    )

    notes.add_note(
        "Technician reviewed recovery result."
    )

    second_cycle = record_recovery_cycle(
        recovery_history,
        workflow,
    )

    assert recovery_history.cycles[-2:] == [
        first_cycle,
        second_cycle,
    ]

    assert len(notes.notes) == 1


def test_notes_and_recovery_history_survive_repeated_reads(
    notes,
    recovery_history,
    summary,
    workflow,
):
    note = notes.add_note(
        "Initial recovery documentation."
    )

    cycle = record_recovery_cycle(
        recovery_history,
        workflow,
    )

    first_notes_read = notes.notes
    second_notes_read = notes.notes

    first_cycles_read = recovery_history.cycles
    second_cycles_read = recovery_history.cycles

    assert first_notes_read == second_notes_read
    assert first_notes_read[0] is note

    assert first_cycles_read == second_cycles_read
    assert first_cycles_read[-1] is cycle

    assert (
        summary.reasoning_summary.cycle_history
        is recovery_history
    )


def test_notes_and_recovery_history_remain_separate_from_workflow_history(
    notes,
    recovery_history,
    workflow,
):
    workflow_history_before = list(
        workflow.history
    )

    notes.add_note(
        "Documented investigation state."
    )

    cycle = record_recovery_cycle(
        recovery_history,
        workflow,
    )

    assert workflow.history == workflow_history_before
    assert cycle not in workflow.history


def test_failed_workflow_operation_does_not_corrupt_notes_or_recovery_history(
    notes,
    recovery_history,
    workflow,
):
    note = notes.add_note(
        "Before invalid workflow operation."
    )

    cycle = record_recovery_cycle(
        recovery_history,
        workflow,
    )

    with pytest.raises(ValueError):
        workflow.resolve()

    assert notes.notes == [note]
    assert recovery_history.cycles[-1] is cycle


def test_notes_preserve_workflow_state_at_time_of_recording(
    notes,
    workflow,
):
    note = notes.add_note(
        "Investigation documented."
    )

    assert note.workflow_state is workflow.state


def test_recovery_history_remains_visible_after_workflow_reopen(
    notes,
    recovery_history,
    summary,
    workflow,
):
    notes.add_note(
        "Initial recovery documentation."
    )

    first_cycle = record_recovery_cycle(
        recovery_history,
        workflow,
    )

    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    workflow.reopen()

    notes.add_note(
        "Reopened investigation documented."
    )

    second_cycle = record_recovery_cycle(
        recovery_history,
        workflow,
    )

    assert recovery_history.cycles[-2:] == [
        first_cycle,
        second_cycle,
    ]

    assert (
        summary.reasoning_summary.cycle_history
        is recovery_history
    )

    assert (
        summary.reasoning_summary.cycle_history.cycles[-2:]
        == [
            first_cycle,
            second_cycle,
        ]
    )


def test_long_notes_and_recovery_sequence_remains_intact(
    notes,
    recovery_history,
    summary,
    workflow,
):
    recorded_notes = []
    recorded_cycles = []

    for index in range(10):
        recorded_notes.append(
            notes.add_note(
                f"Recovery investigation note {index + 1}."
            )
        )

        recorded_cycles.append(
            record_recovery_cycle(
                recovery_history,
                workflow,
            )
        )

    assert notes.notes == recorded_notes

    assert recovery_history.cycles[-10:] == (
        recorded_cycles
    )

    assert (
        summary.reasoning_summary.cycle_history.cycles[-10:]
        == recorded_cycles
    )


def test_reading_summary_does_not_create_notes_or_recovery_cycles(
    notes,
    recovery_history,
    summary,
):
    note = notes.add_note(
        "Stable documentation."
    )

    cycle = record_recovery_cycle(
        recovery_history,
        summary.workflow,
    )

    notes_before = list(notes.notes)
    cycles_before = list(
        recovery_history.cycles
    )

    _ = summary.reasoning_summary
    _ = summary.reasoning_summary.cycle_history
    _ = summary.reasoning_summary.cycle_history.cycles
    _ = summary.workflow_history

    assert notes.notes == notes_before
    assert recovery_history.cycles == cycles_before

    assert notes.notes[0] is note
    assert recovery_history.cycles[-1] is cycle