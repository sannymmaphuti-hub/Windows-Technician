import pytest

from engine.case_access_policy import CaseAccessPolicy
from engine.case_ownership import CaseOwnership
from engine.diagnostic_case import DiagnosticCase
from engine.operation_authorization_policy import OperationAuthorizationPolicy
from engine.security_audit_event import SecurityAuditEventFactory
from engine.security_audit_history import SecurityAuditHistory
from engine.technician_identity import TechnicianIdentity
from engine.technician_permissions import (
    TechnicianPermission,
    TechnicianPermissions,
)
from engine.technician_role_policy import TechnicianRolePolicy


def make_technician(technician_id="TECH-001", role="TECHNICIAN"):
    return TechnicianIdentity(technician_id, technician_id, role)


def make_case():
    case = DiagnosticCase()
    case.machine_id = "MACHINE-001"
    case.hostname = "TEST-PC"
    return case


def make_event():
    return SecurityAuditEventFactory().create(
        event_type="SECURITY_DECISION",
        actor_id="TECH-001",
        resource_id="CASE-001",
        action="VIEW_CASE",
        outcome="ALLOWED",
        reason="CASE_ACCESS_GRANTED",
    )


def test_unknown_permission_never_grants_access():
    permissions = TechnicianPermissions([TechnicianPermission.VIEW_CASE])

    assert not permissions.allows("EXECUTE_EVERYTHING")
    assert not permissions.allows("")


def test_unknown_operation_is_denied():
    decision = OperationAuthorizationPolicy().evaluate(
        make_technician(),
        "EXECUTE_ARBITRARY_CODE",
    )

    assert not decision.allowed
    assert decision.reason == "UNSUPPORTED_OPERATION"


def test_invalid_identity_is_denied():
    decision = OperationAuthorizationPolicy().evaluate(
        object(),
        "VIEW_CASE",
    )

    assert not decision.allowed


def test_case_access_rejects_ownership_for_another_case():
    case = make_case()
    other_case = make_case()
    other_case.case_id = "OTHER-CASE"

    technician = make_technician()
    ownership = CaseOwnership(other_case, technician)

    decision = CaseAccessPolicy().evaluate(
        technician,
        case,
        "VIEW_CASE",
        ownership,
    )

    assert not decision.allowed
    assert decision.reason == "CASE_OWNERSHIP_MISMATCH"


def test_case_access_denies_non_owner():
    case = make_case()
    owner = make_technician("TECH-001")
    other = make_technician("TECH-002")
    ownership = CaseOwnership(case, owner)

    decision = CaseAccessPolicy().evaluate(
        other,
        case,
        "VIEW_CASE",
        ownership,
    )

    assert not decision.allowed


def test_duplicate_audit_event_is_rejected():
    history = SecurityAuditHistory()
    event = make_event()

    history.append(event)

    with pytest.raises(ValueError, match="Duplicate security audit event ID"):
        history.append(event)


def test_invalid_audit_event_is_rejected():
    history = SecurityAuditHistory()

    with pytest.raises(TypeError):
        history.append(object())


def test_unknown_role_fails_closed():
    technician = make_technician()
    technician.role = "SUPERUSER"

    assert not TechnicianRolePolicy().allows(
        technician,
        TechnicianPermission.VIEW_CASE,
    )


def test_remediation_permissions_are_not_granted_by_default_roles():
    policy = TechnicianRolePolicy()

    for role in (
        "TECHNICIAN",
        "SENIOR_TECHNICIAN",
        "SUPERVISOR",
        "ADMINISTRATOR",
    ):
        technician = make_technician(role=role)

        assert not policy.allows(
            technician,
            TechnicianPermission.AUTHORIZE_REMEDIATION,
        )
        assert not policy.allows(
            technician,
            TechnicianPermission.EXECUTE_REMEDIATION,
        )


def test_invalid_case_access_operation_fails_closed():
    decision = CaseAccessPolicy().evaluate(
        make_technician(),
        make_case(),
        None,
    )

    assert not decision.allowed
    assert decision.reason == "INVALID_OPERATION"


def test_audit_factory_rejects_invalid_outcome():
    with pytest.raises(ValueError, match="Unsupported security audit outcome"):
        SecurityAuditEventFactory().create(
            event_type="SECURITY_DECISION",
            actor_id="TECH-001",
            resource_id="CASE-001",
            action="VIEW_CASE",
            outcome="MAYBE",
            reason="UNKNOWN",
        )


def test_permission_policy_rejects_invalid_permission_types():
    with pytest.raises(TypeError):
        TechnicianPermissions([object()])


def test_denied_decisions_do_not_change_case_identity():
    case = make_case()
    original_case_id = case.case_id

    decision = CaseAccessPolicy().evaluate(
        make_technician(),
        case,
        "DELETE_CASE",
    )

    assert not decision.allowed
    assert case.case_id == original_case_id
