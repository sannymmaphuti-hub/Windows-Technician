import pytest

from engine.technician_case_notes import TechnicianCaseNotes
from engine.technician_workflow import (
    TechnicianWorkflow,
    WorkflowState,
)


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
def notes(workflow):
    return TechnicianCaseNotes(workflow)


def test_notes_requires_workflow():
    with pytest.raises(ValueError):
        TechnicianCaseNotes(None)


def test_notes_exposes_workflow(
    notes,
    workflow,
):
    assert notes.workflow is workflow


def test_notes_start_empty(notes):
    assert notes.notes == []


def test_add_note_preserves_text(notes):
    note = notes.add_note("Checked the customer's network connection.")

    assert note.text == "Checked the customer's network connection."


def test_add_note_has_unique_id(notes):
    first = notes.add_note("First note.")
    second = notes.add_note("Second note.")

    assert first.note_id != second.note_id


def test_add_note_has_utc_timestamp(notes):
    note = notes.add_note("Investigated system symptoms.")

    assert note.created_at.tzinfo is not None
    assert note.created_at.utcoffset().total_seconds() == 0


def test_notes_preserve_chronological_order(notes):
    first = notes.add_note("First note.")
    second = notes.add_note("Second note.")

    assert notes.notes == [first, second]


def test_note_records_workflow_state(
    notes,
    workflow,
):
    note = notes.add_note("Initial investigation completed.")

    assert note.workflow_state is WorkflowState.INVESTIGATING


def test_note_can_be_associated_with_explicit_state(
    notes,
):
    note = notes.add_note(
        "Remediation requires technician review.",
        workflow_state=WorkflowState.ACTION_REQUIRED,
    )

    assert note.workflow_state is WorkflowState.ACTION_REQUIRED


def test_empty_note_is_rejected(notes):
    with pytest.raises(ValueError):
        notes.add_note("")


def test_whitespace_only_note_is_rejected(notes):
    with pytest.raises(ValueError):
        notes.add_note("   ")


def test_non_string_note_is_rejected(notes):
    with pytest.raises(ValueError):
        notes.add_note(123)


def test_notes_collection_is_read_only(
    notes,
):
    note = notes.add_note("Keep this note.")

    returned_notes = notes.notes
    returned_notes.clear()

    assert notes.notes == [note]


def test_multiple_notes_are_preserved(notes):
    first = notes.add_note("Reviewed evidence.")
    second = notes.add_note("Reviewed findings.")
    third = notes.add_note("Prepared remediation.")

    assert notes.notes == [first, second, third]


def test_notes_do_not_change_workflow_state(
    notes,
    workflow,
):
    state_before = workflow.state

    notes.add_note("Documenting current investigation.")

    assert workflow.state is state_before


def test_notes_do_not_mutate_case(
    notes,
    workflow,
):
    case = workflow.case
    original_findings = list(case.findings)
    original_root_causes = list(case.root_causes)
    original_recommendations = list(case.recommendations)

    notes.add_note("Documenting diagnostic context.")

    assert case.findings == original_findings
    assert case.root_causes == original_root_causes
    assert case.recommendations == original_recommendations