from engine.operation_authorization_policy import OperationAuthorizationPolicy
from engine.technician_identity import TechnicianIdentity


def make_technician(role="TECHNICIAN"):
    return TechnicianIdentity(
        technician_id="TECH-001",
        name="Test Technician",
        role=role,
    )


def test_permitted_operation_is_allowed():
    decision = OperationAuthorizationPolicy().evaluate(
        make_technician(),
        "VIEW_CASE",
    )

    assert decision.allowed
    assert decision.reason == "ROLE_PERMISSION_GRANTED"


def test_operation_names_are_normalized():
    decision = OperationAuthorizationPolicy().evaluate(
        make_technician(),
        "  view_case  ",
    )

    assert decision.allowed
    assert decision.operation == "VIEW_CASE"


def test_unpermitted_operation_is_denied():
    decision = OperationAuthorizationPolicy().evaluate(
        make_technician(),
        "ASSIGN_CASE",
    )

    assert not decision.allowed
    assert decision.reason == "PERMISSION_DENIED"


def test_unknown_operation_fails_closed():
    decision = OperationAuthorizationPolicy().evaluate(
        make_technician(),
        "DELETE_ALL_DATA",
    )

    assert not decision.allowed
    assert decision.reason == "UNSUPPORTED_OPERATION"


def test_invalid_identity_fails_closed():
    decision = OperationAuthorizationPolicy().evaluate(
        None,
        "VIEW_CASE",
    )

    assert not decision.allowed
    assert decision.reason == "INVALID_TECHNICIAN_IDENTITY"


def test_invalid_operation_fails_closed():
    policy = OperationAuthorizationPolicy()
    technician = make_technician()

    for operation in ("", "   ", None, 123):
        decision = policy.evaluate(technician, operation)

        assert not decision.allowed
        assert decision.reason == "INVALID_OPERATION"


def test_remediation_is_not_implicitly_authorized():
    policy = OperationAuthorizationPolicy()

    for role in (
        "TECHNICIAN",
        "SENIOR_TECHNICIAN",
        "SUPERVISOR",
        "ADMINISTRATOR",
    ):
        technician = make_technician(role)

        assert not policy.evaluate(
            technician,
            "AUTHORIZE_REMEDIATION",
        ).allowed

        assert not policy.evaluate(
            technician,
            "EXECUTE_REMEDIATION",
        ).allowed


def test_decision_projection_is_defensive():
    decision = OperationAuthorizationPolicy().evaluate(
        make_technician(),
        "VIEW_CASE",
    )

    projection = decision.projection()
    projection["allowed"] = False

    assert decision.allowed
    assert decision.projection()["allowed"] is True


def test_decision_is_immutable():
    import pytest

    decision = OperationAuthorizationPolicy().evaluate(
        make_technician(),
        "VIEW_CASE",
    )

    with pytest.raises((AttributeError, TypeError)):
        decision.allowed = False


def test_denied_decision_identifies_the_operation():
    decision = OperationAuthorizationPolicy().evaluate(
        make_technician(),
        "ASSIGN_CASE",
    )

    assert decision.operation == "ASSIGN_CASE"
    assert decision.technician_id == "TECH-001"
