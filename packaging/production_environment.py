"""Integrated production multi-configuration environment architecture."""

from dataclasses import dataclass

from packaging.diagnostic_dataset_environment import (
    DiagnosticDatasetEnvironment,
    diagnostic_dataset_compatibility_is_safe,
)
from packaging.display_environment import (
    DisplayEnvironment,
    display_compatibility_is_safe,
)
from packaging.memory_environment import (
    MemoryEnvironment,
    memory_compatibility_is_safe,
)
from packaging.network_environment import (
    NetworkEnvironment,
    network_compatibility_is_safe,
)
from packaging.permission_environment import (
    PermissionEnvironment,
    permission_compatibility_is_safe,
)
from packaging.service_environment import (
    ServiceEnvironment,
    service_compatibility_is_safe,
)
from packaging.windows_environment import WindowsEnvironment
from packaging.windows_compatibility import (
    evaluate_windows_compatibility,
)


@dataclass(frozen=True)
class ProductionEnvironment:
    windows: WindowsEnvironment
    memory: MemoryEnvironment
    display: DisplayEnvironment
    dataset: DiagnosticDatasetEnvironment
    service: ServiceEnvironment
    network: NetworkEnvironment
    permissions: PermissionEnvironment


@dataclass(frozen=True)
class ProductionEnvironmentResult:
    compatible: bool
    reason: str

    def __post_init__(self) -> None:
        if not isinstance(self.compatible, bool):
            raise TypeError("compatible must be a boolean.")

        if not isinstance(self.reason, str) or not self.reason.strip():
            raise ValueError("reason must be a non-empty string.")


def evaluate_production_environment(
    environment: ProductionEnvironment,
) -> ProductionEnvironmentResult:
    """Evaluate all production environment boundaries together."""

    if not isinstance(environment, ProductionEnvironment):
        raise TypeError(
            "environment must be a ProductionEnvironment."
        )

    windows_result = evaluate_windows_compatibility(
        environment.windows
    )

    memory_safe = memory_compatibility_is_safe(
        environment.memory
    )

    display_safe = display_compatibility_is_safe(
        environment.display
    )

    dataset_safe = diagnostic_dataset_compatibility_is_safe(
        environment.dataset
    )

    service_safe = service_compatibility_is_safe(
        environment.service
    )

    network_safe = network_compatibility_is_safe(
        environment.network
    )

    permissions_safe = permission_compatibility_is_safe(
        environment.permissions
    )

    compatible = (
        windows_result.supported
        and memory_safe
        and display_safe
        and dataset_safe
        and service_safe
        and network_safe
        and permissions_safe
    )

    if compatible:
        return ProductionEnvironmentResult(
            compatible=True,
            reason=(
                "The environment is within the production "
                "compatibility boundaries."
            ),
        )

    return ProductionEnvironmentResult(
        compatible=False,
        reason=(
            "The environment is outside at least one required "
            "production compatibility boundary."
        ),
    )


def production_environment_is_safe(
    environment: ProductionEnvironment,
) -> bool:
    """Return whether the complete environment is production-safe."""

    return evaluate_production_environment(environment).compatible
