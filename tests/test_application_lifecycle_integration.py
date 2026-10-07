import pytest

from packaging.application_lifecycle import (
    ApplicationLifecycleState,
    create_application_lifecycle,
)
from packaging.application_lifecycle_integration import (
    LifecycleRecoveryDecision,
    apply_recovery_action,
    start_application,
    stop_application,
)
from packaging.runtime_recovery import RecoveryAction


def test_start_application_enters_starting():
    lifecycle = start_application(
        create_application_lifecycle()
    )

    assert lifecycle.state is ApplicationLifecycleState.STARTING


def test_continue_completes_startup():
    lifecycle = start_application(
        create_application_lifecycle()
    )

    result = apply_recovery_action(
        lifecycle,
        RecoveryAction.CONTINUE,
    )

    assert result.lifecycle.state is ApplicationLifecycleState.RUNNING
    assert result.lifecycle.startup_completed is True
    assert result.should_continue is True


def test_degraded_recovery_enters_degraded():
    lifecycle = start_application(
        create_application_lifecycle()
    )

    result = apply_recovery_action(
        lifecycle,
        RecoveryAction.DEGRADED,
    )

    assert result.lifecycle.state is ApplicationLifecycleState.DEGRADED
    assert result.should_continue is True


def test_stop_recovery_does_not_continue():
    lifecycle = start_application(
        create_application_lifecycle()
    )

    result = apply_recovery_action(
        lifecycle,
        RecoveryAction.STOP,
    )

    assert result.lifecycle.state is ApplicationLifecycleState.STARTING
    assert result.should_continue is False


def test_stop_application():
    lifecycle = start_application(
        create_application_lifecycle()
    )

    lifecycle = apply_recovery_action(
        lifecycle,
        RecoveryAction.CONTINUE,
    ).lifecycle

    lifecycle = stop_application(lifecycle)

    assert lifecycle.state is ApplicationLifecycleState.STOPPED
    assert lifecycle.shutdown_completed is True


def test_recovery_decision_is_frozen():
    lifecycle = start_application(
        create_application_lifecycle()
    )

    result = apply_recovery_action(
        lifecycle,
        RecoveryAction.CONTINUE,
    )

    with pytest.raises(AttributeError):
        result.should_continue = False


def test_invalid_lifecycle_is_rejected():
    with pytest.raises(TypeError):
        start_application(None)


def test_invalid_recovery_action_is_rejected():
    lifecycle = start_application(
        create_application_lifecycle()
    )

    with pytest.raises(TypeError):
        apply_recovery_action(
            lifecycle,
            "continue",
        )


def test_invalid_recovery_decision_type_is_rejected():
    with pytest.raises(TypeError):
        LifecycleRecoveryDecision(
            lifecycle=None,
            recovery_action=RecoveryAction.CONTINUE,
            should_continue=True,
        )
