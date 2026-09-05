from application.app import TechnicianApp
from gui.sidebar import SidebarWidget


def test_sidebar_can_be_created(qtbot):
    app = TechnicianApp()

    sidebar = SidebarWidget(app)

    qtbot.addWidget(sidebar)

    assert sidebar is not None


def test_sidebar_receives_technician_app(qtbot):
    app = TechnicianApp()

    sidebar = SidebarWidget(app)

    qtbot.addWidget(sidebar)

    assert sidebar.technician_app is app


def test_sidebar_has_layout(qtbot):
    app = TechnicianApp()

    sidebar = SidebarWidget(app)

    qtbot.addWidget(sidebar)

    assert sidebar.layout() is not None


def test_sidebar_has_reasonable_minimum_width(qtbot):
    app = TechnicianApp()

    sidebar = SidebarWidget(app)

    qtbot.addWidget(sidebar)

    assert sidebar.minimumWidth() >= 200

def test_sidebar_has_navigation_items(qtbot):
    app = TechnicianApp()

    sidebar = SidebarWidget(app)

    qtbot.addWidget(sidebar)

    assert sidebar.navigation_items == [
        "Dashboard",
        "Diagnostics",
        "Reports",
        "Settings",
    ]


def test_sidebar_has_dashboard_as_default_navigation(qtbot):
    app = TechnicianApp()

    sidebar = SidebarWidget(app)

    qtbot.addWidget(sidebar)

    assert sidebar.current_navigation == "Dashboard"

def test_sidebar_has_navigation_buttons(qtbot):
    app = TechnicianApp()

    sidebar = SidebarWidget(app)

    qtbot.addWidget(sidebar)

    assert list(sidebar.navigation_buttons.keys()) == [
        "Dashboard",
        "Diagnostics",
        "Reports",
        "Settings",
    ]


def test_sidebar_navigation_buttons_have_matching_labels(qtbot):
    app = TechnicianApp()

    sidebar = SidebarWidget(app)

    qtbot.addWidget(sidebar)

    for name, button in sidebar.navigation_buttons.items():
        assert button.text() == name

def test_sidebar_clicking_diagnostics_changes_navigation(qtbot):
    app = TechnicianApp()

    sidebar = SidebarWidget(app)

    qtbot.addWidget(sidebar)

    sidebar.navigation_buttons["Diagnostics"].click()

    assert sidebar.current_navigation == "Diagnostics"


def test_sidebar_clicking_reports_changes_navigation(qtbot):
    app = TechnicianApp()

    sidebar = SidebarWidget(app)

    qtbot.addWidget(sidebar)

    sidebar.navigation_buttons["Reports"].click()

    assert sidebar.current_navigation == "Reports"


def test_sidebar_clicking_settings_changes_navigation(qtbot):
    app = TechnicianApp()

    sidebar = SidebarWidget(app)

    qtbot.addWidget(sidebar)

    sidebar.navigation_buttons["Settings"].click()

    assert sidebar.current_navigation == "Settings"