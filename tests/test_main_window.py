from application.app import TechnicianApp
from gui.main_window import TechnicianMainWindow


def test_main_window_can_be_created(qtbot):
    app = TechnicianApp()

    window = TechnicianMainWindow(app)

    qtbot.addWidget(window)

    assert window is not None


def test_main_window_receives_technician_app(qtbot):
    app = TechnicianApp()

    window = TechnicianMainWindow(app)

    qtbot.addWidget(window)

    assert window.technician_app is app

def test_main_window_has_application_title(qtbot):
    app = TechnicianApp()

    window = TechnicianMainWindow(app)

    qtbot.addWidget(window)

    assert window.windowTitle() == "Windows Technician"


def test_main_window_has_reasonable_initial_size(qtbot):
    app = TechnicianApp()

    window = TechnicianMainWindow(app)

    qtbot.addWidget(window)

    assert window.minimumWidth() >= 1000
    assert window.minimumHeight() >= 650


def test_main_window_has_central_widget(qtbot):
    app = TechnicianApp()

    window = TechnicianMainWindow(app)

    qtbot.addWidget(window)

    assert window.centralWidget() is not None

def test_main_window_contains_dashboard(qtbot):
    app = TechnicianApp()

    window = TechnicianMainWindow(app)

    qtbot.addWidget(window)

    assert window.dashboard is not None

def test_main_window_contains_sidebar(qtbot):
    app = TechnicianApp()

    window = TechnicianMainWindow(app)

    qtbot.addWidget(window)

    assert window.sidebar is not None

def test_main_window_shell_contains_sidebar_and_dashboard(qtbot):
    app = TechnicianApp()

    window = TechnicianMainWindow(app)

    qtbot.addWidget(window)

    central_widget = window.centralWidget()
    layout = central_widget.layout()

    assert layout is not None
    assert layout.indexOf(window.sidebar) != -1
    assert layout.indexOf(window.dashboard) != -1

def test_main_window_applies_application_style(qtbot):
    app = TechnicianApp()

    window = TechnicianMainWindow(app)
    qtbot.addWidget(window)

    stylesheet = window.styleSheet()

    assert stylesheet
    assert "statusSeverity" in stylesheet