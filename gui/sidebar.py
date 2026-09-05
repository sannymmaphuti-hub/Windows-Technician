from PySide6.QtWidgets import (
    QVBoxLayout,
    QWidget,
    QPushButton,
)


class SidebarWidget(QWidget):
    def __init__(self, technician_app):
        super().__init__()

        self.technician_app = technician_app

        self.setMinimumWidth(200)

        self.navigation_items = [
            "Dashboard",
            "Diagnostics",
            "Reports",
            "Settings",
        ]

        self.current_navigation = "Dashboard"

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.navigation_buttons = {}

        for item in self.navigation_items:
            button = QPushButton(item)

            self.navigation_buttons[item] = button

            button.clicked.connect(
                lambda checked=False, name=item:
                self._select_navigation(name)
            )

            layout.addWidget(button)

    def _select_navigation(self, name):
        self.current_navigation = name