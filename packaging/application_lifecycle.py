"""Canonical production application lifecycle contract."""

from dataclasses import dataclass
from enum import Enum


class ApplicationLifecycleState(Enum):
    CREATED = "created"
    STARTING = "starting"
    RUNNING = "running"
    DEGRADED = "degraded"
    STOPPING = "stopping"
    STOPPED = "stopped"
    FAILED = "failed"


@dataclass(frozen=True)
class ApplicationLifecycle:
    state: ApplicationLifecycleState
    startup_completed: bool = False
    shutdown_completed: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.state, ApplicationLifecycleState):
            raise TypeError("state must be an ApplicationLifecycleState.")

        if not isinstance(self.startup_completed, bool):
            raise TypeError("startup_completed must be a boolean.")

        if not isinstance(self.shutdown_completed, bool):
            raise TypeError("shutdown_completed must be a boolean.")


def create_application_lifecycle() -> ApplicationLifecycle:
    return ApplicationLifecycle(
        state=ApplicationLifecycleState.CREATED,
    )


def begin_startup(
    lifecycle: ApplicationLifecycle,
) -> ApplicationLifecycle:
    if not isinstance(lifecycle, ApplicationLifecycle):
        raise TypeError("lifecycle must be an ApplicationLifecycle.")

    if lifecycle.state is not ApplicationLifecycleState.CREATED:
        raise ValueError(
            "Application startup may only begin from CREATED."
        )

    return ApplicationLifecycle(
        state=ApplicationLifecycleState.STARTING,
    )


def complete_startup(
    lifecycle: ApplicationLifecycle,
) -> ApplicationLifecycle:
    if not isinstance(lifecycle, ApplicationLifecycle):
        raise TypeError("lifecycle must be an ApplicationLifecycle.")

    if lifecycle.state is not ApplicationLifecycleState.STARTING:
        raise ValueError(
            "Application startup may only complete from STARTING."
        )

    return ApplicationLifecycle(
        state=ApplicationLifecycleState.RUNNING,
        startup_completed=True,
    )


def enter_degraded(
    lifecycle: ApplicationLifecycle,
) -> ApplicationLifecycle:
    if not isinstance(lifecycle, ApplicationLifecycle):
        raise TypeError("lifecycle must be an ApplicationLifecycle.")

    if lifecycle.state not in (
        ApplicationLifecycleState.STARTING,
        ApplicationLifecycleState.RUNNING,
    ):
        raise ValueError(
            "Application may only enter DEGRADED from STARTING or RUNNING."
        )

    return ApplicationLifecycle(
        state=ApplicationLifecycleState.DEGRADED,
        startup_completed=lifecycle.startup_completed,
    )


def begin_shutdown(
    lifecycle: ApplicationLifecycle,
) -> ApplicationLifecycle:
    if not isinstance(lifecycle, ApplicationLifecycle):
        raise TypeError("lifecycle must be an ApplicationLifecycle.")

    if lifecycle.state not in (
        ApplicationLifecycleState.RUNNING,
        ApplicationLifecycleState.DEGRADED,
        ApplicationLifecycleState.FAILED,
    ):
        raise ValueError(
            "Application shutdown may only begin from RUNNING, "
            "DEGRADED, or FAILED."
        )

    return ApplicationLifecycle(
        state=ApplicationLifecycleState.STOPPING,
        startup_completed=lifecycle.startup_completed,
    )


def complete_shutdown(
    lifecycle: ApplicationLifecycle,
) -> ApplicationLifecycle:
    if not isinstance(lifecycle, ApplicationLifecycle):
        raise TypeError("lifecycle must be an ApplicationLifecycle.")

    if lifecycle.state is not ApplicationLifecycleState.STOPPING:
        raise ValueError(
            "Application shutdown may only complete from STOPPING."
        )

    return ApplicationLifecycle(
        state=ApplicationLifecycleState.STOPPED,
        startup_completed=lifecycle.startup_completed,
        shutdown_completed=True,
    )
