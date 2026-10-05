from engine.diagnostic_case import DiagnosticCase
from engine.technician_notes import TechnicianNotes


def create_case():
    return DiagnosticCase()

def test_notes_requires_diagnostic_case():
    try:
        TechnicianNotes(None)
    except ValueError:
        return

    raise AssertionError(
        "TechnicianNotes should reject None."
    )


def test_notes_requires_diagnostic_case_instance():
    try:
        TechnicianNotes(object())
    except ValueError:
        return

    raise AssertionError(
        "TechnicianNotes should require a DiagnosticCase."
    )


def test_notes_exposes_case():
    case = create_case()

    notes = TechnicianNotes(case)

    assert notes.case is case


def test_notes_exposes_case_id():
    case = create_case()

    notes = TechnicianNotes(case)

    assert notes.case_id == case.case_id


def test_notes_start_empty():
    case = create_case()

    notes = TechnicianNotes(case)

    assert notes.notes == []


def test_notes_count_starts_at_zero():
    case = create_case()

    notes = TechnicianNotes(case)

    assert notes.note_count == 0


def test_add_note_accepts_text():
    case = create_case()

    notes = TechnicianNotes(case)

    notes.add_note("Checked network configuration.")

    assert notes.note_count == 1


def test_add_note_preserves_text():
    case = create_case()

    notes = TechnicianNotes(case)

    notes.add_note("Checked network configuration.")

    assert notes.notes == ["Checked network configuration."]


def test_multiple_notes_preserve_order():
    case = create_case()

    notes = TechnicianNotes(case)

    notes.add_note("Checked network configuration.")
    notes.add_note("Restarted network adapter.")
    notes.add_note("Verified connectivity.")

    assert notes.notes == [
        "Checked network configuration.",
        "Restarted network adapter.",
        "Verified connectivity.",
    ]


def test_note_count_tracks_notes():
    case = create_case()

    notes = TechnicianNotes(case)

    notes.add_note("First note.")
    notes.add_note("Second note.")

    assert notes.note_count == 2


def test_add_note_rejects_none():
    case = create_case()

    notes = TechnicianNotes(case)

    try:
        notes.add_note(None)
    except ValueError:
        return

    raise AssertionError(
        "TechnicianNotes should reject None notes."
    )


def test_add_note_rejects_non_string():
    case = create_case()

    notes = TechnicianNotes(case)

    try:
        notes.add_note(123)
    except ValueError:
        return

    raise AssertionError(
        "TechnicianNotes should require string notes."
    )


def test_empty_note_is_rejected():
    case = create_case()

    notes = TechnicianNotes(case)

    try:
        notes.add_note("")
    except ValueError:
        return

    raise AssertionError(
        "TechnicianNotes should reject empty notes."
    )


def test_whitespace_only_note_is_rejected():
    case = create_case()

    notes = TechnicianNotes(case)

    try:
        notes.add_note("   ")
    except ValueError:
        return

    raise AssertionError(
        "TechnicianNotes should reject whitespace-only notes."
    )


def test_note_text_is_preserved_without_case_mutation():
    case = create_case()

    notes = TechnicianNotes(case)

    notes.add_note("Technician observation.")

    assert case.case_id == notes.case_id
    assert notes.notes == ["Technician observation."]


def test_notes_do_not_change_case_lifecycle():
    case = create_case()

    original_state = case.lifecycle_state

    notes = TechnicianNotes(case)
    notes.add_note("Technician observation.")

    assert case.lifecycle_state == original_state


def test_notes_do_not_change_case_status():
    case = create_case()

    original_status = case.status

    notes = TechnicianNotes(case)
    notes.add_note("Technician observation.")

    assert case.status == original_status


def test_notes_do_not_authorize_remediation():
    case = create_case()

    notes = TechnicianNotes(case)
    notes.add_note("Technician observation.")

    assert not hasattr(notes, "authorize")


def test_notes_do_not_execute_remediation():
    case = create_case()

    notes = TechnicianNotes(case)
    notes.add_note("Technician observation.")

    assert not hasattr(notes, "execute")


def test_notes_are_operational_context_only():
    case = create_case()

    notes = TechnicianNotes(case)
    notes.add_note("Customer reports intermittent connectivity.")

    assert notes.case is case
    assert notes.note_count == 1
    assert notes.notes[0] == (
        "Customer reports intermittent connectivity."
    )