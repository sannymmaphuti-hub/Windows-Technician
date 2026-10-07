"""Integration between application lifecycle and application services."""

from dataclasses import dataclass

from packaging.application_lifecycle import (
    ApplicationLifecycle,
    ApplicationLifecycleState,
    begin_shutdown,
    begin_startup,
    complete_shutdown,
    complete_startup,
    enter_degraded,
)
from packaging.application_services import (
    ApplicationServiceName,
    ApplicationServiceRegistry,
    ApplicationServiceState,
    update_application_service,
)
from packaging.runtime_operational_logging import (
    RuntimeOperationalLogger,
)


@dataclass(frozen=True)
class ServiceLifecycleResult:
    lifecycle: ApplicationLifecycle
    registry: ApplicationServiceRegistry

    def __post_init__(self) -> None:
        if not isinstance(self.lifecycle, ApplicationLifecycle):
            raise TypeError(
                "lifecycle must be an ApplicationLifecycle."
            )

        if not isinstance(
            self.registry,
            ApplicationServiceRegistry,
        ):
            raise TypeError(
                "registry must be an ApplicationServiceRegistry."
            )


def _validate_operational_logger(
    operational_logger: RuntimeOperationalLogger | None,
) -> None:
    if (
        operational_logger is not None
        and not isinstance(
            operational_logger,
            RuntimeOperationalLogger,
        )
    ):
        raise TypeError(
            "operational_logger must be a RuntimeOperationalLogger "
            "or None."
        )


def _service_event(
    operational_logger: RuntimeOperationalLogger | None,
    event: str,
    name: ApplicationServiceName,
    *,
    level: str = "INFO",
) -> None:
    if operational_logger is None:
        return

    operational_logger.log_event(
        event,
        f"Application service {name.name} entered {event.removeprefix('SERVICE_').lower()} state.",
        level=level,
    )


def start_application_services(
    lifecycle: ApplicationLifecycle,
    registry: ApplicationServiceRegistry,
    operational_logger: RuntimeOperationalLogger | None = None,
) -> ServiceLifecycleResult:
    if not isinstance(lifecycle, ApplicationLifecycle):
        raise TypeError(
            "lifecycle must be an ApplicationLifecycle."
        )

    if not isinstance(registry, ApplicationServiceRegistry):
        raise TypeError(
            "registry must be an ApplicationServiceRegistry."
        )

    _validate_operational_logger(operational_logger)

    lifecycle = begin_startup(lifecycle)

    for name in ApplicationServiceName:
        if operational_logger is not None:
            _service_event(
                operational_logger,
                "SERVICE_STARTING",
                name,
            )

        registry = update_application_service(
            registry,
            name,
            ApplicationServiceState.STARTING,
        )

    for name in ApplicationServiceName:
        registry = update_application_service(
            registry,
            name,
            ApplicationServiceState.RUNNING,
        )

        if operational_logger is not None:
            _service_event(
                operational_logger,
                "SERVICE_STARTED",
                name,
            )

    lifecycle = complete_startup(lifecycle)

    return ServiceLifecycleResult(
        lifecycle=lifecycle,
        registry=registry,
    )


def degrade_application_service(
    lifecycle: ApplicationLifecycle,
    registry: ApplicationServiceRegistry,
    name: ApplicationServiceName,
    operational_logger: RuntimeOperationalLogger | None = None,
) -> ServiceLifecycleResult:
    if not isinstance(lifecycle, ApplicationLifecycle):
        raise TypeError(
            "lifecycle must be an ApplicationLifecycle."
        )

    if not isinstance(registry, ApplicationServiceRegistry):
        raise TypeError(
            "registry must be an ApplicationServiceRegistry."
        )

    if not isinstance(name, ApplicationServiceName):
        raise TypeError(
            "name must be an ApplicationServiceName."
        )

    _validate_operational_logger(operational_logger)

    registry = update_application_service(
        registry,
        name,
        ApplicationServiceState.DEGRADED,
    )

    if operational_logger is not None:
        _service_event(
            operational_logger,
            "SERVICE_DEGRADED",
            name,
            level="WARNING",
        )

    if lifecycle.state in (
        ApplicationLifecycleState.RUNNING,
        ApplicationLifecycleState.STARTING,
    ):
        lifecycle = enter_degraded(lifecycle)

    return ServiceLifecycleResult(
        lifecycle=lifecycle,
        registry=registry,
    )


def stop_application_services(
    lifecycle: ApplicationLifecycle,
    registry: ApplicationServiceRegistry,
    operational_logger: RuntimeOperationalLogger | None = None,
) -> ServiceLifecycleResult:
    if not isinstance(lifecycle, ApplicationLifecycle):
        raise TypeError(
            "lifecycle must be an ApplicationLifecycle."
        )

    if not isinstance(registry, ApplicationServiceRegistry):
        raise TypeError(
            "registry must be an ApplicationServiceRegistry."
        )

    _validate_operational_logger(operational_logger)

    lifecycle = begin_shutdown(lifecycle)

    for name in ApplicationServiceName:
        if operational_logger is not None:
            _service_event(
                operational_logger,
                "SERVICE_STOPPING",
                name,
            )

        registry = update_application_service(
            registry,
            name,
            ApplicationServiceState.STOPPING,
        )

    for name in ApplicationServiceName:
        registry = update_application_service(
            registry,
            name,
            ApplicationServiceState.STOPPED,
        )

        if operational_logger is not None:
            _service_event(
                operational_logger,
                "SERVICE_STOPPED",
                name,
            )

    lifecycle = complete_shutdown(lifecycle)

    return ServiceLifecycleResult(
        lifecycle=lifecycle,
        registry=registry,
    )
