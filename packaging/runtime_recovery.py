"""Runtime recovery decision boundary."""

from dataclasses import dataclass
from enum import Enum


class RecoveryAction(str, Enum):
    CONTINUE = "continue"
    DEGRADED = "degraded"
    STOP = "stop"


@dataclass(frozen=True)
class RecoveryDecision:
    action: RecoveryAction
    reason: str

    def __post_init__(self):
        if not isinstance(self.action, RecoveryAction):
            raise TypeError(
                "action must be a RecoveryAction."
            )

        if not isinstance(self.reason, str) or not self.reason.strip():
            raise ValueError(
                "reason must be a non-empty string."
            )


def determine_recovery(
    *,
    startup_failed: bool = False,
    dependency_missing: bool = False,
    configuration_recovered: bool = False,
    runtime_operation_failed: bool = False,
) -> RecoveryDecision:
    if startup_failed:
        return RecoveryDecision(
            action=RecoveryAction.STOP,
            reason="Application startup failed.",
        )

    if dependency_missing:
        return RecoveryDecision(
            action=RecoveryAction.DEGRADED,
            reason="A required runtime dependency is unavailable.",
        )

    if configuration_recovered:
        return RecoveryDecision(
            action=RecoveryAction.CONTINUE,
            reason="Configuration was recovered using safe defaults.",
        )

    if runtime_operation_failed:
        return RecoveryDecision(
            action=RecoveryAction.DEGRADED,
            reason="A runtime operation failed and functionality may be limited.",
        )

    return RecoveryDecision(
        action=RecoveryAction.CONTINUE,
        reason="No recovery action is required.",
    )
