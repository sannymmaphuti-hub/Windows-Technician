"""Production network environment boundary."""

from dataclasses import dataclass
from enum import Enum


class NetworkState(str, Enum):
    AVAILABLE = "AVAILABLE"
    DEGRADED = "DEGRADED"
    UNAVAILABLE = "UNAVAILABLE"
    UNKNOWN = "UNKNOWN"


class NetworkEnvironmentLevel(str, Enum):
    CONNECTED = "CONNECTED"
    DEGRADED = "DEGRADED"
    OFFLINE = "OFFLINE"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class NetworkEnvironment:
    state: NetworkState

    def __post_init__(self) -> None:
        if not isinstance(self.state, NetworkState):
            raise TypeError("state must be a NetworkState.")


@dataclass(frozen=True)
class NetworkCompatibilityResult:
    compatible: bool
    level: NetworkEnvironmentLevel
    reason: str

    def __post_init__(self) -> None:
        if not isinstance(self.compatible, bool):
            raise TypeError("compatible must be a boolean.")

        if not isinstance(self.level, NetworkEnvironmentLevel):
            raise TypeError(
                "level must be a NetworkEnvironmentLevel."
            )

        if not isinstance(self.reason, str) or not self.reason.strip():
            raise ValueError("reason must be a non-empty string.")


def classify_network_environment(
    environment: NetworkEnvironment,
) -> NetworkEnvironmentLevel:
    """Classify the current network environment."""

    if not isinstance(environment, NetworkEnvironment):
        raise TypeError(
            "environment must be a NetworkEnvironment."
        )

    if environment.state is NetworkState.AVAILABLE:
        return NetworkEnvironmentLevel.CONNECTED

    if environment.state is NetworkState.DEGRADED:
        return NetworkEnvironmentLevel.DEGRADED

    if environment.state is NetworkState.UNAVAILABLE:
        return NetworkEnvironmentLevel.OFFLINE

    return NetworkEnvironmentLevel.UNKNOWN


def evaluate_network_compatibility(
    environment: NetworkEnvironment,
) -> NetworkCompatibilityResult:
    """Evaluate whether the application can safely operate in the environment."""

    level = classify_network_environment(environment)

    if level is NetworkEnvironmentLevel.CONNECTED:
        return NetworkCompatibilityResult(
            compatible=True,
            level=level,
            reason="Network connectivity is available.",
        )

    if level is NetworkEnvironmentLevel.DEGRADED:
        return NetworkCompatibilityResult(
            compatible=True,
            level=level,
            reason=(
                "Network connectivity is degraded. "
                "Local diagnostics remain available while "
                "network-dependent operations may be limited."
            ),
        )

    if level is NetworkEnvironmentLevel.OFFLINE:
        return NetworkCompatibilityResult(
            compatible=True,
            level=level,
            reason=(
                "Network connectivity is unavailable. "
                "Local diagnostics remain available while "
                "network-dependent operations are unavailable."
            ),
        )

    return NetworkCompatibilityResult(
        compatible=True,
        level=level,
        reason=(
            "Network state is unknown. "
            "Local diagnostics can continue without assuming "
            "network availability."
        ),
    )


def network_compatibility_is_safe(
    environment: NetworkEnvironment,
) -> bool:
    """Return whether the network environment can be safely handled."""

    return evaluate_network_compatibility(environment).compatible
