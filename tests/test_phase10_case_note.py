from engine.case_note import CaseNote
from engine.diagnostic_case import DiagnosticCase
from engine.technician_identity import TechnicianIdentity


def create_case():
    return DiagnosticCase()


def create_technician():
    return TechnicianIdentity(
        technician_id="TECH-001",
        name="Sanny",
    )


def test_note_creation():
    note = CaseNote(
        create_case(),
        create_technician(),
        "Investigating elevated memory usage.",
    )

    assert note.note_id
    assert note.case_id == note.case.case_id
    assert note.technician_id == "TECH-001"
    assert note.content == "Investigating elevated memory usage."
    assert note.activity_type == "NOTE"
    assert note.created_at is not None


def test_activity_type_is_normalized():
    note = CaseNote(
        create_case(),
        create_technician(),
        "Diagnostic update.",
        activity_type="status_update",
    )

    assert note.activity_type == "STATUS_UPDATE"


def test_supported_activity_types():
    for activity_type in CaseNote.VALID_ACTIVITY_TYPES:
        note = CaseNote(
            create_case(),
            create_technician(),
            "Activity recorded.",
            activity_type=activity_type,
        )

        assert note.activity_type == activity_type


def test_invalid_case_is_rejected():
    try:
        CaseNote(
            object(),
            create_technician(),
            "Invalid case.",
        )
        assert False
    except ValueError:
        pass


def test_invalid_technician_is_rejected():
    try:
        CaseNote(
            create_case(),
            object(),
            "Invalid technician.",
        )
        assert False
    except ValueError:
        pass


def test_empty_content_is_rejected():
    try:
        CaseNote(
            create_case(),
            create_technician(),
            "   ",
        )
        assert False
    except ValueError:
        pass


def test_invalid_activity_type_is_rejected():
    try:
        CaseNote(
            create_case(),
            create_technician(),
            "Invalid activity.",
            activity_type="REMIDIATION",
        )
        assert False
    except ValueError:
        pass


def test_projection_contains_collaboration_data():
    note = CaseNote(
        create_case(),
        create_technician(),
        "Customer was informed.",
        activity_type="CUSTOMER_UPDATE",
    )

    projection = note.projection()

    assert projection["note_id"] == note.note_id
    assert projection["case_id"] == note.case_id
    assert projection["technician_id"] == "TECH-001"
    assert projection["technician_name"] == "Sanny"
    assert projection["activity_type"] == "CUSTOMER_UPDATE"
    assert projection["content"] == "Customer was informed."
    assert projection["created_at"]


def test_projection_is_defensive():
    note = CaseNote(
        create_case(),
        create_technician(),
        "Original note.",
    )

    projection = note.projection()
    projection["content"] = "Modified externally."

    assert note.content == "Original note."


def test_note_does_not_change_workflow_state():
    case = create_case()
    technician = create_technician()

    note = CaseNote(
        case,
        technician,
        "Observation recorded.",
    )

    assert case.lifecycle_state == "OPEN"
    assert note.case.lifecycle_state == "OPEN"
