from PySide6.QtWidgets import QApplication

from application.app import TechnicianApp
from gui.main_window import TechnicianMainWindow


def test_application_entry_components_can_be_created(qtbot):
    app = TechnicianApp()

    window = TechnicianMainWindow(app)

    qtbot.addWidget(window)

    assert window is not None
    assert window.technician_app is app


def test_qapplication_exists_for_gui_entry_point():
    application = QApplication.instance()

    assert application is not None
