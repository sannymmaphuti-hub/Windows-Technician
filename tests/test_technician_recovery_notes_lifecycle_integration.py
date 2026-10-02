from engine.diagnostic_case import DiagnosticCase
from engine.technician_case_notes import TechnicianCaseNotes
from engine.technician_recovery_cycle import TechnicianRecoveryCycle
from engine.technician_recovery_cycle_history import TechnicianRecoveryCycleHistory
from engine.technician_workflow import TechnicianWorkflow


def build_workflow():
    return TechnicianWorkflow(DiagnosticCase())


def build_notes(workflow):
    return TechnicianCaseNotes(workflow)


def build_recovery_history(workflow):
    return TechnicianRecoveryCycleHistory(workflow)


def record_recovery_cycle(history, workflow):
    cycle = TechnicianRecoveryCycle(
        workflow,
        cycle_number=history.cycle_count,
    )
    history.record_cycle(cycle)
    return cycle


def complete_initial_lifecycle(workflow):
    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()


def continue_reopened_lifecycle(workflow):
    workflow.reopen()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()


def test_notes_and_recovery_history_survive_initial_lifecycle():
    workflow = build_workflow()
    notes = build_notes(workflow)
    history = build_recovery_history(workflow)

    notes.add_note("Initial investigation")
    cycle = record_recovery_cycle(history, workflow)

    complete_initial_lifecycle(workflow)

    assert notes.notes[0].text == "Initial investigation"
    assert history.cycles[-1] is cycle
    assert workflow.is_terminal is True


def test_notes_added_during_lifecycle_do_not_replace_recovery_history():
    workflow = build_workflow()
    notes = build_notes(workflow)
    history = build_recovery_history(workflow)

    first_cycle = record_recovery_cycle(history, workflow)

    workflow.start_investigation()
    notes.add_note("Investigation started")

    workflow.mark_diagnosed()
    notes.add_note("Diagnosis completed")

    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    assert history.cycles[-1] is first_cycle
    assert [note.text for note in notes.notes] == [
        "Investigation started",
        "Diagnosis completed",
    ]


def test_recovery_recorded_during_investigation_survives_resolution():
    workflow = build_workflow()
    notes = build_notes(workflow)
    history = build_recovery_history(workflow)

    workflow.start_investigation()
    notes.add_note("Investigation note")

    cycle = record_recovery_cycle(history, workflow)

    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    assert history.cycles[-1] is cycle
    assert notes.notes[0].text == "Investigation note"


def test_multiple_notes_and_recovery_cycles_remain_ordered():
    workflow = build_workflow()
    notes = build_notes(workflow)
    history = build_recovery_history(workflow)

    notes.add_note("Note 1")
    cycle_1 = record_recovery_cycle(history, workflow)

    workflow.start_investigation()
    notes.add_note("Note 2")
    cycle_2 = record_recovery_cycle(history, workflow)

    workflow.mark_diagnosed()
    notes.add_note("Note 3")
    cycle_3 = record_recovery_cycle(history, workflow)

    assert [note.text for note in notes.notes] == [
        "Note 1",
        "Note 2",
        "Note 3",
    ]

    assert history.cycles[-3:] == [
        cycle_1,
        cycle_2,
        cycle_3,
    ]


def test_reopen_preserves_notes_and_recovery_history():
    workflow = build_workflow()
    notes = build_notes(workflow)
    history = build_recovery_history(workflow)

    notes.add_note("Before closure")
    first_cycle = record_recovery_cycle(history, workflow)

    complete_initial_lifecycle(workflow)

    workflow.reopen()

    assert notes.notes[0].text == "Before closure"
    assert history.cycles[-1] is first_cycle

    notes.add_note("After reopening")
    second_cycle = record_recovery_cycle(history, workflow)

    assert [note.text for note in notes.notes] == [
        "Before closure",
        "After reopening",
    ]

    assert history.cycles[-2:] == [
        first_cycle,
        second_cycle,
    ]


def test_reinvestigation_preserves_previous_notes_and_recovery_cycles():
    workflow = build_workflow()
    notes = build_notes(workflow)
    history = build_recovery_history(workflow)

    notes.add_note("Initial case")
    first_cycle = record_recovery_cycle(history, workflow)

    complete_initial_lifecycle(workflow)

    continue_reopened_lifecycle(workflow)

    notes.add_note("Reinvestigation")
    second_cycle = record_recovery_cycle(history, workflow)

    assert [note.text for note in notes.notes] == [
        "Initial case",
        "Reinvestigation",
    ]

    assert history.cycles[-2:] == [
        first_cycle,
        second_cycle,
    ]


