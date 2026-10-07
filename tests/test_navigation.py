import pytest

from engine.application_bootstrap import (
    ApplicationBootstrap,
)
from engine.navigation import (
    MainWindowController,
    NavigationModel,
)


def test_navigation_defaults_to_dashboard():
    navigation = NavigationModel()

    assert navigation.current_page == "DASHBOARD"


def test_navigation_exposes_expected_pages():
    assert NavigationModel.pages() == (
        "DASHBOARD",
        "MACHINES",
        "DIAGNOSTICS",
        "CASES",
        "REMEDIATION",
        "INTELLIGENCE",
        "SETTINGS",
    )


@pytest.mark.parametrize(
    "page",
    [
        "DASHBOARD",
        "MACHINES",
        "DIAGNOSTICS",
        "CASES",
        "REMEDIATION",
        "INTELLIGENCE",
        "SETTINGS",
    ],
)
def test_supported_pages(page):
    navigation = NavigationModel(
        page
    )

    assert navigation.current_page == page


def test_page_is_normalized():
    navigation = NavigationModel(
        " diagnostics "
    )

    assert navigation.current_page == "DIAGNOSTICS"


def test_invalid_page_is_rejected():
    with pytest.raises(ValueError):
        NavigationModel("UNKNOWN")


def test_non_string_page_is_rejected():
    with pytest.raises(ValueError):
        NavigationModel(123)


def test_navigate_changes_current_page():
    navigation = NavigationModel()

    result = navigation.navigate(
        "MACHINES"
    )

    assert result == "MACHINES"
    assert navigation.current_page == "MACHINES"


def test_navigate_normalizes_page():
    navigation = NavigationModel()

    navigation.navigate(
        " intelligence "
    )

    assert navigation.current_page == "INTELLIGENCE"


def test_navigate_invalid_page_is_rejected():
    navigation = NavigationModel()

    with pytest.raises(ValueError):
        navigation.navigate("INVALID")


def test_is_current():
    navigation = NavigationModel(
        "CASES"
    )

    assert navigation.is_current("cases")
    assert not navigation.is_current(
        "dashboard"
    )


def test_to_dict_contains_navigation_state():
    navigation = NavigationModel(
        "SETTINGS"
    )

    assert navigation.to_dict() == {
        "pages": [
            "DASHBOARD",
            "MACHINES",
            "DIAGNOSTICS",
            "CASES",
            "REMEDIATION",
            "INTELLIGENCE",
            "SETTINGS",
        ],
        "current_page": "SETTINGS",
    }


def test_controller_requires_application_state():
    with pytest.raises(ValueError):
        MainWindowController(None)


def test_controller_uses_default_navigation():
    bootstrap = ApplicationBootstrap()

    controller = MainWindowController(
        bootstrap.state
    )

    assert controller.current_page == "DASHBOARD"


def test_controller_accepts_custom_navigation():
    bootstrap = ApplicationBootstrap()
    navigation = NavigationModel(
        "INTELLIGENCE"
    )

    controller = MainWindowController(
        bootstrap.state,
        navigation,
    )

    assert controller.current_page == (
        "INTELLIGENCE"
    )


def test_controller_is_hidden_by_default():
    bootstrap = ApplicationBootstrap()

    controller = MainWindowController(
        bootstrap.state
    )

    assert controller.visible is False


def test_show_makes_controller_visible():
    bootstrap = ApplicationBootstrap()

    controller = MainWindowController(
        bootstrap.state
    )

    result = controller.show()

    assert result is True
    assert controller.visible is True


def test_hide_makes_controller_hidden():
    bootstrap = ApplicationBootstrap()

    controller = MainWindowController(
        bootstrap.state
    )

    controller.show()
    result = controller.hide()

    assert result is False
    assert controller.visible is False


def test_controller_navigation():
    bootstrap = ApplicationBootstrap()

    controller = MainWindowController(
        bootstrap.state
    )

    result = controller.navigate(
        "DIAGNOSTICS"
    )

    assert result == "DIAGNOSTICS"
    assert controller.current_page == (
        "DIAGNOSTICS"
    )


def test_controller_navigation_rejects_invalid_page():
    bootstrap = ApplicationBootstrap()

    controller = MainWindowController(
        bootstrap.state
    )

    with pytest.raises(ValueError):
        controller.navigate(
            "NOT_A_PAGE"
        )


def test_controller_to_dict():
    bootstrap = ApplicationBootstrap()

    controller = MainWindowController(
        bootstrap.state
    )

    controller.show()
    controller.navigate(
        "MACHINES"
    )

    data = controller.to_dict()

    assert data["visible"] is True
    assert data["current_page"] == "MACHINES"
    assert data["application"]["version"] == "0.9.0"


def test_navigation_has_no_execution_surface():
    navigation = NavigationModel()

    assert not hasattr(
        navigation,
        "execute",
    )
    assert not hasattr(
        navigation,
        "diagnose",
    )
    assert not hasattr(
        navigation,
        "remediate",
    )


def test_controller_has_no_execution_surface():
    bootstrap = ApplicationBootstrap()

    controller = MainWindowController(
        bootstrap.state
    )

    assert not hasattr(
        controller,
        "execute",
    )
    assert not hasattr(
        controller,
        "diagnose",
    )
    assert not hasattr(
        controller,
        "remediate",
    )


def test_controller_preserves_application_state():
    bootstrap = ApplicationBootstrap()

    controller = MainWindowController(
        bootstrap.state
    )

    assert (
        controller.application_state
        is bootstrap.state
    )


def test_controller_can_navigate_all_pages():
    bootstrap = ApplicationBootstrap()

    controller = MainWindowController(
        bootstrap.state
    )

    for page in NavigationModel.pages():
        assert (
            controller.navigate(page)
            == page
        )
