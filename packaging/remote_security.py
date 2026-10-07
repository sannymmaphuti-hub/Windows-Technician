"""Production remote and fleet security boundary."""

from dataclasses import dataclass
from enum import Enum

from packaging.privileged_operation import (
    OperationPrivilege,
    PermissionContext,
    PrivilegedOperation,
    privilege_allows_operation,
)
from packaging.remediation_authorization import (
    RemediationAuthorization,
    authorization_allows_execution,
)
from packaging.unsafe_input import (
    InputValidationError,
    validate_remote_target,
)


class RemoteSecurityReason(str, Enum):
    ALLOWED = "ALLOWED"
    REMOTE_OPERATIONS_DISABLED = "REMOTE_OPERATIONS_DISABLED"
    INVALID_TARGET = "INVALID_TARGET"
    UNAUTHORIZED = "UNAUTHORIZED"
    INSUFFICIENT_PRIVILEGE = "INSUFFICIENT_PRIVILEGE"


@dataclass(frozen=True)
class RemoteSecurityDecision:
    """Decision determining whether a remote operation may execute."""

    target: str
    operation_id: str
    allowed: bool
    reason: RemoteSecurityReason

    def __post_init__(self):
        if not isinstance(self.target, str) or not self.target.strip():
            raise ValueError("target must be a non-empty string.")

        if not isinstance(self.operation_id, str) or not self.operation_id.strip():
            raise ValueError(
                "operation_id must be a non-empty string."
            )

        if not isinstance(self.allowed, bool):
            raise TypeError("allowed must be a boolean.")

        if not isinstance(self.reason, RemoteSecurityReason):
            raise TypeError(
                "reason must be a RemoteSecurityReason."
            )


def _invalid_target_value(target: object) -> str:
    """Return a safe diagnostic representation for an invalid target."""

    if isinstance(target, str) and target.strip():
        return "[INVALID TARGET]"

    return "[INVALID TARGET]"


def evaluate_remote_operation(
    *,
    target: str,
    operation_id: str,
    remote_operations_enabled: bool,
    authorization: RemediationAuthorization,
    required_privilege: OperationPrivilege,
    permission_context: PermissionContext,
) -> RemoteSecurityDecision:
    """
    Evaluate whether a remote operation may execute.

    Every security gate must pass explicitly. No gate performs
    implicit authorization or automatic privilege elevation.
    """

    if not isinstance(remote_operations_enabled, bool):
        raise TypeError(
            "remote_operations_enabled must be a boolean."
        )

    if not isinstance(authorization, RemediationAuthorization):
        raise TypeError(
            "authorization must be a RemediationAuthorization."
        )

    if not isinstance(required_privilege, OperationPrivilege):
        raise TypeError(
            "required_privilege must be an OperationPrivilege."
        )

    if not isinstance(permission_context, PermissionContext):
        raise TypeError(
            "permission_context must be a PermissionContext."
        )

    try:
        validated_target = validate_remote_target(target)
    except InputValidationError:
        return RemoteSecurityDecision(
            target=_invalid_target_value(target),
            operation_id=operation_id,
            allowed=False,
            reason=RemoteSecurityReason.INVALID_TARGET,
        )

    if not remote_operations_enabled:
        return RemoteSecurityDecision(
            target=validated_target.value,
            operation_id=operation_id,
            allowed=False,
            reason=RemoteSecurityReason.REMOTE_OPERATIONS_DISABLED,
        )

    if not authorization_allows_execution(authorization):
        return RemoteSecurityDecision(
            target=validated_target.value,
            operation_id=operation_id,
            allowed=False,
            reason=RemoteSecurityReason.UNAUTHORIZED,
        )

    operation = PrivilegedOperation(
        operation_id=operation_id,
        required_privilege=required_privilege,
    )

    if not privilege_allows_operation(
        operation,
        permission_context,
    ):
        return RemoteSecurityDecision(
            target=validated_target.value,
            operation_id=operation_id,
            allowed=False,
            reason=RemoteSecurityReason.INSUFFICIENT_PRIVILEGE,
        )

    return RemoteSecurityDecision(
        target=validated_target.value,
        operation_id=operation_id,
        allowed=True,
        reason=RemoteSecurityReason.ALLOWED,
    )
