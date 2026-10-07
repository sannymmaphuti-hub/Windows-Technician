"""Production configuration integration boundary."""

from dataclasses import dataclass
from pathlib import Path

from packaging.application_runtime import ApplicationRuntime
from packaging.application_runtime_configuration import (
    ConfigurationRuntimeResult,
    RuntimeConfigurationState,
    apply_configuration_to_runtime,
    configuration_allows_startup,
)
from packaging.configuration_environment_architecture import (
    ConfigurationEnvironmentArchitecture,
    build_configuration_environment_architecture,
)
from packaging.configuration_sources import (
    ConfigurationLocations,
    ConfigurationSources,
    build_configuration_locations as _build_configuration_locations,
    merge_configuration,
)
from packaging.runtime_configuration import (
    RuntimePaths,
    initialize_runtime_paths,
)
from packaging.safe_defaults import apply_safe_defaults


@dataclass(frozen=True)
class ProductionConfiguration:
    """Validated effective configuration presented to the runtime."""

    state: RuntimeConfigurationState

    def __post_init__(self) -> None:
        if not isinstance(
            self.state,
            RuntimeConfigurationState,
        ):
            raise TypeError(
                "state must be a RuntimeConfigurationState."
            )


@dataclass(frozen=True)
class ProductionConfigurationResult:
    """Result of applying production configuration to a runtime."""

    runtime: ApplicationRuntime
    configuration: ProductionConfiguration
    startup_allowed: bool

    def __post_init__(self) -> None:
        if not isinstance(
            self.runtime,
            ApplicationRuntime,
        ):
            raise TypeError(
                "runtime must be an ApplicationRuntime."
            )

        if not isinstance(
            self.configuration,
            ProductionConfiguration,
        ):
            raise TypeError(
                "configuration must be a ProductionConfiguration."
            )

        if not isinstance(
            self.startup_allowed,
            bool,
        ):
            raise TypeError(
                "startup_allowed must be a boolean."
            )


def build_production_configuration(
    configuration: RuntimeConfigurationState,
) -> ProductionConfiguration:
    """Wrap an existing validated runtime configuration state."""
    if not isinstance(
        configuration,
        RuntimeConfigurationState,
    ):
        raise TypeError(
            "configuration must be a RuntimeConfigurationState."
        )

    return ProductionConfiguration(
        state=configuration,
    )


def build_production_configuration_from_sources(
    sources: ConfigurationSources,
    *,
    safe: bool = True,
    recovered: bool = False,
) -> ProductionConfiguration:
    """
    Build production configuration from canonical system/user sources.

    System configuration is merged first, user configuration overrides
    it, and the existing canonical safe-default mechanism fills missing
    settings.
    """
    if not isinstance(
        sources,
        ConfigurationSources,
    ):
        raise TypeError(
            "sources must be ConfigurationSources."
        )

    if not isinstance(safe, bool):
        raise TypeError(
            "safe must be a boolean."
        )

    if not isinstance(recovered, bool):
        raise TypeError(
            "recovered must be a boolean."
        )

    merged = merge_configuration(sources)
    effective = apply_safe_defaults(merged)

    return ProductionConfiguration(
        state=RuntimeConfigurationState(
            configuration=effective,
            recovered=recovered,
            safe=safe,
        )
    )


def build_production_configuration_from_environment(
    architecture: ConfigurationEnvironmentArchitecture,
    *,
    safe: bool | None = None,
    recovered: bool = False,
) -> ProductionConfiguration:
    """
    Build production configuration from the canonical integrated
    configuration/environment architecture.
    """
    if not isinstance(
        architecture,
        ConfigurationEnvironmentArchitecture,
    ):
        raise TypeError(
            "architecture must be a "
            "ConfigurationEnvironmentArchitecture."
        )

    if safe is not None and not isinstance(safe, bool):
        raise TypeError(
            "safe must be a boolean or None."
        )

    if not isinstance(recovered, bool):
        raise TypeError(
            "recovered must be a boolean."
        )

    effective_safe = (
        safe
        if safe is not None
        else (
            architecture.effective_configuration.get(
                "remediation",
                {},
            ).get(
                "authorized_by_default",
                True,
            )
            is False
            and architecture.effective_configuration.get(
                "remote",
                {},
            ).get(
                "enabled",
                True,
            )
            is False
            and architecture.effective_configuration.get(
                "telemetry",
                {},
            ).get(
                "enabled",
                True,
            )
            is False
        )
    )

    return ProductionConfiguration(
        state=RuntimeConfigurationState(
            configuration=architecture.effective_configuration,
            recovered=recovered,
            safe=effective_safe,
        )
    )


def build_default_production_configuration(
    *,
    project_root: Path,
    user_data_root: Path,
    system_data_root: Path,
    recovered: bool = False,
) -> ProductionConfiguration:
    """
    Build production configuration through the complete canonical
    configuration/environment architecture.
    """
    architecture = build_configuration_environment_architecture(
        project_root=project_root,
        user_data_root=user_data_root,
        system_data_root=system_data_root,
    )

    return build_production_configuration_from_environment(
        architecture,
        recovered=recovered,
    )


def initialize_production_runtime_paths(
    paths: RuntimePaths | None = None,
) -> RuntimePaths:
    """Initialize the canonical runtime filesystem boundary."""
    return initialize_runtime_paths(paths)


def build_configuration_locations(
    *,
    user_data_root: Path,
    system_data_root: Path,
) -> ConfigurationLocations:
    """Build canonical system/user configuration locations."""
    return _build_configuration_locations(
        user_data_root=user_data_root,
        system_data_root=system_data_root,
    )


def apply_production_configuration(
    runtime: ApplicationRuntime,
    configuration: ProductionConfiguration,
) -> ProductionConfigurationResult:
    if not isinstance(
        runtime,
        ApplicationRuntime,
    ):
        raise TypeError(
            "runtime must be an ApplicationRuntime."
        )

    if not isinstance(
        configuration,
        ProductionConfiguration,
    ):
        raise TypeError(
            "configuration must be a ProductionConfiguration."
        )

    result: ConfigurationRuntimeResult = (
        apply_configuration_to_runtime(
            runtime,
            configuration.state,
        )
    )

    return ProductionConfigurationResult(
        runtime=result.runtime,
        configuration=configuration,
        startup_allowed=configuration_allows_startup(
            result
        ),
    )


def production_configuration_is_safe(
    configuration: ProductionConfiguration,
) -> bool:
    if not isinstance(
        configuration,
        ProductionConfiguration,
    ):
        return False

    return configuration.state.safe


def production_configuration_allows_startup(
    result: ProductionConfigurationResult,
) -> bool:
    if not isinstance(
        result,
        ProductionConfigurationResult,
    ):
        return False

    return result.startup_allowed
