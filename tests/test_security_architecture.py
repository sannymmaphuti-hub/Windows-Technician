from packaging.privileged_operation import (
    OperationPrivilege,
    PermissionContext,
    PrivilegeLevel,
    PrivilegedOperation,
    privilege_allows_operation,
)
from packaging.remediation_authorization import (
    AuthorizationReason,
    AuthorizationState,
    RemediationAuthorization,
    authorization_allows_execution,
)
from packaging.remote_security import (
    RemoteSecurityDecision,
    RemoteSecurityReason,
    evaluate_remote_operation,
)
from packaging.security_architecture import (
    PRODUCTION_SECURITY_ARCHITECTURE,
    SecurityArchitecture,
    security_architecture_is_consistent,
)
from packaging.sensitive_information import (
    RedactionResult,
    redact_sensitive_information,
)
from packaging.unsafe_input import (
    ValidatedInput,
    validate_command_argument,
    validate_identifier,
    validate_machine_name,
    validate_remote_target,
    validate_service_name,
)


def test_security_architecture_is_canonical():
    assert security_architecture_is_consistent()


def test_security_architecture_has_expected_type():
    assert isinstance(
        PRODUCTION_SECURITY_ARCHITECTURE,
        SecurityArchitecture,
    )


def test_authorization_boundary_is_integrated():
    assert (
        PRODUCTION_SECURITY_ARCHITECTURE.remediation_authorization
        is RemediationAuthorization
    )


def test_privileged_operation_boundary_is_integrated():
    assert (
        PRODUCTION_SECURITY_ARCHITECTURE.privileged_operations
        is PrivilegedOperation
    )


def test_input_validation_boundary_is_integrated():
    assert (
        PRODUCTION_SECURITY_ARCHITECTURE.unsafe_input_validation
        is ValidatedInput
    )


def test_sensitive_information_boundary_is_integrated():
    assert (
        PRODUCTION_SECURITY_ARCHITECTURE.sensitive_information_protection
        is RedactionResult
    )


def test_remote_security_boundary_is_integrated():
    assert (
        PRODUCTION_SECURITY_ARCHITECTURE.remote_fleet_security
        is RemoteSecurityDecision
    )


def test_unauthorized_remediation_cannot_execute():
    authorization = RemediationAuthorization(
        action_id="action-1",
        state=AuthorizationState.UNAUTHORIZED,
        reason=AuthorizationReason.NOT_REQUESTED,
    )

    assert not authorization_allows_execution(authorization)


def test_authorized_remediation_can_execute():
    authorization = RemediationAuthorization(
        action_id="action-1",
        state=AuthorizationState.AUTHORIZED,
        reason=AuthorizationReason.USER_APPROVED,
    )

    assert authorization_allows_execution(authorization)


def test_standard_operation_is_allowed_without_elevation():
    operation = PrivilegedOperation(
        operation_id="diagnostic",
        required_privilege=OperationPrivilege.STANDARD,
    )
    context = PermissionContext(
        privilege_level=PrivilegeLevel.STANDARD,
    )

    assert privilege_allows_operation(operation, context)


def test_elevated_operation_requires_elevated_context():
    operation = PrivilegedOperation(
        operation_id="repair",
        required_privilege=OperationPrivilege.ELEVATED,
    )
    context = PermissionContext(
        privilege_level=PrivilegeLevel.STANDARD,
    )

    assert not privilege_allows_operation(operation, context)


def test_elevated_operation_is_allowed_when_context_is_elevated():
    operation = PrivilegedOperation(
        operation_id="repair",
        required_privilege=OperationPrivilege.ELEVATED,
    )
    context = PermissionContext(
        privilege_level=PrivilegeLevel.ELEVATED,
    )

    assert privilege_allows_operation(operation, context)


def test_input_validation_functions_are_available():
    assert validate_machine_name("PC-01").value == "PC-01"
    assert validate_identifier("case:001").value == "case:001"
    assert validate_service_name("Spooler").value == "Spooler"
    assert validate_command_argument("argument").value == "argument"
    assert validate_remote_target("PC-01").value == "PC-01"