def test_escalation_preserves_notes_and_recovery_history():
    workflow = build_workflow()
    notes = build_notes(workflow)
    history = build_recovery_history(workflow)

    workflow.start_investigation()
    notes.add_note("Escalation required")

    cycle = record_recovery_cycle(history, workflow)

    workflow.escalate()

    assert workflow.is_terminal is True
    assert notes.notes[0].text == "Escalation required"
    assert history.cycles[-1] is cycle


def test_failed_workflow_operation_does_not_corrupt_notes_or_recovery_history():
    workflow = build_workflow()
    notes = build_notes(workflow)
    history = build_recovery_history(workflow)

    notes.add_note("Before invalid operation")
    cycle = record_recovery_cycle(history, workflow)

    try:
        workflow.resolve()
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected invalid workflow operation to raise ValueError."
        )

    assert notes.notes[0].text == "Before invalid operation"
    assert history.cycles[-1] is cycle
    assert history.cycles[-1].cycle_number == cycle.cycle_number


def test_recovery_history_remains_separate_from_workflow_history():
    workflow = build_workflow()
    notes = build_notes(workflow)
    history = build_recovery_history(workflow)

    notes.add_note("Lifecycle note")
    cycle = record_recovery_cycle(history, workflow)

    workflow.start_investigation()
    workflow.mark_diagnosed()

    assert cycle not in workflow.history
    assert len(history.cycles) == 2
    assert len(workflow.history) == 2


def test_repeated_lifecycle_activity_does_not_duplicate_notes_or_recovery_cycles():
    workflow = build_workflow()
    notes = build_notes(workflow)
    history = build_recovery_history(workflow)

    notes.add_note("Persistent note")
    cycle = record_recovery_cycle(history, workflow)

    complete_initial_lifecycle(workflow)

    for _ in range(3):
        assert [note.text for note in notes.notes] == [
            "Persistent note"
        ]
        assert history.cycles[-1] is cycle
        assert len(history.cycles) == 2

    continue_reopened_lifecycle(workflow)

    assert [note.text for note in notes.notes] == [
        "Persistent note"
    ]

    assert history.cycles[-1] is cycle
    assert len(history.cycles) == 2


def test_new_records_after_reopen_do_not_mutate_previous_records():
    workflow = build_workflow()
    notes = build_notes(workflow)
    history = build_recovery_history(workflow)

    notes.add_note("Original note")
    first_cycle = record_recovery_cycle(history, workflow)

    complete_initial_lifecycle(workflow)

    workflow.reopen()

    notes.add_note("New note")
    second_cycle = record_recovery_cycle(history, workflow)

    assert first_cycle.cycle_number != second_cycle.cycle_number

    assert [note.text for note in notes.notes] == [
        "Original note",
        "New note",
    ]

    assert history.cycles[-2] is first_cycle
    assert history.cycles[-1] is second_cycle


def test_notes_and_recovery_history_remain_intact_after_long_sequence():
    workflow = build_workflow()
    notes = build_notes(workflow)
    history = build_recovery_history(workflow)

    recorded_cycles = []

    for index in range(1, 6):
        notes.add_note(f"Note {index}")

        recorded_cycles.append(
            record_recovery_cycle(history, workflow)
        )

        if workflow.state.name == "OPEN":
            workflow.start_investigation()

        elif workflow.state.name == "INVESTIGATING":
            workflow.mark_diagnosed()

        elif workflow.state.name == "DIAGNOSED":
            workflow.require_action()

        elif workflow.state.name == "ACTION_REQUIRED":
            workflow.start_remediation()

        elif workflow.state.name == "REMEDIATING":
            workflow.start_verification()

        elif workflow.state.name == "VERIFYING":
            workflow.resolve()

        elif workflow.state.name == "RESOLVED":
            workflow.reopen()

    assert [note.text for note in notes.notes] == [
        "Note 1",
        "Note 2",
        "Note 3",
        "Note 4",
        "Note 5",
    ]

    assert history.cycles[-5:] == recorded_cycles

    assert [
        cycle.cycle_number
        for cycle in history.cycles
    ] == [0, 1, 2, 3, 4, 5]


def test_reading_notes_and_recovery_history_does_not_create_records():
    workflow = build_workflow()
    notes = build_notes(workflow)
    history = build_recovery_history(workflow)

    notes.add_note("Stable note")
    cycle = record_recovery_cycle(history, workflow)

    notes_first = notes.notes
    notes_second = notes.notes

    cycles_first = history.cycles
    cycles_second = history.cycles

    assert notes_first == notes_second
    assert cycles_first == cycles_second

    assert history.cycles[-1] is cycle
    assert len(notes.notes) == 1
    assert len(history.cycles) == 2