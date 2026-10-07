"""Canonical production application runtime orchestration."""

from dataclasses import dataclass

from engine.application_logging import ApplicationLogger
from packaging.application_lifecycle import (
    ApplicationLifecycle,
    ApplicationLifecycleState,
    create_application_lifecycle,
)
from packaging.application_service_lifecycle import (
    degrade_application_service,
    start_application_services,
    stop_application_services,
)
from packaging.application_services import (
    ApplicationServiceName,
    ApplicationServiceRegistry,
    create_application_service_registry,
    get_application_service,
)
from packaging.runtime_operational_state import (
    RuntimeOperationalState,
)
from packaging.runtime_operational_logging import (
    RuntimeOperationalLogger,
)
from packaging.runtime_recovery import RecoveryAction


@dataclass(frozen=True)
class ApplicationRuntime:
    lifecycle: ApplicationLifecycle
    services: ApplicationServiceRegistry
    operational_state: RuntimeOperationalState | None = None
    operational_logger: RuntimeOperationalLogger | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.lifecycle, ApplicationLifecycle):
            raise TypeError(
                "lifecycle must be an ApplicationLifecycle."
            )

        if not isinstance(
            self.services,
            ApplicationServiceRegistry,
        ):
            raise TypeError(
                "services must be an ApplicationServiceRegistry."
            )

        if (
            self.operational_state is not None
            and not isinstance(
                self.operational_state,
                RuntimeOperationalState,
            )
        ):
            raise TypeError(
                "operational_state must be a RuntimeOperationalState "
                "or None."
            )

        if (
            self.operational_logger is not None
            and not isinstance(
                self.operational_logger,
                RuntimeOperationalLogger,
            )
        ):
            raise TypeError(
                "operational_logger must be a RuntimeOperationalLogger "
                "or None."
            )

    @property
    def status(self) -> str:
        """
        Compatibility status surface.

        The canonical lifecycle remains authoritative. This property
        exposes the historical string status expected by compatibility
        consumers without creating a second lifecycle.
        """
        status_map = {
            ApplicationLifecycleState.CREATED: "STARTING",
            ApplicationLifecycleState.STARTING: "STARTING",
            ApplicationLifecycleState.RUNNING: "READY",
            ApplicationLifecycleState.DEGRADED: "ERROR",
            ApplicationLifecycleState.FAILED: "ERROR",
            ApplicationLifecycleState.STOPPING: "STOPPING",
            ApplicationLifecycleState.STOPPED: "STOPPED",
        }

        return status_map.get(
            self.lifecycle.state,
            "ERROR",
        )


def create_application_runtime(
    operational_state: RuntimeOperationalState | None = None,
    operational_logger: RuntimeOperationalLogger | None = None,
) -> ApplicationRuntime:
    return ApplicationRuntime(
        lifecycle=create_application_lifecycle(),
        services=create_application_service_registry(),
        operational_state=operational_state,
        operational_logger=operational_logger,
    )


def _persist_lifecycle(
    runtime: ApplicationRuntime,
    *,
    lifecycle_state: ApplicationLifecycleState,
    clean_shutdown: bool,
    recovered: bool = False,
) -> None:
    if runtime.operational_state is None:
        return

    runtime.operational_state.persist(
        lifecycle_state=lifecycle_state.name,
        clean_shutdown=clean_shutdown,
        recovered=recovered,
    )


def _log_starting(runtime: ApplicationRuntime) -> None:
    if runtime.operational_logger is not None:
        runtime.operational_logger.application_starting()


def _log_running(runtime: ApplicationRuntime) -> None:
    if runtime.operational_logger is not None:
        runtime.operational_logger.application_running()


def _log_degraded(runtime: ApplicationRuntime) -> None:
    if runtime.operational_logger is not None:
        runtime.operational_logger.application_degraded()


def _log_stopping(runtime: ApplicationRuntime) -> None:
    if runtime.operational_logger is not None:
        runtime.operational_logger.application_stopping()


def _log_stopped(runtime: ApplicationRuntime) -> None:
    if runtime.operational_logger is not None:
        runtime.operational_logger.application_stopped()