def test_sensitive_information_redaction_is_available():
    result = redact_sensitive_information(
        "token=abc123"
    )

    assert isinstance(result, RedactionResult)
    assert result.redacted


def test_remote_security_requires_explicit_enablement():
    authorization = RemediationAuthorization(
        action_id="remote-action",
        state=AuthorizationState.AUTHORIZED,
        reason=AuthorizationReason.TECHNICIAN_APPROVED,
    )

    result = evaluate_remote_operation(
        target="PC-01",
        operation_id="remote-action",
        remote_operations_enabled=False,
        authorization=authorization,
        required_privilege=OperationPrivilege.STANDARD,
        permission_context=PermissionContext(
            privilege_level=PrivilegeLevel.STANDARD,
        ),
    )

    assert not result.allowed
    assert result.reason is RemoteSecurityReason.REMOTE_OPERATIONS_DISABLED


def test_remote_security_requires_authorization():
    authorization = RemediationAuthorization(
        action_id="remote-action",
        state=AuthorizationState.UNAUTHORIZED,
        reason=AuthorizationReason.NOT_REQUESTED,
    )

    result = evaluate_remote_operation(
        target="PC-01",
        operation_id="remote-action",
        remote_operations_enabled=True,
        authorization=authorization,
        required_privilege=OperationPrivilege.STANDARD,
        permission_context=PermissionContext(
            privilege_level=PrivilegeLevel.STANDARD,
        ),
    )

    assert not result.allowed
    assert result.reason is RemoteSecurityReason.UNAUTHORIZED


def test_remote_security_requires_privilege():
    authorization = RemediationAuthorization(
        action_id="remote-action",
        state=AuthorizationState.AUTHORIZED,
        reason=AuthorizationReason.TECHNICIAN_APPROVED,
    )

    result = evaluate_remote_operation(
        target="PC-01",
        operation_id="remote-action",
        remote_operations_enabled=True,
        authorization=authorization,
        required_privilege=OperationPrivilege.ELEVATED,
        permission_context=PermissionContext(
            privilege_level=PrivilegeLevel.STANDARD,
        ),
    )

    assert not result.allowed
    assert result.reason is RemoteSecurityReason.INSUFFICIENT_PRIVILEGE


def test_remote_security_allows_fully_authorized_operation():
    authorization = RemediationAuthorization(
        action_id="remote-action",
        state=AuthorizationState.AUTHORIZED,
        reason=AuthorizationReason.TECHNICIAN_APPROVED,
    )

    result = evaluate_remote_operation(
        target="PC-01",
        operation_id="remote-action",
        remote_operations_enabled=True,
        authorization=authorization,
        required_privilege=OperationPrivilege.STANDARD,
        permission_context=PermissionContext(
            privilege_level=PrivilegeLevel.STANDARD,
        ),
    )

    assert result.allowed
    assert result.reason is RemoteSecurityReason.ALLOWED


def test_security_architecture_does_not_perform_implicit_authorization():
    authorization = RemediationAuthorization(
        action_id="remote-action",
        state=AuthorizationState.UNAUTHORIZED,
        reason=AuthorizationReason.NOT_REQUESTED,
    )

    result = evaluate_remote_operation(
        target="PC-01",
        operation_id="remote-action",
        remote_operations_enabled=True,
        authorization=authorization,
        required_privilege=OperationPrivilege.STANDARD,
        permission_context=PermissionContext(
            privilege_level=PrivilegeLevel.STANDARD,
        ),
    )

    assert not result.allowed


def test_security_architecture_does_not_perform_automatic_elevation():
    authorization = RemediationAuthorization(
        action_id="remote-action",
        state=AuthorizationState.AUTHORIZED,
        reason=AuthorizationReason.TECHNICIAN_APPROVED,
    )

    result = evaluate_remote_operation(
        target="PC-01",
        operation_id="remote-action",
        remote_operations_enabled=True,
        authorization=authorization,
        required_privilege=OperationPrivilege.ELEVATED,
        permission_context=PermissionContext(
            privilege_level=PrivilegeLevel.STANDARD,
        ),
    )

    assert not result.allowed
