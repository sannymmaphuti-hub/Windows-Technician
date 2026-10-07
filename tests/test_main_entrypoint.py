import importlib

import pytest

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication

from engine.application_bootstrap import ApplicationBootstrap
from engine.main_window import MainWindow


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()

    if app is None:
        app = QApplication([])

    return app


def test_main_module_imports():
    module = importlib.import_module("main")

    assert hasattr(module, "create_application")
    assert hasattr(module, "start_application")
    assert hasattr(module, "main")


def test_create_application_returns_qt_and_bootstrap(qapp):
    import main

    qt_application, bootstrap = main.create_application()

    assert isinstance(qt_application, QApplication)
    assert isinstance(bootstrap, ApplicationBootstrap)


def test_start_application_creates_window(qapp):
    import main

    qt_application, bootstrap, window = main.start_application()

    assert isinstance(qt_application, QApplication)
    assert isinstance(bootstrap, ApplicationBootstrap)
    assert isinstance(window, MainWindow)

    assert bootstrap.state is window.application_state
    assert bootstrap.state.status == "READY"
    assert window.current_page() == "DASHBOARD"

    window.close()
    bootstrap.stop()


def test_start_application_creates_dashboard(qapp):
    import main

    _, bootstrap, window = main.start_application()

    assert window.dashboard is not None
    assert window.dashboard.view_model.application_state is (
        window.application_state
    )

    window.close()
    bootstrap.stop()


def test_startup_sequence_is_ready_before_window_use(qapp):
    import main

    _, bootstrap, window = main.start_application()

    assert bootstrap.state.status == "READY"
    assert window.application_state.status == "READY"

    window.close()
    bootstrap.stop()


def test_main_module_exposes_no_diagnostic_execution_logic():
    import main

    declared_names = set(main.__dict__)

    forbidden = (
        "diagnose",
        "analyze",
        "recommend",
        "remediate",
        "execute",
        "authorize",
    )

    for name in forbidden:
        assert not any(
            name in attribute.lower()
            for attribute in declared_names
        )


def test_start_application_does_not_run_diagnostics(qapp):
    import main

    _, bootstrap, window = main.start_application()

    assert window.dashboard_view_model.intelligence == {}

    window.close()
    bootstrap.stop()
