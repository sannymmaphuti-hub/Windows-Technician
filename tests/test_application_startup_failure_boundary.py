from packaging.application_lifecycle import ApplicationLifecycleState
from packaging.application_runtime import (
    ApplicationRuntime,
    create_application_runtime,
)
from packaging.application_services import ApplicationServiceState

from engine.application_bootstrap import ApplicationBootstrap


def test_fresh_bootstrap_is_not_started():
    bootstrap = ApplicationBootstrap()

    assert bootstrap.started is False
    assert bootstrap.state.status == "STARTING"
    assert (
        bootstrap.runtime.lifecycle.state
        is ApplicationLifecycleState.CREATED
    )


def test_failed_bootstrap_does_not_report_running():
    bootstrap = ApplicationBootstrap()

    bootstrap.fail()

    assert bootstrap.started is False
    assert bootstrap.state.status == "ERROR"
    assert (
        bootstrap.runtime.lifecycle.state
        is ApplicationLifecycleState.CREATED
    )


def test_failed_bootstrap_can_recover_with_fresh_start():
    bootstrap = ApplicationBootstrap()

    bootstrap.fail()
    bootstrap.start()

    assert bootstrap.started is True
    assert bootstrap.state.status == "READY"
    assert (
        bootstrap.runtime.lifecycle.state
        is ApplicationLifecycleState.RUNNING
    )


def test_recovered_start_restores_all_services():
    bootstrap = ApplicationBootstrap()

    bootstrap.fail()
    bootstrap.start()

    for service in bootstrap.runtime.services.services:
        assert service.state is ApplicationServiceState.RUNNING


def test_runtime_creation_is_safe_and_does_not_start_services():
    runtime = create_application_runtime()

    assert isinstance(runtime, ApplicationRuntime)
    assert (
        runtime.lifecycle.state
        is ApplicationLifecycleState.CREATED
    )

    for service in runtime.services.services:
        assert service.state is ApplicationServiceState.UNAVAILABLE
