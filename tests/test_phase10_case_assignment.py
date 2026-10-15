import pytest

from engine.case_assignment import CaseAssignment
from engine.case_ownership import CaseOwnership
from engine.diagnostic_case import DiagnosticCase
from engine.technician_identity import TechnicianIdentity


def create_case():
    case = DiagnosticCase()
    case.machine_id = "M001"
    case.hostname = "PC-001"
    return case


def technician(
    technician_id,
    name,
):
    return TechnicianIdentity(
        technician_id,
        name,
    )


def test_assignment_requires_case():
    with pytest.raises(ValueError):
        CaseAssignment(
            object(),
            technician("T002", "Bob"),
            technician("T001", "Alice"),
        )


def test_assignment_requires_destination_technician():
    with pytest.raises(ValueError):
        CaseAssignment(
            create_case(),
            object(),
            technician("T001", "Alice"),
        )


def test_assignment_requires_assigning_technician():
    with pytest.raises(ValueError):
        CaseAssignment(
            create_case(),
            technician("T002", "Bob"),
            object(),
        )


def test_assignment_rejects_non_string_reason():
    with pytest.raises(ValueError):
        CaseAssignment(
            create_case(),
            technician("T002", "Bob"),
            technician("T001", "Alice"),
            reason=123,
        )


def test_assignment_preserves_identity():
    case = create_case()
    destination = technician("T002", "Bob")
    assigner = technician("T001", "Alice")

    assignment = CaseAssignment(
        case,
        destination,
        assigner,
        reason="Specialist review",
    )

    assert assignment.case is case
    assert assignment.case_id == case.case_id
    assert assignment.assigned_to is destination
    assert assignment.assigned_by is assigner
    assert assignment.assigned_to_id == "T002"
    assert assignment.assigned_by_id == "T001"
    assert assignment.reason == "Specialist review"


def test_assignment_applies_to_matching_ownership():
    case = create_case()
    destination = technician("T002", "Bob")
    assigner = technician("T001", "Alice")

    ownership = CaseOwnership(case)

    assignment = CaseAssignment(
        case,
        destination,
        assigner,
    )

    assignment.apply(ownership)

    assert ownership.case is case
    assert ownership.owner is destination
    assert ownership.owner_id == "T002"


def test_assignment_rejects_different_case_ownership():
    case = create_case()
    other_case = create_case()

    ownership = CaseOwnership(other_case)

    assignment = CaseAssignment(
        case,
        technician("T002", "Bob"),
        technician("T001", "Alice"),
    )

    with pytest.raises(ValueError):
        assignment.apply(ownership)


def test_assignment_projection_has_canonical_surface():
    case = create_case()

    assignment = CaseAssignment(
        case,
        technician("T002", "Bob"),
        technician("T001", "Alice"),
        reason="Escalation",
    )

    projection = assignment.projection()

    assert set(projection) == {
        "case_id",
        "assigned_to",
        "assigned_to_id",
        "assigned_by",
        "assigned_by_id",
        "reason",
    }

    assert projection["case_id"] == case.case_id
    assert projection["assigned_to_id"] == "T002"
    assert projection["assigned_by_id"] == "T001"
    assert projection["reason"] == "Escalation"


def test_assignment_projection_is_defensive():
    assignment = CaseAssignment(
        create_case(),
        technician("T002", "Bob"),
        technician("T001", "Alice"),
    )

    projection = assignment.projection()
    projection["assigned_to"]["name"] = "MUTATED"
    projection["assigned_by"]["name"] = "MUTATED"

    current = assignment.projection()

    assert current["assigned_to"]["name"] == "Bob"
    assert current["assigned_by"]["name"] == "Alice"


def test_assignment_does_not_mutate_case():
    case = create_case()
    original_case_id = case.case_id
    original_machine_id = case.machine_id
    original_hostname = case.hostname

    assignment = CaseAssignment(
        case,
        technician("T002", "Bob"),
        technician("T001", "Alice"),
    )

    ownership = CaseOwnership(case)
    assignment.apply(ownership)

    assert case.case_id == original_case_id
    assert case.machine_id == original_machine_id
    assert case.hostname == original_hostname


def test_assignment_has_no_remediation_controls():
    assignment = CaseAssignment(
        create_case(),
        technician("T002", "Bob"),
        technician("T001", "Alice"),
    )

    assert not hasattr(assignment, "authorize_remediation")
    assert not hasattr(assignment, "execute_remediation")
    assert not hasattr(assignment, "verify_remediation")


def test_assignment_repr_is_safe():
    assignment = CaseAssignment(
        create_case(),
        technician("T002", "Bob"),
        technician("T001", "Alice"),
    )

    representation = repr(assignment)

    assert "T002" in representation
    assert "T001" in representation
    assert "authorize_remediation" not in representation
    assert "execute_remediation" not in representation
    assert "verify_remediation" not in representation
