"""Integrated runtime reliability architecture."""

from dataclasses import dataclass

from packaging.configuration_recovery import (
    ConfigurationRecovery,
    load_configuration,
)
from packaging.dependency_boundary import (
    DependencyStatus,
    check_dependencies,
)
from packaging.runtime_exception import (
    RuntimeResult,
    execute_runtime_operation,
)
from packaging.runtime_recovery import (
    RecoveryDecision,
    determine_recovery,
)
from packaging.runtime_startup import (
    StartupResult,
    execute_startup,
)


@dataclass(frozen=True)
class RuntimeReliabilityResult:
    startup: StartupResult
    operation: RuntimeResult
    configuration: ConfigurationRecovery
    dependencies: tuple[DependencyStatus, ...]
    recovery: RecoveryDecision


def initialize_runtime_reliability(
    *,
    startup_callable,
    operation_name: str,
    operation_callable,
    configuration_path,
    dependency_names: tuple[str, ...],
) -> RuntimeReliabilityResult:
    startup = execute_startup(startup_callable)

    configuration = load_configuration(configuration_path)

    dependencies = check_dependencies(dependency_names)

    operation = execute_runtime_operation(
        operation_name,
        operation_callable,
    )

    recovery = determine_recovery(
        startup_failed=not startup.succeeded,
        dependency_missing=(
            not all(
                dependency.available
                for dependency in dependencies
            )
        ),
        configuration_recovered=configuration.recovered,
        runtime_operation_failed=not operation.succeeded,
    )

    return RuntimeReliabilityResult(
        startup=startup,
        operation=operation,
        configuration=configuration,
        dependencies=dependencies,
        recovery=recovery,
    )


def runtime_reliability_is_healthy(
    result: RuntimeReliabilityResult,
) -> bool:
    return (
        result.startup.succeeded
        and result.operation.succeeded
        and all(
            dependency.available
            for dependency in result.dependencies
        )
        and not result.configuration.recovered
    )
