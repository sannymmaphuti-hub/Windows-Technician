"""Recovery-aware application startup boundary."""

from dataclasses import dataclass

from packaging.operational_state import OperationalState
from packaging.runtime_operational_state import RuntimeOperationalState


@dataclass(frozen=True)
class StartupRecoveryContext:
    """Operational history available during application startup."""

    previous_state: OperationalState
    recovery_required: bool

    def __post_init__(self) -> None:
        if not isinstance(
            self.previous_state,
            OperationalState,
        ):
            raise TypeError(
                "previous_state must be an OperationalState."
            )

        if not isinstance(
            self.recovery_required,
            bool,
        ):
            raise TypeError(
                "recovery_required must be a boolean."
            )


def build_startup_recovery_context(
    operational_state: RuntimeOperationalState,
) -> StartupRecoveryContext:
    if not isinstance(
        operational_state,
        RuntimeOperationalState,
    ):
        raise TypeError(
            "operational_state must be a RuntimeOperationalState."
        )

    previous_state = operational_state.recover()

    return StartupRecoveryContext(
        previous_state=previous_state,
        recovery_required=previous_state.recovered,
    )


def startup_recovery_is_required(
    context: StartupRecoveryContext,
) -> bool:
    if not isinstance(
        context,
        StartupRecoveryContext,
    ):
        return False

    return context.recovery_required


def startup_recovery_was_clean(
    context: StartupRecoveryContext,
) -> bool:
    if not isinstance(
        context,
        StartupRecoveryContext,
    ):
        return False

    return context.previous_state.clean_shutdown
