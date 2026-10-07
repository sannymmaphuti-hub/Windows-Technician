from packaging.application_lifecycle import ApplicationLifecycleState
from packaging.application_services import (
    ApplicationServiceName,
    ApplicationServiceState,
)

from engine.application_bootstrap import ApplicationBootstrap


def test_bootstrap_owns_production_runtime():
    bootstrap = ApplicationBootstrap()

    assert bootstrap.runtime is not None
    assert bootstrap.runtime.lifecycle.state is ApplicationLifecycleState.CREATED


def test_bootstrap_start_transitions_production_runtime():
    bootstrap = ApplicationBootstrap()

    state = bootstrap.start()

    assert bootstrap.started is True
    assert state.status == "READY"
    assert (
        bootstrap.runtime.lifecycle.state
        is ApplicationLifecycleState.RUNNING
    )


def test_bootstrap_start_starts_all_application_services():
    bootstrap = ApplicationBootstrap()

    bootstrap.start()

    for name in ApplicationServiceName:
        assert (
            bootstrap.service_state(name)
            is ApplicationServiceState.RUNNING
        )


def test_bootstrap_start_is_idempotent():
    bootstrap = ApplicationBootstrap()

    first = bootstrap.start()
    runtime = bootstrap.runtime
    second = bootstrap.start()

    assert second is first
    assert bootstrap.runtime is runtime
    assert bootstrap.started is True


def test_bootstrap_stop_stops_production_runtime():
    bootstrap = ApplicationBootstrap()

    bootstrap.start()
    state = bootstrap.stop()

    assert bootstrap.started is False
    assert state.status == "STOPPED"
    assert (
        bootstrap.runtime.lifecycle.state
        is ApplicationLifecycleState.STOPPED
    )


def test_bootstrap_stop_stops_all_application_services():
    bootstrap = ApplicationBootstrap()

    bootstrap.start()
    bootstrap.stop()

    for name in ApplicationServiceName:
        assert (
            bootstrap.service_state(name)
            is ApplicationServiceState.STOPPED
        )


def test_bootstrap_stop_before_start_preserves_safe_behavior():
    bootstrap = ApplicationBootstrap()

    state = bootstrap.stop()

    assert bootstrap.started is False
    assert state.status == "STOPPED"
    assert (
        bootstrap.runtime.lifecycle.state
        is ApplicationLifecycleState.CREATED
    )


def test_bootstrap_failure_does_not_start_runtime():
    bootstrap = ApplicationBootstrap()

    state = bootstrap.fail()

    assert bootstrap.started is False
    assert state.status == "ERROR"
    assert (
        bootstrap.runtime.lifecycle.state
        is ApplicationLifecycleState.CREATED
    )
