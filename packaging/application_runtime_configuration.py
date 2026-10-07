"""Integration between configuration recovery and application runtime."""

from dataclasses import dataclass

from packaging.application_runtime import (
    ApplicationRuntime,
    create_application_runtime,
)
from packaging.application_lifecycle import ApplicationLifecycleState


@dataclass(frozen=True)
class RuntimeConfigurationState:
    """Configuration state accepted by the production runtime."""

    configuration: object
    recovered: bool
    safe: bool

    def __post_init__(self) -> None:
        if not isinstance(self.recovered, bool):
            raise TypeError("recovered must be a boolean.")

        if not isinstance(self.safe, bool):
            raise TypeError("safe must be a boolean.")


@dataclass(frozen=True)
class ConfigurationRuntimeResult:
    """Result of applying configuration state to the runtime."""

    runtime: ApplicationRuntime
    configuration: RuntimeConfigurationState
    startup_allowed: bool

    def __post_init__(self) -> None:
        if not isinstance(self.runtime, ApplicationRuntime):
            raise TypeError(
                "runtime must be an ApplicationRuntime."
            )

        if not isinstance(
            self.configuration,
            RuntimeConfigurationState,
        ):
            raise TypeError(
                "configuration must be a RuntimeConfigurationState."
            )

        if not isinstance(self.startup_allowed, bool):
            raise TypeError(
                "startup_allowed must be a boolean."
            )


def apply_configuration_to_runtime(
    runtime: ApplicationRuntime,
    configuration: RuntimeConfigurationState,
) -> ConfigurationRuntimeResult:
    if not isinstance(runtime, ApplicationRuntime):
        raise TypeError(
            "runtime must be an ApplicationRuntime."
        )

    if not isinstance(
        configuration,
        RuntimeConfigurationState,
    ):
        raise TypeError(
            "configuration must be a RuntimeConfigurationState."
        )

    startup_allowed = configuration.safe

    return ConfigurationRuntimeResult(
        runtime=runtime,
        configuration=configuration,
        startup_allowed=startup_allowed,
    )


def configuration_allows_startup(
    result: ConfigurationRuntimeResult,
) -> bool:
    if not isinstance(result, ConfigurationRuntimeResult):
        return False

    return result.startup_allowed


def configuration_was_recovered(
    result: ConfigurationRuntimeResult,
) -> bool:
    if not isinstance(result, ConfigurationRuntimeResult):
        return False

    return result.configuration.recovered


def configuration_is_safe(
    result: ConfigurationRuntimeResult,
) -> bool:
    if not isinstance(result, ConfigurationRuntimeResult):
        return False

    return result.configuration.safe


def runtime_configuration_is_startable(
    configuration: RuntimeConfigurationState,
) -> bool:
    if not isinstance(configuration, RuntimeConfigurationState):
        return False

    return configuration.safe
