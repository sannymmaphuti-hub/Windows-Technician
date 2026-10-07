from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QStackedWidget,
    QWidget,
    QVBoxLayout,
)

from engine.accessibility import AccessibilityHelper
from engine.keyboard_navigation import KeyboardNavigation
from engine.dashboard_view_model import DashboardViewModel
from engine.dashboard_widget import DashboardWidget
from engine.navigation import NavigationModel


class MainWindow(QMainWindow):
    """
    Primary Windows Technician application window.

    The window composes presentation components and navigation.
    It does not perform diagnosis, reasoning, authorization,
    remediation, or execution.
    """

    def __init__(self, application_state, parent=None):
        super().__init__(parent)

        if application_state is None:
            raise ValueError("application_state is required.")

        self.application_state = application_state
        self.navigation = NavigationModel()

        self.setWindowTitle("Windows Technician")
        self.resize(1100, 700)
        self.setMinimumSize(640, 480)

        AccessibilityHelper.describe(
            self,
            "Windows Technician main window",
            "Primary application window for Windows Technician.",
        )

        self._build_ui()
        self.navigate("DASHBOARD")

    def _build_ui(self):
        central = QWidget()
        AccessibilityHelper.describe(
            central,
            "Windows Technician application content",
            "Main content area of the Windows Technician application.",
        )

        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)

        self.pages = QStackedWidget()
        AccessibilityHelper.describe(
            self.pages,
            "Application pages",
            "Current Windows Technician application page.",
        )

        self.dashboard_view_model = DashboardViewModel(
            self.application_state
        )

        self.dashboard = DashboardWidget(
            self.dashboard_view_model
        )

        self.pages.addWidget(self.dashboard)

        layout.addWidget(self.pages)

        self._configure_keyboard_navigation()

        self.setCentralWidget(central)

    def _configure_keyboard_navigation(self):
        """
        Establish keyboard navigation for the currently available
        application controls.

        Navigation remains presentation-only.
        """
        review_buttons = [
            card.review_button
            for card in self.dashboard.remediation_widgets.cards()
            if card.review_button.isEnabled()
        ]

        KeyboardNavigation.set_tab_order(
            review_buttons
        )

    def navigate(self, page):
        normalized = self.navigation.navigate(page)

        if normalized == "DASHBOARD":
            self.pages.setCurrentWidget(self.dashboard)

        return normalized

    def current_page(self):
        return self.navigation.current_page

    def refresh_dashboard(self):
        self.dashboard.refresh()
        self._configure_keyboard_navigation()

    def to_dict(self):
        return {
            "window": "Windows Technician",
            "current_page": self.current_page(),
            "dashboard": self.dashboard_view_model.to_dict(),
        }


def create_main_window(application_state):
    """
    Create the primary application window.

    QApplication creation remains the responsibility of the
    application entry point.
    """
    return MainWindow(application_state)


