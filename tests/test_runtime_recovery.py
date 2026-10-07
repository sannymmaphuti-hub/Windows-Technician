"""Tests for runtime recovery decisions."""

import pytest

from packaging.runtime_recovery import (
    RecoveryAction,
    RecoveryDecision,
    determine_recovery,
)


def test_normal_runtime_continues():
    result = determine_recovery()

    assert result.action is RecoveryAction.CONTINUE


def test_startup_failure_requires_stop():
    result = determine_recovery(
        startup_failed=True,
    )

    assert result.action is RecoveryAction.STOP


def test_missing_dependency_enters_degraded_mode():
    result = determine_recovery(
        dependency_missing=True,
    )

    assert result.action is RecoveryAction.DEGRADED


def test_recovered_configuration_can_continue():
    result = determine_recovery(
        configuration_recovered=True,
    )

    assert result.action is RecoveryAction.CONTINUE


def test_runtime_operation_failure_enters_degraded_mode():
    result = determine_recovery(
        runtime_operation_failed=True,
    )

    assert result.action is RecoveryAction.DEGRADED


def test_startup_failure_takes_priority():
    result = determine_recovery(
        startup_failed=True,
        dependency_missing=True,
        runtime_operation_failed=True,
    )

    assert result.action is RecoveryAction.STOP


def test_dependency_failure_takes_priority_over_runtime_operation():
    result = determine_recovery(
        dependency_missing=True,
        runtime_operation_failed=True,
    )

    assert result.action is RecoveryAction.DEGRADED


def test_recovery_decision_requires_reason():
    with pytest.raises(ValueError):
        RecoveryDecision(
            action=RecoveryAction.CONTINUE,
            reason="",
        )


def test_recovery_decision_requires_valid_action():
    with pytest.raises(TypeError):
        RecoveryDecision(
            action="continue",
            reason="valid reason",
        )


def test_recovery_decision_is_immutable():
    result = determine_recovery()

    with pytest.raises(AttributeError):
        result.action = RecoveryAction.STOP


def test_recovery_reason_is_exposed():
    result = determine_recovery(
        configuration_recovered=True,
    )

    assert "safe defaults" in result.reason


def test_no_failure_does_not_enter_degraded_mode():
    result = determine_recovery()

    assert result.action is not RecoveryAction.DEGRADED
    assert result.action is not RecoveryAction.STOP
