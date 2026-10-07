"""Integrated production security architecture."""

from dataclasses import dataclass

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
from packaging.remote_security import (
    RemoteSecurityDecision,
    evaluate_remote_operation,
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


@dataclass(frozen=True)
class SecurityArchitecture:
    """Canonical security boundaries used by production runtime."""

    remediation_authorization: object
    privileged_operations: object
    unsafe_input_validation: object
    sensitive_information_protection: object
    remote_fleet_security: object


PRODUCTION_SECURITY_ARCHITECTURE = SecurityArchitecture(
    remediation_authorization=RemediationAuthorization,
    privileged_operations=PrivilegedOperation,
    unsafe_input_validation=ValidatedInput,
    sensitive_information_protection=RedactionResult,
    remote_fleet_security=RemoteSecurityDecision,
)


def security_architecture_is_consistent() -> bool:
    """Verify that all canonical security boundaries are available."""

    return (
        PRODUCTION_SECURITY_ARCHITECTURE.remediation_authorization
        is RemediationAuthorization
        and PRODUCTION_SECURITY_ARCHITECTURE.privileged_operations
        is PrivilegedOperation
        and PRODUCTION_SECURITY_ARCHITECTURE.unsafe_input_validation
        is ValidatedInput
        and PRODUCTION_SECURITY_ARCHITECTURE.sensitive_information_protection
        is RedactionResult
        and PRODUCTION_SECURITY_ARCHITECTURE.remote_fleet_security
        is RemoteSecurityDecision
        and callable(authorization_allows_execution)
        and callable(privilege_allows_operation)
        and callable(evaluate_remote_operation)
        and callable(redact_sensitive_information)
        and callable(validate_command_argument)
        and callable(validate_identifier)
        and callable(validate_machine_name)
        and callable(validate_remote_target)
        and callable(validate_service_name)
    )


__all__ = [
    "SecurityArchitecture",
    "PRODUCTION_SECURITY_ARCHITECTURE",
    "security_architecture_is_consistent",
]
