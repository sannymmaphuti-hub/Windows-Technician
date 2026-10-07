import pytest

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication

from engine.application_state import ApplicationState
from engine.main_window import MainWindow, create_main_window


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()

    if app is None:
        app = QApplication([])

    return app


def test_main_window_requires_application_state(qapp):
    with pytest.raises(ValueError):
        MainWindow(None)


def test_main_window_starts_on_dashboard(qapp):
    state = ApplicationState()

    window = MainWindow(state)

    assert window.current_page() == "DASHBOARD"
    assert window.pages.currentWidget() is window.dashboard


def test_main_window_contains_dashboard(qapp):
    state = ApplicationState()

    window = MainWindow(state)

    assert window.dashboard is not None
    assert window.dashboard.view_model is window.dashboard_view_model


def test_dashboard_uses_application_state(qapp):
    state = ApplicationState()
    state.set_active_machine("MACHINE-001")
    state.set_active_case("CASE-001")

    window = MainWindow(state)

    assert window.dashboard.view_model.application_state is state


def test_main_window_navigation_uses_navigation_model(qapp):
    state = ApplicationState()

    window = MainWindow(state)

    assert window.navigation.current_page == "DASHBOARD"

    result = window.navigate("dashboard")

    assert result == "DASHBOARD"
    assert window.current_page() == "DASHBOARD"


def test_main_window_dashboard_refresh(qapp):
    state = ApplicationState()

    window = MainWindow(state)

    window.dashboard_view_model.update_intelligence(
        {
            "health": {
                "status": "WARNING",
                "score": 74,
            },
            "system_findings": [
                {"title": "High memory pressure"},
            ],
        }
    )

    window.refresh_dashboard()

    assert window.dashboard.health_status_label.value_label.text() == "WARNING"
    assert window.dashboard.health_score_label.value_label.text() == "74"
    assert window.dashboard.findings_label.value_label.text() == "1"


def test_main_window_to_dict(qapp):
    state = ApplicationState()

    window = MainWindow(state)

    data = window.to_dict()

    assert data["window"] == "Windows Technician"
    assert data["current_page"] == "DASHBOARD"
    assert "dashboard" in data


def test_factory_creates_main_window(qapp):
    state = ApplicationState()

    window = create_main_window(state)

    assert isinstance(window, MainWindow)


def test_main_window_has_no_execution_surface(qapp):
    state = ApplicationState()

    window = MainWindow(state)

    declared_names = set(window.__class__.__dict__)

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
