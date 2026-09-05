from PySide6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QWidget,
)

from gui.dashboard import DashboardWidget
from gui.sidebar import SidebarWidget
from gui.styles import APPLICATION_STYLE


class TechnicianMainWindow(QMainWindow):
    def __init__(self, technician_app):
        super().__init__()

        self.technician_app = technician_app

        self.setWindowTitle("Windows Technician")
        self.setMinimumSize(1000, 650)

        self.setStyleSheet(APPLICATION_STYLE)

        self.sidebar = SidebarWidget(
            self.technician_app
        )

        self.dashboard = DashboardWidget(
            self.technician_app
        )

        central_widget = QWidget()
        layout = QHBoxLayout()

        layout.addWidget(self.sidebar)
        layout.addWidget(self.dashboard)

        central_widget.setLayout(layout)

        self.setCentralWidget(central_widget)