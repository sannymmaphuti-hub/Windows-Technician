import pytest

from packaging.application_runtime import (
    application_runtime_is_degraded,
    application_runtime_is_running,
    create_application_runtime,
    start_application_runtime,
)
from packaging.application_runtime_reliability import (
    RuntimeReliabilityResult,
    apply_recovery_decision_to_runtime,
    runtime_should_continue,
    runtime_should_degrade,
    runtime_should_stop,
)
from packaging.runtime_recovery import (
    RecoveryAction,
    RecoveryDecision,
)


def _running_runtime():
    return start_application_runtime(
        create_application_runtime()
    )


def test_continue_decision_preserves_running_runtime():
    runtime = _running_runtime()

    decision = RecoveryDecision(
        action=RecoveryAction.CONTINUE,
        reason="Runtime operation completed successfully.",
    )

    result = apply_recovery_decision_to_runtime(
        runtime,
        decision,
    )

    assert result.runtime == runtime
    assert application_runtime_is_running(result.runtime) is True
    assert runtime_should_continue(result) is True


def test_degraded_decision_degrades_runtime():
    runtime = _running_runtime()

    decision = RecoveryDecision(
        action=RecoveryAction.DEGRADED,
        reason="A non-critical runtime dependency failed.",
    )

    result = apply_recovery_decision_to_runtime(
        runtime,
        decision,
    )

    assert application_runtime_is_degraded(result.runtime) is True
    assert runtime_should_degrade(result) is True
    assert runtime_should_continue(result) is False


def test_stop_decision_preserves_stop_intent():
    runtime = _running_runtime()

    decision = RecoveryDecision(
        action=RecoveryAction.STOP,
        reason="A critical runtime dependency failed.",
    )

    result = apply_recovery_decision_to_runtime(
        runtime,
        decision,
    )

    assert result.runtime == runtime
    assert runtime_should_stop(result) is True


def test_recovery_decision_is_preserved():
    runtime = _running_runtime()

    decision = RecoveryDecision(
        action=RecoveryAction.DEGRADED,
        reason="Dependency unavailable.",
    )

    result = apply_recovery_decision_to_runtime(
        runtime,
        decision,
    )

    assert result.recovery_decision is decision


def test_result_is_frozen():
    runtime = _running_runtime()

    decision = RecoveryDecision(
        action=RecoveryAction.CONTINUE,
        reason="Success.",
    )

    result = RuntimeReliabilityResult(
        runtime=runtime,
        recovery_decision=decision,
    )

    with pytest.raises(AttributeError):
        result.runtime = runtime


def test_invalid_runtime_is_rejected():
    decision = RecoveryDecision(
        action=RecoveryAction.CONTINUE,
        reason="Success.",
    )

    with pytest.raises(TypeError):
        apply_recovery_decision_to_runtime(
            None,
            decision,
        )


def test_invalid_decision_is_rejected():
    runtime = _running_runtime()

    with pytest.raises(TypeError):
        apply_recovery_decision_to_runtime(
            runtime,
            None,
        )


def test_continue_helper_rejects_invalid_value():
    assert runtime_should_continue(None) is False


def test_degrade_helper_rejects_invalid_value():
    assert runtime_should_degrade(None) is False


def test_stop_helper_rejects_invalid_value():
    assert runtime_should_stop(None) is False


def test_result_requires_runtime():
    decision = RecoveryDecision(
        action=RecoveryAction.CONTINUE,
        reason="Success.",
    )

    with pytest.raises(TypeError):
        RuntimeReliabilityResult(
            runtime=None,
            recovery_decision=decision,
        )


def test_result_requires_recovery_decision():
    runtime = _running_runtime()

    with pytest.raises(TypeError):
        RuntimeReliabilityResult(
            runtime=runtime,
            recovery_decision=None,
        )
