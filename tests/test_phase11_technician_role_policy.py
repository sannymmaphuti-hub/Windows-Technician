from engine.technician_identity import TechnicianIdentity
from engine.technician_permissions import TechnicianPermission
from engine.technician_role_policy import TechnicianRolePolicy


def make_technician(role):
    return TechnicianIdentity(
        technician_id="TECH-001",
        name="Test Technician",
        role=role,
    )


def test_standard_technician_can_view_cases_and_add_notes():
    policy = TechnicianRolePolicy()
    technician = make_technician("TECHNICIAN")

    assert policy.allows(technician, TechnicianPermission.VIEW_CASE)
    assert policy.allows(technician, TechnicianPermission.ADD_CASE_NOTE)


def test_standard_technician_cannot_assign_cases():
    policy = TechnicianRolePolicy()

    assert not policy.allows(
        make_technician("TECHNICIAN"),
        TechnicianPermission.ASSIGN_CASE,
    )


def test_senior_technician_can_assign_cases():
    policy = TechnicianRolePolicy()

    assert policy.allows(
        make_technician("SENIOR_TECHNICIAN"),
        TechnicianPermission.ASSIGN_CASE,
    )


def test_supervisor_can_view_audit_history():
    policy = TechnicianRolePolicy()

    assert policy.allows(
        make_technician("SUPERVISOR"),
        TechnicianPermission.VIEW_AUDIT_HISTORY,
    )


def test_administrator_can_manage_security_policy():
    policy = TechnicianRolePolicy()

    assert policy.allows(
        make_technician("ADMINISTRATOR"),
        TechnicianPermission.MANAGE_SECURITY_POLICY,
    )


def test_role_does_not_implicitly_authorize_remediation():
    policy = TechnicianRolePolicy()

    for role in (
        "TECHNICIAN",
        "SENIOR_TECHNICIAN",
        "SUPERVISOR",
        "ADMINISTRATOR",
    ):
        technician = make_technician(role)

        assert not policy.allows(
            technician,
            TechnicianPermission.EXECUTE_REMEDIATION,
        )
        assert not policy.allows(
            technician,
            TechnicianPermission.AUTHORIZE_REMEDIATION,
        )


def test_unknown_role_policy_lookup_fails_closed():
    policy = TechnicianRolePolicy()
    technician = make_technician("TECHNICIAN")

    # Simulate an identity whose role is no longer recognized.
    technician.role = "UNKNOWN_ROLE"

    assert not policy.allows(
        technician,
        TechnicianPermission.VIEW_CASE,
    )


def test_policy_rejects_invalid_identity():
    import pytest

    policy = TechnicianRolePolicy()

    with pytest.raises(TypeError):
        policy.permissions_for("TECH-001")


def test_policy_projection_is_defensive():
    policy = TechnicianRolePolicy()

    first = policy.projection()
    first["TECHNICIAN"].append("EXECUTE_REMEDIATION")

    assert "EXECUTE_REMEDIATION" not in policy.projection()["TECHNICIAN"]


def test_role_policy_contains_all_supported_identity_roles():
    policy = TechnicianRolePolicy()

    assert set(policy.projection()) == {
        "TECHNICIAN",
        "SENIOR_TECHNICIAN",
        "ADMINISTRATOR",
        "SUPERVISOR",
    }
