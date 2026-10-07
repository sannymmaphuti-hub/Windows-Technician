"""Production Windows service environment boundary."""

from dataclasses import dataclass
from enum import Enum


class ServiceState(str, Enum):
    RUNNING = "RUNNING"
    STOPPED = "STOPPED"
    FAILED = "FAILED"
    START_PENDING = "START_PENDING"
    STOP_PENDING = "STOP_PENDING"
    UNKNOWN = "UNKNOWN"


class ServiceEnvironmentLevel(str, Enum):
    HEALTHY = "HEALTHY"
    INACTIVE = "INACTIVE"
    FAILED = "FAILED"
    TRANSITIONING = "TRANSITIONING"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class ServiceEnvironment:
    service_name: str
    state: ServiceState

    def __post_init__(self) -> None:
        if not isinstance(self.service_name, str):
            raise TypeError("service_name must be a string.")

        if not self.service_name.strip():
            raise ValueError("service_name must not be empty.")

        if not isinstance(self.state, ServiceState):
            raise TypeError("state must be a ServiceState.")


@dataclass(frozen=True)
class ServiceCompatibilityResult:
    compatible: bool
    level: ServiceEnvironmentLevel
    reason: str

    def __post_init__(self) -> None:
        if not isinstance(self.compatible, bool):
            raise TypeError("compatible must be a boolean.")

        if not isinstance(self.level, ServiceEnvironmentLevel):
            raise TypeError(
                "level must be a ServiceEnvironmentLevel."
            )

        if not isinstance(self.reason, str) or not self.reason.strip():
            raise ValueError("reason must be a non-empty string.")


def classify_service_environment(
    environment: ServiceEnvironment,
) -> ServiceEnvironmentLevel:
    """Classify a Windows service environment."""

    if not isinstance(environment, ServiceEnvironment):
        raise TypeError(
            "environment must be a ServiceEnvironment."
        )

    if environment.state is ServiceState.RUNNING:
        return ServiceEnvironmentLevel.HEALTHY

    if environment.state is ServiceState.STOPPED:
        return ServiceEnvironmentLevel.INACTIVE

    if environment.state is ServiceState.FAILED:
        return ServiceEnvironmentLevel.FAILED

    if environment.state in {
        ServiceState.START_PENDING,
        ServiceState.STOP_PENDING,
    }:
        return ServiceEnvironmentLevel.TRANSITIONING

    return ServiceEnvironmentLevel.UNKNOWN


def evaluate_service_compatibility(
    environment: ServiceEnvironment,
) -> ServiceCompatibilityResult:
    """Evaluate whether a service environment can be safely handled."""

    level = classify_service_environment(environment)

    if level is ServiceEnvironmentLevel.HEALTHY:
        return ServiceCompatibilityResult(
            compatible=True,
            level=level,
            reason="The service is running normally.",
        )

    if level is ServiceEnvironmentLevel.INACTIVE:
        return ServiceCompatibilityResult(
            compatible=True,
            level=level,
            reason=(
                "The service is stopped. The condition can be "
                "diagnosed without automatically changing the service."
            ),
        )

    if level is ServiceEnvironmentLevel.FAILED:
        return ServiceCompatibilityResult(
            compatible=True,
            level=level,
            reason=(
                "The service is failed. The condition can be "
                "diagnosed without automatically changing the service."
            ),
        )

    if level is ServiceEnvironmentLevel.TRANSITIONING:
        return ServiceCompatibilityResult(
            compatible=True,
            level=level,
            reason=(
                "The service is transitioning between states. "
                "The condition can be observed safely."
            ),
        )

    return ServiceCompatibilityResult(
        compatible=True,
        level=level,
        reason=(
            "The service state is unknown. The condition can be "
            "observed safely without assuming a remediation."
        ),
    )


def service_compatibility_is_safe(
    environment: ServiceEnvironment,
) -> bool:
    """Return whether the service environment is safe to handle."""

    return evaluate_service_compatibility(environment).compatible
