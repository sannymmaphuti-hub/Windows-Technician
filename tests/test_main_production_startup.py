"""Tests for the production application entry point."""

from pathlib import Path

import main

from packaging.application_lifecycle import ApplicationLifecycleState

from packaging.application_lifecycle import (
    ApplicationLifecycleState,
)


def test_project_root_resolves_to_application_root():
    root = main._project_root()

    assert isinstance(root, Path)
    assert root == Path(main.__file__).resolve().parent


def test_create_application_builds_production_bootstrap(monkeypatch, tmp_path):
    monkeypatch.setenv(
        "LOCALAPPDATA",
        str(tmp_path / "localappdata"),
    )

    qt_application, bootstrap = main.create_application()

    assert qt_application is not None
    assert bootstrap.application_name == main.APP_NAME
    assert bootstrap.version == main.APP_VERSION
    assert bootstrap.configuration is not None
    assert bootstrap.operational_state is not None
    assert bootstrap.operational_logger is not None


def test_create_application_uses_safe_production_configuration(
    monkeypatch,
    tmp_path,
):
    monkeypatch.setenv(
        "LOCALAPPDATA",
        str(tmp_path / "localappdata"),
    )

    _, bootstrap = main.create_application()

    assert bootstrap.configuration is not None
    assert bootstrap.configuration.state.safe is True
    assert bootstrap.startup_allowed is True


def test_create_application_wires_operational_log_path(
    monkeypatch,
    tmp_path,
):
    monkeypatch.setenv(
        "LOCALAPPDATA",
        str(tmp_path / "localappdata"),
    )

    _, bootstrap = main.create_application()

    logger = bootstrap.operational_logger

    assert logger is not None
    assert logger.logger.log_path == (
        tmp_path
        / "localappdata"
        / "WindowsTechnician"
        / "logs"
        / "application.log"
    )


def test_start_application_reaches_running_state(
    monkeypatch,
    tmp_path,
):
    monkeypatch.setenv(
        "LOCALAPPDATA",
        str(tmp_path / "localappdata"),
    )

    _, bootstrap, window = main.start_application()

    assert bootstrap.started is True
    assert bootstrap.runtime.lifecycle.state is (
        ApplicationLifecycleState.RUNNING
    )
    assert window is not None

    window.close()
    bootstrap.stop()


def test_blocked_start_does_not_create_window(
    monkeypatch,
    tmp_path,
):
    monkeypatch.setenv(
        "LOCALAPPDATA",
        str(tmp_path / "localappdata"),
    )

    class UnsafeBootstrap:
        started = False

        def start(self):
            return None

    monkeypatch.setattr(
        main,
        "ApplicationBootstrap",
        lambda **kwargs: UnsafeBootstrap(),
    )

    _, bootstrap, window = main.start_application()

    assert bootstrap.started is False
    assert window is None

def test_runtime_is_translated_to_application_state():
    class Lifecycle:
        state = ApplicationLifecycleState.RUNNING

    class Runtime:
        lifecycle = Lifecycle()

    state = main._application_state_from_runtime(
        Runtime()
    )

    assert state.application_name == main.APP_NAME
    assert state.version == main.APP_VERSION
    assert state.status == "READY"
    assert state.active_case_id is None
    assert state.active_machine_id is None


def test_runtime_configuration_is_exposed_to_application_state():
    class ConfigurationState:
        configuration = {
            "version": 1,
            "diagnostics": {
                "automatic_collection": True,
            },
        }

    class Configuration:
        state = ConfigurationState()

    class Lifecycle:
        state = ApplicationLifecycleState.RUNNING

    class Runtime:
        lifecycle = Lifecycle()

    state = main._application_state_from_runtime(
        Runtime(),
        configuration=Configuration(),
    )

    assert state.configuration["version"] == 1
    assert (
        state.configuration["diagnostics"]
        ["automatic_collection"]
        is True
    )
