import pytest

from engine.technician_identity import TechnicianIdentity


def test_identity_requires_technician_id():
    with pytest.raises(ValueError):
        TechnicianIdentity("", "Alice")


def test_identity_requires_name():
    with pytest.raises(ValueError):
        TechnicianIdentity("T001", "")


def test_identity_normalizes_role():
    technician = TechnicianIdentity(
        "T001",
        "Alice",
        "technician",
    )

    assert technician.role == "TECHNICIAN"


def test_identity_rejects_unknown_role():
    with pytest.raises(ValueError):
        TechnicianIdentity(
            "T001",
            "Alice",
            "UNKNOWN_ROLE",
        )


def test_identity_preserves_identity_fields():
    technician = TechnicianIdentity(
        "T001",
        "Alice",
        "SENIOR_TECHNICIAN",
    )

    assert technician.technician_id == "T001"
    assert technician.name == "Alice"
    assert technician.role == "SENIOR_TECHNICIAN"


def test_identity_projection_has_canonical_surface():
    technician = TechnicianIdentity(
        "T001",
        "Alice",
    )

    projection = technician.projection()

    assert set(projection) == {
        "technician_id",
        "name",
        "role",
    }


def test_identity_projection_is_defensive():
    technician = TechnicianIdentity(
        "T001",
        "Alice",
    )

    projection = technician.projection()
    projection["name"] = "MUTATED"

    assert technician.name == "Alice"
    assert technician.projection()["name"] == "Alice"


def test_identity_does_not_expose_case_or_remediation_controls():
    technician = TechnicianIdentity(
        "T001",
        "Alice",
    )

    assert not hasattr(technician, "case")
    assert not hasattr(technician, "workflow")
    assert not hasattr(technician, "authorize_remediation")
    assert not hasattr(technician, "execute_remediation")
    assert not hasattr(technician, "verify_remediation")


def test_identity_repr_contains_identity_only():
    technician = TechnicianIdentity(
        "T001",
        "Alice",
    )

    representation = repr(technician)

    assert "T001" in representation
    assert "Alice" in representation
    assert "authorize_remediation" not in representation
    assert "execute_remediation" not in representation
    assert "verify_remediation" not in representation
