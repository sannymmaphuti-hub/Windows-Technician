from packaging.application_lifecycle import ApplicationLifecycleState
from packaging.application_services import (
    ApplicationServiceName,
    ApplicationServiceState,
)

import main


def _fake_window(monkeypatch):
    class FakeWindow:
        shown = False

        def show(self):
            self.shown = True

    window = FakeWindow()

    monkeypatch.setattr(
        main,
        "create_main_window",
        lambda state: window,
    )

    return window


def test_main_startup_reaches_running_runtime(qapp, monkeypatch):
    window = _fake_window(monkeypatch)

    qt_application, bootstrap, returned_window = main.start_application()

    assert qt_application is qapp
    assert returned_window is window
    assert window.shown is True
    assert bootstrap.started is True
    assert (
        bootstrap.runtime.lifecycle.state
        is ApplicationLifecycleState.RUNNING
    )


def test_main_startup_reaches_ready_application_state(qapp, monkeypatch):
    _fake_window(monkeypatch)

    _, bootstrap, _ = main.start_application()

    assert bootstrap.state.status == "READY"


def test_main_startup_has_all_services_running(qapp, monkeypatch):
    _fake_window(monkeypatch)

    _, bootstrap, _ = main.start_application()

    for name in ApplicationServiceName:
        assert (
            bootstrap.service_state(name)
            is ApplicationServiceState.RUNNING
        )


def test_main_shutdown_reaches_stopped_runtime(qapp, monkeypatch):
    _fake_window(monkeypatch)

    _, bootstrap, _ = main.start_application()

    state = bootstrap.stop()

    assert bootstrap.started is False
    assert state.status == "STOPPED"
    assert (
        bootstrap.runtime.lifecycle.state
        is ApplicationLifecycleState.STOPPED
    )


def test_main_shutdown_stops_all_services(qapp, monkeypatch):
    _fake_window(monkeypatch)

    _, bootstrap, _ = main.start_application()

    bootstrap.stop()

    for name in ApplicationServiceName:
        assert (
            bootstrap.service_state(name)
            is ApplicationServiceState.STOPPED
        )


def test_main_runtime_can_restart_after_shutdown(qapp, monkeypatch):
    _fake_window(monkeypatch)

    _, bootstrap, _ = main.start_application()

    first_runtime = bootstrap.runtime

    bootstrap.stop()
    bootstrap.start()

    second_runtime = bootstrap.runtime

    assert first_runtime is not second_runtime
    assert bootstrap.started is True
    assert (
        second_runtime.lifecycle.state
        is ApplicationLifecycleState.RUNNING
    )


def test_restart_restores_all_services(qapp, monkeypatch):
    _fake_window(monkeypatch)

    _, bootstrap, _ = main.start_application()

    bootstrap.stop()
    bootstrap.start()

    for name in ApplicationServiceName:
        assert (
            bootstrap.service_state(name)
            is ApplicationServiceState.RUNNING
        )
