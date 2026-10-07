"""Production restricted-permission environment boundary."""

from dataclasses import dataclass
from enum import Enum

from packaging.privileged_operation import (
    OperationPrivilege,
    PermissionContext,
    PrivilegedOperation,
    privilege_allows_operation,
)


class PermissionEnvironmentLevel(str, Enum):
    STANDARD = "STANDARD"
    ELEVATED = "ELEVATED"
    RESTRICTED = "RESTRICTED"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class PermissionEnvironment:
    context: PermissionContext

    def __post_init__(self) -> None:
        if not isinstance(self.context, PermissionContext):
            raise TypeError(
                "context must be a PermissionContext."
            )


@dataclass(frozen=True)
class PermissionCompatibilityResult:
    compatible: bool
    level: PermissionEnvironmentLevel
    reason: str

    def __post_init__(self) -> None:
        if not isinstance(self.compatible, bool):
            raise TypeError("compatible must be a boolean.")

        if not isinstance(self.level, PermissionEnvironmentLevel):
            raise TypeError(
                "level must be a PermissionEnvironmentLevel."
            )

        if not isinstance(self.reason, str) or not self.reason.strip():
            raise ValueError("reason must be a non-empty string.")


def classify_permission_environment(
    environment: PermissionEnvironment,
) -> PermissionEnvironmentLevel:
    """Classify the current permission environment."""

    if not isinstance(environment, PermissionEnvironment):
        raise TypeError(
            "environment must be a PermissionEnvironment."
        )

    privilege = environment.context.privilege_level

    if privilege.value == "ELEVATED":
        return PermissionEnvironmentLevel.ELEVATED

    if privilege.value == "STANDARD":
        return PermissionEnvironmentLevel.STANDARD

    return PermissionEnvironmentLevel.UNKNOWN


def evaluate_permission_compatibility(
    environment: PermissionEnvironment,
) -> PermissionCompatibilityResult:
    """Evaluate whether the current permission environment is usable."""

    level = classify_permission_environment(environment)

    if level is PermissionEnvironmentLevel.ELEVATED:
        return PermissionCompatibilityResult(
            compatible=True,
            level=level,
            reason=(
                "The application has elevated permissions. "
                "Standard and elevated operations may be evaluated "
                "against their explicit privilege requirements."
            ),
        )

    if level is PermissionEnvironmentLevel.STANDARD:
        return PermissionCompatibilityResult(
            compatible=True,
            level=level,
            reason=(
                "The application has standard permissions. "
                "Diagnostics remain available while operations "
                "requiring elevation remain restricted."
            ),
        )

    return PermissionCompatibilityResult(
        compatible=True,
        level=level,
        reason=(
            "The permission level is unknown. "
            "The application remains restricted until the required "
            "permission level can be established."
        ),
    )


def permission_compatibility_is_safe(
    environment: PermissionEnvironment,
) -> bool:
    """Return whether the permission environment is safe to handle."""

    return evaluate_permission_compatibility(environment).compatible


def operation_is_allowed_in_environment(
    environment: PermissionEnvironment,
    *,
    operation_id: str,
    required_privilege: OperationPrivilege,
) -> bool:
    """Evaluate one operation using the canonical privilege boundary."""

    if not isinstance(environment, PermissionEnvironment):
        raise TypeError(
            "environment must be a PermissionEnvironment."
        )

    if not isinstance(operation_id, str) or not operation_id.strip():
        raise ValueError("operation_id must be a non-empty string.")

    if not isinstance(required_privilege, OperationPrivilege):
        raise TypeError(
            "required_privilege must be an OperationPrivilege."
        )

    operation = PrivilegedOperation(
        operation_id=operation_id,
        required_privilege=required_privilege,
    )

    return privilege_allows_operation(
        operation,
        environment.context,
    )
