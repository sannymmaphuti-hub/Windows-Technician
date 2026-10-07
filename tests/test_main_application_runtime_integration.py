import pytest

from packaging.application_lifecycle import ApplicationLifecycleState
from packaging.application_metadata import APPLICATION_METADATA
from packaging.application_services import (
    ApplicationServiceName,
    ApplicationServiceState,
)

import main


def test_create_application_uses_canonical_metadata(qapp):
    qt_application, bootstrap = main.create_application()

    assert qt_application is qapp
    assert bootstrap.state.application_name == APPLICATION_METADATA.display_name
    assert bootstrap.state.version == APPLICATION_METADATA.version


def test_create_application_runtime_starts_created(qapp):
    _, bootstrap = main.create_application()

    assert (
        bootstrap.runtime.lifecycle.state
        is ApplicationLifecycleState.CREATED
    )


def test_start_application_starts_production_runtime(qapp, monkeypatch):
    class FakeWindow:
        def __init__(self):
            self.shown = False

        def show(self):
            self.shown = True

    fake_window = FakeWindow()

    monkeypatch.setattr(
        main,
        "create_main_window",
        lambda state: fake_window,
    )

    qt_application, bootstrap, window = main.start_application()

    assert qt_application is qapp
    assert bootstrap.started is True
    assert window is fake_window
    assert window.shown is True
    assert (
        bootstrap.runtime.lifecycle.state
        is ApplicationLifecycleState.RUNNING
    )


def test_start_application_starts_all_production_services(qapp, monkeypatch):
    monkeypatch.setattr(
        main,
        "create_main_window",
        lambda state: type(
            "FakeWindow",
            (),
            {"show": lambda self: None},
        )(),
    )

    _, bootstrap, _ = main.start_application()

    for name in ApplicationServiceName:
        assert (
            bootstrap.service_state(name)
            is ApplicationServiceState.RUNNING
        )


def test_start_application_passes_bootstrap_state_to_main_window(
    qapp,
    monkeypatch,
):
    captured = {}

    class FakeWindow:
        def show(self):
            pass

    def create_window(state):
        captured["state"] = state
        return FakeWindow()

    monkeypatch.setattr(
        main,
        "create_main_window",
        create_window,
    )

    _, bootstrap, _ = main.start_application()

    assert captured["state"] is bootstrap.state
    assert captured["state"].status == "READY"
