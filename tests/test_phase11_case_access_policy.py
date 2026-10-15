import pytest

from engine.case_access_policy import CaseAccessPolicy
from engine.case_ownership import CaseOwnership
from engine.diagnostic_case import DiagnosticCase
from engine.technician_identity import TechnicianIdentity


def make_technician(technician_id="TECH-001", role="TECHNICIAN"):
    return TechnicianIdentity(technician_id, technician_id, role)


def make_case():
    case = DiagnosticCase()
    case.machine_id = "MACHINE-001"
    case.hostname = "TEST-PC"
    return case


def test_allowed_role_can_view_case():
    decision = CaseAccessPolicy().evaluate(
        make_technician(), make_case(), "VIEW_CASE"
    )

    assert decision.allowed
    assert decision.reason == "CASE_ACCESS_GRANTED"


def test_unpermitted_role_is_denied():
    decision = CaseAccessPolicy().evaluate(
        make_technician(), make_case(), "ASSIGN_CASE"
    )

    assert not decision.allowed
    assert decision.reason == "PERMISSION_DENIED"


def test_unknown_case_operation_is_denied():
    decision = CaseAccessPolicy().evaluate(
        make_technician(), make_case(), "DELETE_CASE"
    )

    assert not decision.allowed
    assert decision.reason == "UNSUPPORTED_CASE_OPERATION"


def test_invalid_case_is_denied():
    decision = CaseAccessPolicy().evaluate(
        make_technician(), object(), "VIEW_CASE"
    )

    assert not decision.allowed
    assert decision.reason == "INVALID_CASE"


def test_invalid_technician_is_denied():
    decision = CaseAccessPolicy().evaluate(
        None, make_case(), "VIEW_CASE"
    )

    assert not decision.allowed
    assert decision.reason == "INVALID_TECHNICIAN_IDENTITY"


def test_matching_owner_can_access_case():
    case = make_case()
    technician = make_technician()
    ownership = CaseOwnership(case, technician)

    decision = CaseAccessPolicy().evaluate(
        technician, case, "VIEW_CASE", ownership
    )

    assert decision.allowed


def test_non_owner_is_denied_when_ownership_is_enforced():
    case = make_case()
    owner = make_technician("TECH-001")
    other = make_technician("TECH-002")
    ownership = CaseOwnership(case, owner)

    decision = CaseAccessPolicy().evaluate(
        other, case, "VIEW_CASE", ownership
    )

    assert not decision.allowed
    assert decision.reason == "CASE_NOT_OWNED_BY_TECHNICIAN"


def test_ownership_for_another_case_is_rejected():
    case = make_case()
    other_case = make_case()
    other_case.case_id = "OTHER-CASE"
    technician = make_technician()
    ownership = CaseOwnership(other_case, technician)

    decision = CaseAccessPolicy().evaluate(
        technician, case, "VIEW_CASE", ownership
    )

    assert not decision.allowed
    assert decision.reason == "CASE_OWNERSHIP_MISMATCH"


def test_invalid_ownership_is_denied():
    decision = CaseAccessPolicy().evaluate(
        make_technician(), make_case(), "VIEW_CASE", object()
    )

    assert not decision.allowed
    assert decision.reason == "INVALID_OWNERSHIP"


def test_decision_projection_does_not_change_decision():
    decision = CaseAccessPolicy().evaluate(
        make_technician(), make_case(), "VIEW_CASE"
    )

    data = decision.projection()
    data["allowed"] = False

    assert decision.allowed
    assert decision.projection()["allowed"] is True


def test_decision_is_immutable():
    decision = CaseAccessPolicy().evaluate(
        make_technician(), make_case(), "VIEW_CASE"
    )

    with pytest.raises((AttributeError, TypeError)):
        decision.allowed = False
