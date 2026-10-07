"""Integration between application lifecycle and runtime reliability."""

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
from packaging.runtime_recovery import RecoveryAction


@dataclass(frozen=True)
class LifecycleRecoveryDecision:
    lifecycle: ApplicationLifecycle
    recovery_action: RecoveryAction
    should_continue: bool

    def __post_init__(self) -> None:
        if not isinstance(self.lifecycle, ApplicationLifecycle):
            raise TypeError(
                "lifecycle must be an ApplicationLifecycle."
            )

        if not isinstance(self.recovery_action, RecoveryAction):
            raise TypeError(
                "recovery_action must be a RecoveryAction."
            )

        if not isinstance(self.should_continue, bool):
            raise TypeError(
                "should_continue must be a boolean."
            )


def apply_recovery_action(
    lifecycle: ApplicationLifecycle,
    recovery_action: RecoveryAction,
) -> LifecycleRecoveryDecision:
    if not isinstance(lifecycle, ApplicationLifecycle):
        raise TypeError(
            "lifecycle must be an ApplicationLifecycle."
        )

    if not isinstance(recovery_action, RecoveryAction):
        raise TypeError(
            "recovery_action must be a RecoveryAction."
        )

    if recovery_action is RecoveryAction.CONTINUE:
        if lifecycle.state is ApplicationLifecycleState.STARTING:
            lifecycle = complete_startup(lifecycle)

        return LifecycleRecoveryDecision(
            lifecycle=lifecycle,
            recovery_action=recovery_action,
            should_continue=True,
        )

    if recovery_action is RecoveryAction.DEGRADED:
        if lifecycle.state in (
            ApplicationLifecycleState.STARTING,
            ApplicationLifecycleState.RUNNING,
        ):
            lifecycle = enter_degraded(lifecycle)

        return LifecycleRecoveryDecision(
            lifecycle=lifecycle,
            recovery_action=recovery_action,
            should_continue=True,
        )

    return LifecycleRecoveryDecision(
        lifecycle=lifecycle,
        recovery_action=recovery_action,
        should_continue=False,
    )


def start_application(
    lifecycle: ApplicationLifecycle,
) -> ApplicationLifecycle:
    if not isinstance(lifecycle, ApplicationLifecycle):
        raise TypeError(
            "lifecycle must be an ApplicationLifecycle."
        )

    return begin_startup(lifecycle)


def stop_application(
    lifecycle: ApplicationLifecycle,
) -> ApplicationLifecycle:
    if not isinstance(lifecycle, ApplicationLifecycle):
        raise TypeError(
            "lifecycle must be an ApplicationLifecycle."
        )

    return complete_shutdown(
        begin_shutdown(lifecycle)
    )
