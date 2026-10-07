import pytest

from packaging.application_lifecycle import (
    ApplicationLifecycle,
    ApplicationLifecycleState,
    begin_shutdown,
    begin_startup,
    complete_shutdown,
    complete_startup,
    create_application_lifecycle,
    enter_degraded,
)


def test_initial_state_is_created():
    lifecycle = create_application_lifecycle()

    assert lifecycle.state is ApplicationLifecycleState.CREATED
    assert lifecycle.startup_completed is False
    assert lifecycle.shutdown_completed is False


def test_startup_transition():
    lifecycle = create_application_lifecycle()

    lifecycle = begin_startup(lifecycle)

    assert lifecycle.state is ApplicationLifecycleState.STARTING


def test_startup_completion():
    lifecycle = begin_startup(create_application_lifecycle())
    lifecycle = complete_startup(lifecycle)

    assert lifecycle.state is ApplicationLifecycleState.RUNNING
    assert lifecycle.startup_completed is True


def test_degraded_transition_from_running():
    lifecycle = complete_startup(
        begin_startup(create_application_lifecycle())
    )

    lifecycle = enter_degraded(lifecycle)

    assert lifecycle.state is ApplicationLifecycleState.DEGRADED
    assert lifecycle.startup_completed is True


def test_degraded_transition_from_starting():
    lifecycle = begin_startup(create_application_lifecycle())

    lifecycle = enter_degraded(lifecycle)

    assert lifecycle.state is ApplicationLifecycleState.DEGRADED
    assert lifecycle.startup_completed is False


def test_shutdown_transition():
    lifecycle = complete_startup(
        begin_startup(create_application_lifecycle())
    )

    lifecycle = begin_shutdown(lifecycle)

    assert lifecycle.state is ApplicationLifecycleState.STOPPING


def test_shutdown_completion():
    lifecycle = complete_startup(
        begin_startup(create_application_lifecycle())
    )

    lifecycle = complete_shutdown(
        begin_shutdown(lifecycle)
    )

    assert lifecycle.state is ApplicationLifecycleState.STOPPED
    assert lifecycle.shutdown_completed is True


def test_failed_application_can_shutdown():
    lifecycle = ApplicationLifecycle(
        state=ApplicationLifecycleState.FAILED,
    )

    lifecycle = begin_shutdown(lifecycle)

    assert lifecycle.state is ApplicationLifecycleState.STOPPING


def test_invalid_startup_transition_is_rejected():
    lifecycle = ApplicationLifecycle(
        state=ApplicationLifecycleState.RUNNING,
    )

    with pytest.raises(ValueError):
        begin_startup(lifecycle)


def test_invalid_startup_completion_is_rejected():
    lifecycle = create_application_lifecycle()

    with pytest.raises(ValueError):
        complete_startup(lifecycle)


def test_invalid_shutdown_transition_is_rejected():
    lifecycle = create_application_lifecycle()

    with pytest.raises(ValueError):
        begin_shutdown(lifecycle)


def test_invalid_shutdown_completion_is_rejected():
    lifecycle = create_application_lifecycle()

    with pytest.raises(ValueError):
        complete_shutdown(lifecycle)


def test_lifecycle_is_frozen():
    lifecycle = create_application_lifecycle()

    with pytest.raises(AttributeError):
        lifecycle.state = ApplicationLifecycleState.RUNNING


def test_invalid_lifecycle_type_is_rejected():
    with pytest.raises(TypeError):
        ApplicationLifecycle(
            state="running",
        )


def test_invalid_startup_flag_is_rejected():
    with pytest.raises(TypeError):
        ApplicationLifecycle(
            state=ApplicationLifecycleState.CREATED,
            startup_completed="yes",
        )


def test_invalid_shutdown_flag_is_rejected():
    with pytest.raises(TypeError):
        ApplicationLifecycle(
            state=ApplicationLifecycleState.CREATED,
            shutdown_completed="yes",
        )
