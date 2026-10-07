"""Tests for the production remote and fleet security boundary."""

import pytest

from packaging.privileged_operation import (
    OperationPrivilege,
    PermissionContext,
    PrivilegeLevel,
)
from packaging.remediation_authorization import (
    AuthorizationReason,
    AuthorizationState,
    RemediationAuthorization,
    authorize,
    unauthorized,
)
from packaging.remote_security import (
    RemoteSecurityDecision,
    RemoteSecurityReason,
    evaluate_remote_operation,
)


def standard_context():
    return PermissionContext(
        privilege_level=PrivilegeLevel.STANDARD
    )


def elevated_context():
    return PermissionContext(
        privilege_level=PrivilegeLevel.ELEVATED
    )


def authorized_action(action_id="remote-action"):
    return authorize(action_id)


def unauthorized_action(action_id="remote-action"):
    return unauthorized(action_id)


def test_remote_operations_are_denied_by_default():
    result = evaluate_remote_operation(
        target="WORKSTATION-01",
        operation_id="remote-action",
        remote_operations_enabled=False,
        authorization=authorized_action(),
        required_privilege=OperationPrivilege.STANDARD,
        permission_context=standard_context(),
    )

    assert not result.allowed
    assert result.reason == (
        RemoteSecurityReason.REMOTE_OPERATIONS_DISABLED
    )


def test_valid_authorized_standard_remote_operation_is_allowed():
    result = evaluate_remote_operation(
        target="WORKSTATION-01",
        operation_id="remote-action",
        remote_operations_enabled=True,
        authorization=authorized_action(),
        required_privilege=OperationPrivilege.STANDARD,
        permission_context=standard_context(),
    )

    assert result.allowed
    assert result.reason == RemoteSecurityReason.ALLOWED


def test_elevated_context_can_execute_standard_operation():
    result = evaluate_remote_operation(
        target="WORKSTATION-01",
        operation_id="remote-action",
        remote_operations_enabled=True,
        authorization=authorized_action(),
        required_privilege=OperationPrivilege.STANDARD,
        permission_context=elevated_context(),
    )

    assert result.allowed


def test_standard_context_cannot_execute_elevated_operation():
    result = evaluate_remote_operation(
        target="WORKSTATION-01",
        operation_id="remote-action",
        remote_operations_enabled=True,
        authorization=authorized_action(),
        required_privilege=OperationPrivilege.ELEVATED,
        permission_context=standard_context(),
    )

    assert not result.allowed
    assert result.reason == (
        RemoteSecurityReason.INSUFFICIENT_PRIVILEGE
    )


def test_elevated_context_can_execute_elevated_operation():
    result = evaluate_remote_operation(
        target="WORKSTATION-01",
        operation_id="remote-action",
        remote_operations_enabled=True,
        authorization=authorized_action(),
        required_privilege=OperationPrivilege.ELEVATED,
        permission_context=elevated_context(),
    )

    assert result.allowed


def test_unauthorized_remote_operation_is_denied():
    result = evaluate_remote_operation(
        target="WORKSTATION-01",
        operation_id="remote-action",
        remote_operations_enabled=True,
        authorization=unauthorized_action(),
        required_privilege=OperationPrivilege.STANDARD,
        permission_context=standard_context(),
    )

    assert not result.allowed
    assert result.reason == RemoteSecurityReason.UNAUTHORIZED


def test_invalid_remote_target_is_denied():
    result = evaluate_remote_operation(
        target="WORKSTATION-01;evil",
        operation_id="remote-action",
        remote_operations_enabled=True,
        authorization=authorized_action(),
        required_privilege=OperationPrivilege.STANDARD,
        permission_context=standard_context(),
    )

    assert not result.allowed
    assert result.reason == RemoteSecurityReason.INVALID_TARGET
    assert result.target == "[INVALID TARGET]"


@pytest.mark.parametrize(
    "target",
    [
        "WORKSTATION-01",
        "SERVER01",
        "LAB-PC_01",
        "machine.example.local",
    ],
)
def test_valid_remote_targets_are_accepted(target):
    result = evaluate_remote_operation(
        target=target,
        operation_id="remote-action",
        remote_operations_enabled=True,
        authorization=authorized_action(),
        required_privilege=OperationPrivilege.STANDARD,
        permission_context=standard_context(),
    )

    assert result.allowed


@pytest.mark.parametrize(
    "target",
    [
        "",
        " ",
        "WORKSTATION 01",
        "WORKSTATION/01",
        "WORKSTATION\\01",
        "WORKSTATION;01",
        "WORKSTATION|01",
        "WORKSTATION&01",
        "WORKSTATION`01",
        "WORKSTATION\n01",
    ],
)
def test_invalid_remote_targets_are_denied(target):
    result = evaluate_remote_operation(
        target=target,
        operation_id="remote-action",
        remote_operations_enabled=True,
        authorization=authorized_action(),
        required_privilege=OperationPrivilege.STANDARD,
        permission_context=standard_context(),
    )

    assert not result.allowed
    assert result.reason == RemoteSecurityReason.INVALID_TARGET
    assert result.target == "[INVALID TARGET]"


def test_remote_operation_requires_all_security_gates():
    result = evaluate_remote_operation(
        target="WORKSTATION-01",
        operation_id="remote-action",
        remote_operations_enabled=True,
        authorization=authorized_action(),
        required_privilege=OperationPrivilege.ELEVATED,
        permission_context=standard_context(),
    )

    assert not result.allowed
    assert result.reason == (
        RemoteSecurityReason.INSUFFICIENT_PRIVILEGE
    )


