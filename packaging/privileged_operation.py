"""Production privileged-operation security boundary."""

from dataclasses import dataclass
from enum import Enum


class PrivilegeLevel(str, Enum):
    STANDARD = "STANDARD"
    ELEVATED = "ELEVATED"


class OperationPrivilege(str, Enum):
    STANDARD = "STANDARD"
    ELEVATED = "ELEVATED"


@dataclass(frozen=True)
class PrivilegedOperation:
    """Describes the privilege requirements of one operation."""

    operation_id: str
    required_privilege: OperationPrivilege

    def __post_init__(self):
        if not isinstance(self.operation_id, str) or not self.operation_id.strip():
            raise ValueError("operation_id must be a non-empty string.")

        if not isinstance(
            self.required_privilege,
            OperationPrivilege,
        ):
            raise TypeError(
                "required_privilege must be an OperationPrivilege."
            )


@dataclass(frozen=True)
class PermissionContext:
    """Current execution privilege context."""

    privilege_level: PrivilegeLevel

    def __post_init__(self):
        if not isinstance(
            self.privilege_level,
            PrivilegeLevel,
        ):
            raise TypeError(
                "privilege_level must be a PrivilegeLevel."
            )


def operation_requires_elevation(
    operation: PrivilegedOperation,
) -> bool:
    """Return whether an operation requires elevated privileges."""

    if not isinstance(operation, PrivilegedOperation):
        raise TypeError(
            "operation must be a PrivilegedOperation."
        )

    return operation.required_privilege == OperationPrivilege.ELEVATED


def privilege_allows_operation(
    operation: PrivilegedOperation,
    context: PermissionContext,
) -> bool:
    """Return whether the current privilege level permits the operation."""

    if not isinstance(operation, PrivilegedOperation):
        raise TypeError(
            "operation must be a PrivilegedOperation."
        )

    if not isinstance(context, PermissionContext):
        raise TypeError(
            "context must be a PermissionContext."
        )

    if operation.required_privilege == OperationPrivilege.STANDARD:
        return True

    return context.privilege_level == PrivilegeLevel.ELEVATED


def privileged_operation_is_safe_to_execute(
    operation: PrivilegedOperation,
    context: PermissionContext,
) -> bool:
    """Final privilege boundary for an operation."""

    return privilege_allows_operation(
        operation,
        context,
    )
