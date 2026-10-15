from engine.case_handoff import CaseHandoff
from engine.case_ownership import CaseOwnership
from engine.diagnostic_case import DiagnosticCase
from engine.technician_identity import TechnicianIdentity
from engine.technician_workflow import TechnicianWorkflow


def create_case():
    return DiagnosticCase()


def create_technician(technician_id, name):
    return TechnicianIdentity(
        technician_id=technician_id,
        name=name,
    )


def create_ownership():
    case = create_case()
    owner = create_technician("TECH-001", "Alice")

    ownership = CaseOwnership(case, owner)

    return case, ownership


def test_handoff_creation():
    case, ownership = create_ownership()

    recipient = create_technician("TECH-002", "Bob")
    performed_by = ownership.owner

    handoff = CaseHandoff(
        ownership,
        recipient,
        performed_by,
        reason="Escalating to senior technician.",
    )

    assert handoff.case_id == case.case_id
    assert handoff.from_technician_id == "TECH-001"
    assert handoff.to_technician_id == "TECH-002"
    assert handoff.performed_by_id == "TECH-001"
    assert handoff.reason == "Escalating to senior technician."


def test_apply_transfers_case_ownership():
    case, ownership = create_ownership()

    recipient = create_technician("TECH-002", "Bob")

    handoff = CaseHandoff(
        ownership,
        recipient,
        ownership.owner,
        reason="Specialist required.",
    )

    handoff.apply()

    assert ownership.is_owned
    assert ownership.owner_id == "TECH-002"
    assert ownership.case_id == case.case_id


def test_handoff_preserves_original_sender():
    case, ownership = create_ownership()

    original_owner = ownership.owner
    recipient = create_technician("TECH-002", "Bob")

    handoff = CaseHandoff(
        ownership,
        recipient,
        original_owner,
    )

    handoff.apply()

    assert handoff.from_technician_id == "TECH-001"
    assert ownership.owner_id == "TECH-002"


def test_handoff_requires_existing_owner():
    case = create_case()
    ownership = CaseOwnership(case)

    recipient = create_technician("TECH-002", "Bob")
    performed_by = create_technician("TECH-003", "Carol")

    try:
        CaseHandoff(
            ownership,
            recipient,
            performed_by,
        )
        assert False
    except ValueError:
        pass


def test_handoff_rejects_same_owner():
    case, ownership = create_ownership()

    try:
        CaseHandoff(
            ownership,
            ownership.owner,
            ownership.owner,
        )
        assert False
    except ValueError:
        pass


def test_invalid_reason_is_rejected():
    case, ownership = create_ownership()

    recipient = create_technician("TECH-002", "Bob")

    try:
        CaseHandoff(
            ownership,
            recipient,
            ownership.owner,
            reason="   ",
        )
        assert False
    except ValueError:
        pass


def test_projection_contains_handoff_data():
    case, ownership = create_ownership()

    recipient = create_technician("TECH-002", "Bob")

    handoff = CaseHandoff(
        ownership,
        recipient,
        ownership.owner,
        reason="Shift change.",
    )

    projection = handoff.projection()

    assert projection["case_id"] == case.case_id
    assert projection["from_technician_id"] == "TECH-001"
    assert projection["to_technician_id"] == "TECH-002"
    assert projection["performed_by_id"] == "TECH-001"
    assert projection["reason"] == "Shift change."
    assert projection["created_at"]


def test_projection_is_defensive():
    case, ownership = create_ownership()

    recipient = create_technician("TECH-002", "Bob")

    handoff = CaseHandoff(
        ownership,
        recipient,
        ownership.owner,
    )

    projection = handoff.projection()
    projection["to_technician"]["name"] = "Changed"

    assert handoff.to_technician.name == "Bob"


def test_handoff_does_not_change_workflow_state():
    case, ownership = create_ownership()

    workflow = TechnicianWorkflow(case)

    recipient = create_technician("TECH-002", "Bob")

    handoff = CaseHandoff(
        ownership,
        recipient,
        ownership.owner,
    )

    initial_state = workflow.state

    handoff.apply()

    assert workflow.state == initial_state