@pytest.mark.parametrize(
    "enabled",
    [True, False],
)
def test_remote_enabled_accepts_boolean(enabled):
    result = evaluate_remote_operation(
        target="WORKSTATION-01",
        operation_id="remote-action",
        remote_operations_enabled=enabled,
        authorization=authorized_action(),
        required_privilege=OperationPrivilege.STANDARD,
        permission_context=standard_context(),
    )

    assert isinstance(result.allowed, bool)


@pytest.mark.parametrize(
    "value",
    [None, 1, "true", object()],
)
def test_remote_enabled_rejects_non_boolean(value):
    with pytest.raises(TypeError):
        evaluate_remote_operation(
            target="WORKSTATION-01",
            operation_id="remote-action",
            remote_operations_enabled=value,
            authorization=authorized_action(),
            required_privilege=OperationPrivilege.STANDARD,
            permission_context=standard_context(),
        )


def test_invalid_authorization_object_is_rejected():
    with pytest.raises(TypeError):
        evaluate_remote_operation(
            target="WORKSTATION-01",
            operation_id="remote-action",
            remote_operations_enabled=True,
            authorization=object(),
            required_privilege=OperationPrivilege.STANDARD,
            permission_context=standard_context(),
        )


def test_invalid_privilege_requirement_is_rejected():
    with pytest.raises(TypeError):
        evaluate_remote_operation(
            target="WORKSTATION-01",
            operation_id="remote-action",
            remote_operations_enabled=True,
            authorization="STANDARD",
            required_privilege="ELEVATED",
            permission_context=standard_context(),
        )


def test_invalid_permission_context_is_rejected():
    with pytest.raises(TypeError):
        evaluate_remote_operation(
            target="WORKSTATION-01",
            operation_id="remote-action",
            remote_operations_enabled=True,
            authorization=authorized_action(),
            required_privilege=OperationPrivilege.STANDARD,
            permission_context=object(),
        )


def test_decision_is_immutable():
    result = evaluate_remote_operation(
        target="WORKSTATION-01",
        operation_id="remote-action",
        remote_operations_enabled=True,
        authorization=authorized_action(),
        required_privilege=OperationPrivilege.STANDARD,
        permission_context=standard_context(),
    )

    with pytest.raises(AttributeError):
        result.allowed = False


def test_decision_preserves_operation_identity():
    result = evaluate_remote_operation(
        target="WORKSTATION-01",
        operation_id="remote-action-42",
        remote_operations_enabled=True,
        authorization=authorize("remote-action-42"),
        required_privilege=OperationPrivilege.STANDARD,
        permission_context=standard_context(),
    )

    assert result.operation_id == "remote-action-42"


def test_decision_preserves_validated_target():
    result = evaluate_remote_operation(
        target="SERVER01",
        operation_id="remote-action",
        remote_operations_enabled=True,
        authorization=authorized_action(),
        required_privilege=OperationPrivilege.STANDARD,
        permission_context=standard_context(),
    )

    assert result.target == "SERVER01"


def test_remote_security_reason_values_are_stable():
    assert RemoteSecurityReason.ALLOWED.value == "ALLOWED"
    assert (
        RemoteSecurityReason.REMOTE_OPERATIONS_DISABLED.value
        == "REMOTE_OPERATIONS_DISABLED"
    )
    assert RemoteSecurityReason.INVALID_TARGET.value == "INVALID_TARGET"
    assert RemoteSecurityReason.UNAUTHORIZED.value == "UNAUTHORIZED"
    assert (
        RemoteSecurityReason.INSUFFICIENT_PRIVILEGE.value
        == "INSUFFICIENT_PRIVILEGE"
    )


def test_unauthorized_state_cannot_bypass_remote_security():
    authorization = RemediationAuthorization(
        action_id="remote-action",
        state=AuthorizationState.UNAUTHORIZED,
        reason=AuthorizationReason.NOT_REQUESTED,
    )

    result = evaluate_remote_operation(
        target="WORKSTATION-01",
        operation_id="remote-action",
        remote_operations_enabled=True,
        authorization=authorization,
        required_privilege=OperationPrivilege.STANDARD,
        permission_context=standard_context(),
    )

    assert not result.allowed
    assert result.reason == RemoteSecurityReason.UNAUTHORIZED


def test_denied_state_cannot_bypass_remote_security():
    authorization = RemediationAuthorization(
        action_id="remote-action",
        state=AuthorizationState.DENIED,
        reason=AuthorizationReason.USER_DENIED,
    )

    result = evaluate_remote_operation(
        target="WORKSTATION-01",
        operation_id="remote-action",
        remote_operations_enabled=True,
        authorization=authorization,
        required_privilege=OperationPrivilege.STANDARD,
        permission_context=standard_context(),
    )

    assert not result.allowed
    assert result.reason == RemoteSecurityReason.UNAUTHORIZED


def test_invalid_target_is_not_exposed_in_decision():
    result = evaluate_remote_operation(
        target="SERVER01;Remove-Item-C",
        operation_id="remote-action",
        remote_operations_enabled=True,
        authorization=authorized_action(),
        required_privilege=OperationPrivilege.STANDARD,
        permission_context=standard_context(),
    )

    assert result.reason == RemoteSecurityReason.INVALID_TARGET
    assert result.target == "[INVALID TARGET]"
    assert "Remove-Item" not in result.target
