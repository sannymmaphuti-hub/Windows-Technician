import pytest

from engine.case_ownership import CaseOwnership
from engine.diagnostic_case import DiagnosticCase
from engine.technician_identity import TechnicianIdentity


def create_case():
    case = DiagnosticCase()
    case.machine_id = "M001"
    case.hostname = "PC-001"
    return case


def create_technician(
    technician_id="T001",
    name="Alice",
):
    return TechnicianIdentity(
        technician_id,
        name,
    )


def test_ownership_requires_diagnostic_case():
    with pytest.raises(ValueError):
        CaseOwnership(object())


def test_ownership_requires_valid_owner():
    case = create_case()

    with pytest.raises(ValueError):
        CaseOwnership(case, owner=object())


def test_ownership_starts_unassigned():
    case = create_case()

    ownership = CaseOwnership(case)

    assert ownership.case is case
    assert ownership.case_id == case.case_id
    assert ownership.owner is None
    assert ownership.owner_id is None
    assert ownership.is_owned is False


def test_assign_sets_owner():
    case = create_case()
    technician = create_technician()

    ownership = CaseOwnership(case)

    ownership.assign(technician)

    assert ownership.owner is technician
    assert ownership.owner_id == "T001"
    assert ownership.is_owned is True


def test_assign_replaces_existing_owner():
    case = create_case()
    first = create_technician("T001", "Alice")
    second = create_technician("T002", "Bob")

    ownership = CaseOwnership(case, first)

    ownership.assign(second)

    assert ownership.owner is second
    assert ownership.owner_id == "T002"


def test_clear_removes_owner():
    case = create_case()
    technician = create_technician()

    ownership = CaseOwnership(case, technician)

    ownership.clear()

    assert ownership.owner is None
    assert ownership.owner_id is None
    assert ownership.is_owned is False


def test_projection_has_canonical_surface():
    case = create_case()
    technician = create_technician()

    ownership = CaseOwnership(case, technician)

    projection = ownership.projection()

    assert set(projection) == {
        "case_id",
        "owner",
        "owner_id",
        "is_owned",
    }

    assert projection["case_id"] == case.case_id
    assert projection["owner_id"] == "T001"
    assert projection["is_owned"] is True


def test_projection_is_defensive():
    case = create_case()
    technician = create_technician()

    ownership = CaseOwnership(case, technician)

    projection = ownership.projection()
    projection["owner"]["name"] = "MUTATED"
    projection["owner_id"] = "MUTATED"

    current = ownership.projection()

    assert current["owner"]["name"] == "Alice"
    assert current["owner_id"] == "T001"


def test_ownership_does_not_mutate_canonical_case():
    case = create_case()
    original_case_id = case.case_id
    original_machine_id = case.machine_id
    original_hostname = case.hostname

    ownership = CaseOwnership(
        case,
        create_technician(),
    )

    ownership.assign(
        create_technician("T002", "Bob")
    )

    assert case.case_id == original_case_id
    assert case.machine_id == original_machine_id
    assert case.hostname == original_hostname


def test_ownership_does_not_expose_execution_controls():
    case = create_case()

    ownership = CaseOwnership(case)

    assert not hasattr(ownership, "authorize_remediation")
    assert not hasattr(ownership, "execute_remediation")
    assert not hasattr(ownership, "verify_remediation")


def test_repr_is_safe():
    case = create_case()
    ownership = CaseOwnership(
        case,
        create_technician(),
    )

    representation = repr(ownership)

    assert case.case_id in representation
    assert "T001" in representation
    assert "authorize_remediation" not in representation
    assert "execute_remediation" not in representation
    assert "verify_remediation" not in representation
