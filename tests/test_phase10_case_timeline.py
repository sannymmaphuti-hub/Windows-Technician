from datetime import timedelta

from engine.case_handoff import CaseHandoff
from engine.case_note import CaseNote
from engine.case_ownership import CaseOwnership
from engine.case_timeline import CaseTimeline
from engine.diagnostic_case import DiagnosticCase
from engine.technician_identity import TechnicianIdentity


def create_case():
    return DiagnosticCase()


def create_technician(technician_id, name):
    return TechnicianIdentity(
        technician_id=technician_id,
        name=name,
    )


def create_ownership(case):
    owner = create_technician("TECH-001", "Alice")
    return CaseOwnership(case, owner)


def test_timeline_creation():
    case = create_case()

    timeline = CaseTimeline(case)

    assert timeline.case_id == case.case_id
    assert timeline.entries == ()
    assert timeline.projection()["entry_count"] == 0


def test_note_can_be_added():
    case = create_case()
    timeline = CaseTimeline(case)

    note = CaseNote(
        case,
        create_technician("TECH-001", "Alice"),
        "Initial investigation started.",
    )

    timeline.add_note(note)

    assert timeline.entries == (note,)
    assert timeline.projection()["entry_count"] == 1


def test_handoff_can_be_added():
    case = create_case()
    ownership = create_ownership(case)
    timeline = CaseTimeline(case)

    recipient = create_technician("TECH-002", "Bob")

    handoff = CaseHandoff(
        ownership,
        recipient,
        ownership.owner,
        reason="Specialist required.",
    )

    timeline.add_handoff(handoff)

    assert timeline.entries == (handoff,)
    assert timeline.projection()["entry_count"] == 1


def test_entries_are_chronological():
    case = create_case()
    timeline = CaseTimeline(case)

    technician = create_technician("TECH-001", "Alice")

    first = CaseNote(
        case,
        technician,
        "First activity.",
    )

    second = CaseNote(
        case,
        technician,
        "Second activity.",
    )

    second.created_at = first.created_at + timedelta(seconds=5)

    timeline.add_note(second)
    timeline.add_note(first)

    entries = timeline.chronological_entries()

    assert entries == (first, second)


def test_mixed_activity_is_chronological():
    case = create_case()
    ownership = create_ownership(case)
    timeline = CaseTimeline(case)

    owner = ownership.owner
    recipient = create_technician("TECH-002", "Bob")

    note = CaseNote(
        case,
        owner,
        "Investigation started.",
    )

    handoff = CaseHandoff(
        ownership,
        recipient,
        owner,
        reason="Escalation.",
    )

    handoff.created_at = note.created_at + timedelta(seconds=10)

    timeline.add_handoff(handoff)
    timeline.add_note(note)

    entries = timeline.chronological_entries()

    assert entries[0] is note
    assert entries[1] is handoff


def test_wrong_case_note_is_rejected():
    case = create_case()
    other_case = create_case()

    timeline = CaseTimeline(case)

    note = CaseNote(
        other_case,
        create_technician("TECH-001", "Alice"),
        "Wrong case.",
    )

    try:
        timeline.add_note(note)
        assert False
    except ValueError:
        pass


def test_wrong_case_handoff_is_rejected():
    case = create_case()
    other_case = create_case()

    timeline = CaseTimeline(case)
    ownership = create_ownership(other_case)

    recipient = create_technician("TECH-002", "Bob")

    handoff = CaseHandoff(
        ownership,
        recipient,
        ownership.owner,
    )

    try:
        timeline.add_handoff(handoff)
        assert False
    except ValueError:
        pass


def test_entries_are_read_only():
    case = create_case()
    timeline = CaseTimeline(case)

    note = CaseNote(
        case,
        create_technician("TECH-001", "Alice"),
        "Activity.",
    )

    timeline.add_note(note)

    entries = timeline.entries

    try:
        entries.append(note)
        assert False
    except AttributeError:
        pass

    assert len(timeline.entries) == 1


def test_projection_contains_ordered_entries():
    case = create_case()
    timeline = CaseTimeline(case)

    technician = create_technician("TECH-001", "Alice")

    first = CaseNote(
        case,
        technician,
        "First.",
    )

    second = CaseNote(
        case,
        technician,
        "Second.",
        activity_type="STATUS_UPDATE",
    )

    second.created_at = first.created_at + timedelta(seconds=10)

    timeline.add_note(second)
    timeline.add_note(first)

    projection = timeline.projection()

    assert projection["case_id"] == case.case_id
    assert projection["entry_count"] == 2
    assert projection["entries"][0]["content"] == "First."
    assert projection["entries"][1]["content"] == "Second."


def test_projection_is_defensive():
    case = create_case()
    timeline = CaseTimeline(case)

    note = CaseNote(
        case,
        create_technician("TECH-001", "Alice"),
        "Original.",
    )

    timeline.add_note(note)

    projection = timeline.projection()
    projection["entries"][0]["content"] = "Modified."

    assert note.content == "Original."
