"""Integration between application runtime and existing runtime reliability."""

from dataclasses import dataclass

from packaging.application_runtime import (
    ApplicationRuntime,
    apply_runtime_recovery,
)
from packaging.runtime_recovery import RecoveryAction, RecoveryDecision


@dataclass(frozen=True)
class RuntimeReliabilityResult:
    runtime: ApplicationRuntime
    recovery_decision: RecoveryDecision

    def __post_init__(self) -> None:
        if not isinstance(self.runtime, ApplicationRuntime):
            raise TypeError(
                "runtime must be an ApplicationRuntime."
            )

        if not isinstance(
            self.recovery_decision,
            RecoveryDecision,
        ):
            raise TypeError(
                "recovery_decision must be a RecoveryDecision."
            )


def apply_recovery_decision_to_runtime(
    runtime: ApplicationRuntime,
    decision: RecoveryDecision,
) -> RuntimeReliabilityResult:
    if not isinstance(runtime, ApplicationRuntime):
        raise TypeError(
            "runtime must be an ApplicationRuntime."
        )

    if not isinstance(decision, RecoveryDecision):
        raise TypeError(
            "decision must be a RecoveryDecision."
        )

    updated_runtime = apply_runtime_recovery(
        runtime,
        decision.action,
    )

    return RuntimeReliabilityResult(
        runtime=updated_runtime,
        recovery_decision=decision,
    )


def runtime_should_continue(
    result: RuntimeReliabilityResult,
) -> bool:
    if not isinstance(result, RuntimeReliabilityResult):
        return False

    return result.recovery_decision.action is RecoveryAction.CONTINUE


def runtime_should_degrade(
    result: RuntimeReliabilityResult,
) -> bool:
    if not isinstance(result, RuntimeReliabilityResult):
        return False

    return result.recovery_decision.action is RecoveryAction.DEGRADED


def runtime_should_stop(
    result: RuntimeReliabilityResult,
) -> bool:
    if not isinstance(result, RuntimeReliabilityResult):
        return False

    return result.recovery_decision.action is RecoveryAction.STOP
