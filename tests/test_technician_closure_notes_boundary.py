from engine.diagnostic_case import DiagnosticCase
from engine.technician_case_closure import TechnicianCaseClosure
from engine.technician_case_notes import TechnicianCaseNotes
from engine.technician_case_summary import TechnicianCaseSummary
from engine.technician_workflow import TechnicianWorkflow


def build_workflow():
    return TechnicianWorkflow(DiagnosticCase())


def resolve_workflow(workflow):
    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()


def build_summary(workflow):
    return TechnicianCaseSummary(workflow)


def build_notes(workflow):
    notes = TechnicianCaseNotes(workflow)
    notes.add_note(
        "Investigated memory pressure and identified excessive usage.",
    )
    return notes


def build_closure(workflow, technician="Test Technician"):
    return TechnicianCaseClosure(
        workflow=workflow,
        technician=technician,
        reason="Issue resolved and verified.",
    )


def note_signature(note):
    return (
        note.note_id,
        note.text,
        note.created_at,
        note.workflow_state,
    )


def note_signatures(summary):
    return [
        note_signature(note)
        for note in summary.notes
    ]


def test_closure_does_not_create_notes():
    workflow = build_workflow()
    summary = build_summary(workflow)

    assert summary.notes == []

    resolve_workflow(workflow)
    closure = build_closure(workflow)

    summary.set_closure(closure)

    assert summary.notes == []


def test_closure_does_not_remove_existing_notes():
    workflow = build_workflow()
    summary = build_summary(workflow)

    notes = build_notes(workflow)
    summary.set_notes(notes)

    notes_before = note_signatures(summary)

    resolve_workflow(workflow)
    closure = build_closure(workflow)

    summary.set_closure(closure)

    assert note_signatures(summary) == notes_before


def test_closure_does_not_replace_existing_notes():
    workflow = build_workflow()
    summary = build_summary(workflow)

    notes = build_notes(workflow)
    summary.set_notes(notes)

    notes_before = note_signatures(summary)

    resolve_workflow(workflow)
    summary.set_closure(build_closure(workflow))

    assert note_signatures(summary) == notes_before


def test_closure_does_not_change_note_count():
    workflow = build_workflow()
    summary = build_summary(workflow)

    notes = build_notes(workflow)
    summary.set_notes(notes)

    resolve_workflow(workflow)
    count_before = len(summary.notes)

    summary.set_closure(build_closure(workflow))

    assert len(summary.notes) == count_before


def test_closure_does_not_change_note_text():
    workflow = build_workflow()
    summary = build_summary(workflow)

    notes = build_notes(workflow)
    summary.set_notes(notes)

    text_before = summary.notes[0].text

    resolve_workflow(workflow)
    closure = build_closure(workflow)

    summary.set_closure(closure)

    assert summary.notes[0].text == text_before


def test_closure_does_not_change_note_workflow_state():
    workflow = build_workflow()
    summary = build_summary(workflow)

    notes = TechnicianCaseNotes(workflow)
    note = notes.add_note(
        "Initial investigation note.",
    )
    summary.set_notes(notes)

    workflow_state_before = summary.notes[0].workflow_state

    resolve_workflow(workflow)
    summary.set_closure(build_closure(workflow))

    assert summary.notes[0].workflow_state is workflow_state_before
    assert note.workflow_state is workflow_state_before


def test_closure_does_not_change_note_identity():
    workflow = build_workflow()
    summary = build_summary(workflow)

    notes = build_notes(workflow)
    summary.set_notes(notes)

    note = summary.notes[0]

    resolve_workflow(workflow)
    closure = build_closure(workflow)
    summary.set_closure(closure)

    assert summary.notes[0].note_id == note.note_id
    assert closure is not note


def test_closure_does_not_change_summary_identity():
    workflow = build_workflow()
    summary = build_summary(workflow)

    notes = build_notes(workflow)
    summary.set_notes(notes)

    summary_before = summary

    resolve_workflow(workflow)
    summary.set_closure(build_closure(workflow))

    assert summary is summary_before


def test_closure_does_not_change_workflow_identity():
    workflow = build_workflow()
    summary = build_summary(workflow)

    notes = build_notes(workflow)
    summary.set_notes(notes)

    workflow_id_before = workflow.workflow_id

    resolve_workflow(workflow)
    closure = build_closure(workflow)
    summary.set_closure(closure)

    assert workflow.workflow_id == workflow_id_before
    assert closure.workflow is workflow
    assert summary.workflow is workflow


def test_closure_does_not_change_notes_after_reopen():
    workflow = build_workflow()
    summary = build_summary(workflow)

    notes = build_notes(workflow)
    summary.set_notes(notes)

    resolve_workflow(workflow)
    summary.set_closure(build_closure(workflow))

    notes_before_reopen = note_signatures(summary)

    workflow.reopen()

    assert note_signatures(summary) == notes_before_reopen
    assert len(summary.notes) == 1


def test_multiple_closures_do_not_duplicate_notes():
    workflow = build_workflow()
    summary = build_summary(workflow)

    notes = build_notes(workflow)
    summary.set_notes(notes)

    resolve_workflow(workflow)

    first_closure = build_closure(workflow)
    summary.set_closure(first_closure)

    notes_before = note_signatures(summary)

    workflow.reopen()

    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    second_closure = build_closure(
        workflow,
        technician="Second Technician",
    )
    summary.set_closure(second_closure)

    assert first_closure is not second_closure
    assert note_signatures(summary) == notes_before
    assert len(summary.notes) == 1


def test_closure_does_not_become_note():
    workflow = build_workflow()
    summary = build_summary(workflow)

    notes = build_notes(workflow)
    summary.set_notes(notes)

    resolve_workflow(workflow)
    closure = build_closure(workflow)
    summary.set_closure(closure)

    assert closure not in summary.notes


def test_closure_reason_does_not_replace_note_text():
    workflow = build_workflow()
    summary = build_summary(workflow)

    notes = TechnicianCaseNotes(workflow)
    notes.add_note("Original technician investigation note.")
    summary.set_notes(notes)

    resolve_workflow(workflow)

    closure = TechnicianCaseClosure(
        workflow=workflow,
        technician="Test Technician",
        reason="Issue resolved and verified.",
    )
    summary.set_closure(closure)

    assert summary.notes[0].text == "Original technician investigation note."
    assert summary.notes[0].text != closure.reason


def test_notes_do_not_create_closure():
    workflow = build_workflow()
    summary = build_summary(workflow)

    notes = build_notes(workflow)
    summary.set_notes(notes)

    assert summary.closure is None
    assert workflow.state.value == "OPEN"


def test_replacing_closure_preserves_notes():
    workflow = build_workflow()
    summary = build_summary(workflow)

    notes = build_notes(workflow)
    summary.set_notes(notes)

    resolve_workflow(workflow)

    first_closure = build_closure(workflow)
    summary.set_closure(first_closure)

    notes_before = note_signatures(summary)

    second_closure = TechnicianCaseClosure(
        workflow=workflow,
        technician="Second Technician",
        reason="Verified again after follow-up.",
    )
    summary.set_closure(second_closure)

    assert summary.closure is second_closure
    assert summary.closure is not first_closure
    assert note_signatures(summary) == notes_before
    assert len(summary.notes) == 1