def start_application_runtime(
    runtime: ApplicationRuntime,
) -> ApplicationRuntime:
    if not isinstance(runtime, ApplicationRuntime):
        raise TypeError(
            "runtime must be an ApplicationRuntime."
        )


    _log_starting(runtime)

    result = start_application_services(
        runtime.lifecycle,
        runtime.services,
        runtime.operational_logger,
    )

    updated = ApplicationRuntime(
        lifecycle=result.lifecycle,
        services=result.registry,
        operational_state=runtime.operational_state,
        operational_logger=runtime.operational_logger,
    )

    _persist_lifecycle(
        updated,
        lifecycle_state=updated.lifecycle.state,
        clean_shutdown=False,
    )

    if updated.lifecycle.state is ApplicationLifecycleState.RUNNING:
        _log_running(updated)

    return updated


def apply_runtime_recovery(
    runtime: ApplicationRuntime,
    recovery_action: RecoveryAction,
    service_name: ApplicationServiceName | None = None,
) -> ApplicationRuntime:
    if not isinstance(runtime, ApplicationRuntime):
        raise TypeError(
            "runtime must be an ApplicationRuntime."
        )

    if not isinstance(recovery_action, RecoveryAction):
        raise TypeError(
            "recovery_action must be a RecoveryAction."
        )

    if service_name is not None and not isinstance(
        service_name,
        ApplicationServiceName,
    ):
        raise TypeError(
            "service_name must be an ApplicationServiceName or None."
        )

    if recovery_action is RecoveryAction.CONTINUE:
        return runtime

    if recovery_action is RecoveryAction.DEGRADED:
        if service_name is None:
            if runtime.lifecycle.state in (
                ApplicationLifecycleState.STARTING,
                ApplicationLifecycleState.RUNNING,
            ):
                from packaging.application_lifecycle import enter_degraded

                lifecycle = enter_degraded(runtime.lifecycle)

                updated = ApplicationRuntime(
                    lifecycle=lifecycle,
                    services=runtime.services,
                    operational_state=runtime.operational_state,
                    operational_logger=runtime.operational_logger,
                )

                _persist_lifecycle(
                    updated,
                    lifecycle_state=updated.lifecycle.state,
                    clean_shutdown=False,
                )

                _log_degraded(updated)

                return updated

            return runtime

        result = degrade_application_service(
            runtime.lifecycle,
            runtime.services,
            service_name,
            runtime.operational_logger,
        )

        updated = ApplicationRuntime(
            lifecycle=result.lifecycle,
            services=result.registry,
            operational_state=runtime.operational_state,
            operational_logger=runtime.operational_logger,
        )

        _persist_lifecycle(
            updated,
            lifecycle_state=updated.lifecycle.state,
            clean_shutdown=False,
        )

        if updated.lifecycle.state is ApplicationLifecycleState.DEGRADED:
            _log_degraded(updated)

        return updated

    return runtime


def stop_application_runtime(
    runtime: ApplicationRuntime,
) -> ApplicationRuntime:
    if not isinstance(runtime, ApplicationRuntime):
        raise TypeError(
            "runtime must be an ApplicationRuntime."
        )

    # Stopping an already-stopped runtime is idempotent.
    if application_runtime_is_stopped(runtime):
        return runtime

    _log_stopping(runtime)

    result = stop_application_services(
        runtime.lifecycle,
        runtime.services,
        runtime.operational_logger,
    )

    updated = ApplicationRuntime(
        lifecycle=result.lifecycle,
        services=result.registry,
        operational_state=runtime.operational_state,
        operational_logger=runtime.operational_logger,
    )

    _persist_lifecycle(
        updated,
        lifecycle_state=updated.lifecycle.state,
        clean_shutdown=True,
    )

    if updated.lifecycle.state is ApplicationLifecycleState.STOPPED:
        _log_stopped(updated)

    return updated


def application_runtime_is_running(
    runtime: ApplicationRuntime,
) -> bool:
    if not isinstance(runtime, ApplicationRuntime):
        return False

    return (
        runtime.lifecycle.state is ApplicationLifecycleState.RUNNING
    )


def application_runtime_is_degraded(
    runtime: ApplicationRuntime,
) -> bool:
    if not isinstance(runtime, ApplicationRuntime):
        return False

    return (
        runtime.lifecycle.state is ApplicationLifecycleState.DEGRADED
    )


def application_runtime_is_stopped(
    runtime: ApplicationRuntime,
) -> bool:
    if not isinstance(runtime, ApplicationRuntime):
        return False

    return (
        runtime.lifecycle.state is ApplicationLifecycleState.STOPPED
    )
