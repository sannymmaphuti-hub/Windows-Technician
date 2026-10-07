"""Canonical Windows Technician application service boundary."""

from dataclasses import dataclass
from enum import Enum


class ApplicationServiceState(Enum):
    UNAVAILABLE = "unavailable"
    STARTING = "starting"
    RUNNING = "running"
    DEGRADED = "degraded"
    STOPPING = "stopping"
    STOPPED = "stopped"
    FAILED = "failed"


class ApplicationServiceName(Enum):
    CONFIGURATION = "configuration"
    DIAGNOSTICS = "diagnostics"
    INTELLIGENCE = "intelligence"
    LOGGING = "logging"
    UI = "ui"


@dataclass(frozen=True)
class ApplicationService:
    name: ApplicationServiceName
    state: ApplicationServiceState

    def __post_init__(self) -> None:
        if not isinstance(self.name, ApplicationServiceName):
            raise TypeError(
                "name must be an ApplicationServiceName."
            )

        if not isinstance(self.state, ApplicationServiceState):
            raise TypeError(
                "state must be an ApplicationServiceState."
            )


@dataclass(frozen=True)
class ApplicationServiceRegistry:
    services: tuple[ApplicationService, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.services, tuple):
            raise TypeError("services must be a tuple.")

        names = tuple(service.name for service in self.services)

        if len(names) != len(set(names)):
            raise ValueError(
                "Application service names must be unique."
            )


def create_application_service_registry() -> ApplicationServiceRegistry:
    return ApplicationServiceRegistry(
        services=tuple(
            ApplicationService(
                name=name,
                state=ApplicationServiceState.UNAVAILABLE,
            )
            for name in ApplicationServiceName
        )
    )


def update_application_service(
    registry: ApplicationServiceRegistry,
    name: ApplicationServiceName,
    state: ApplicationServiceState,
) -> ApplicationServiceRegistry:
    if not isinstance(registry, ApplicationServiceRegistry):
        raise TypeError(
            "registry must be an ApplicationServiceRegistry."
        )

    if not isinstance(name, ApplicationServiceName):
        raise TypeError(
            "name must be an ApplicationServiceName."
        )

    if not isinstance(state, ApplicationServiceState):
        raise TypeError(
            "state must be an ApplicationServiceState."
        )

    updated = tuple(
        ApplicationService(
            name=service.name,
            state=state if service.name is name else service.state,
        )
        for service in registry.services
    )

    return ApplicationServiceRegistry(services=updated)


def get_application_service(
    registry: ApplicationServiceRegistry,
    name: ApplicationServiceName,
) -> ApplicationService:
    if not isinstance(registry, ApplicationServiceRegistry):
        raise TypeError(
            "registry must be an ApplicationServiceRegistry."
        )

    if not isinstance(name, ApplicationServiceName):
        raise TypeError(
            "name must be an ApplicationServiceName."
        )

    for service in registry.services:
        if service.name is name:
            return service

    raise ValueError(
        f"Application service is not registered: {name.value}"
    )


def application_service_registry_healthy(
    registry: ApplicationServiceRegistry,
) -> bool:
    if not isinstance(registry, ApplicationServiceRegistry):
        return False

    return all(
        service.state is ApplicationServiceState.RUNNING
        for service in registry.services
    )
