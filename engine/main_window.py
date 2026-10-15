from PySide6.QtCore import QThread
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
from engine.dashboard_diagnostic_controller import DashboardDiagnosticController
from engine.navigation import NavigationModel
from ui.design_system import DesignSystem
from gui.diagnostic_worker import DiagnosticWorker


class MainWindow(QMainWindow):
    """
    Primary Windows Technician application window.

    The window composes presentation components and navigation.
    It does not perform diagnosis, reasoning, authorization,
    remediation, or execution.
    """

    def __init__(self, application_state, parent=None):
        super().__init__(parent)

        self.design_system = DesignSystem()
        self.setStyleSheet(self.design_system.stylesheet())

        if application_state is None:
            raise ValueError("application_state is required.")

        self.application_state = application_state
        self.navigation = NavigationModel()
        self.diagnostic_controller = DashboardDiagnosticController()
        self._diagnostic_thread = None
        self._diagnostic_worker = None

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
        self.dashboard.diagnostics_requested.connect(
            self.run_diagnostics
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

    def run_diagnostics(self):
        """Start diagnostics in a worker thread without blocking the UI."""
        if self._diagnostic_thread is not None:
            return

        self.dashboard.set_diagnostics_running(True)
        self.dashboard.set_diagnostics_status(
            "Diagnostics are running across the registered Windows domains. "
            "You can continue using the application while they run."
        )

        thread = QThread(self)
        worker = DiagnosticWorker(self.diagnostic_controller)
        worker.moveToThread(thread)

        thread.started.connect(worker.run)
        worker.result.connect(self._on_diagnostics_result)
        worker.error_details.connect(self._on_diagnostics_error)

        # The worker signals completion on both success and failure.
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)

        thread.finished.connect(self._on_diagnostic_thread_finished)
        thread.finished.connect(thread.deleteLater)

        self._diagnostic_thread = thread
        self._diagnostic_worker = worker

        thread.start()

    def _on_diagnostics_result(self, outcome):
        """Apply worker results on the main/UI thread."""
        try:
            if not isinstance(outcome, dict):
                raise TypeError(
                    "The diagnostic controller returned an invalid result."
                )

            intelligence = outcome["intelligence"]
            completed = outcome["domains_completed"]
            requested = len(outcome["domains_requested"])
            failures = len(outcome["failures"])

            self.dashboard_view_model.update_intelligence(intelligence)
            self.refresh_dashboard()

            if not outcome["success"]:
                message = (
                    "Diagnostics could not produce a successful result. "
                    f"{completed} of {requested} domains completed; "
                    f"{failures} domain failures. No repairs were executed."
                )
            elif outcome["partial"]:
                message = (
                    "Diagnostics completed with some domain failures. "
                    f"{completed} of {requested} domains completed; "
                    f"{failures} failed. Review the available findings. "
                    "No repairs were executed."
                )
            else:
                message = (
                    "Diagnostics completed successfully across "
                    f"{completed} registered domains. "
                    "Review the findings and recommendations below. "
                    "No repairs were executed."
                )

            self.dashboard.set_diagnostics_status(message)

        except Exception as exc:
            self.dashboard.set_diagnostics_status(
                "Diagnostic results could not be displayed. "
                f"{type(exc).__name__}: {exc}"
            )

    def _on_diagnostics_error(self, message):
        """Display worker errors on the main/UI thread."""
        self.dashboard.set_diagnostics_status(
            "Diagnostics could not be completed. "
            f"{message} No repairs were executed."
        )

    def _on_diagnostic_thread_finished(self):
        """Release thread references and restore the dashboard control."""
        self._diagnostic_worker = None
        self._diagnostic_thread = None
        self.dashboard.set_diagnostics_running(False)
        self._configure_keyboard_navigation()

    def closeEvent(self, event):
        "Prevent closing the window while background diagnostics are active."
        thread = getattr(self, "_diagnostic_thread", None)
        if thread is not None and thread.isRunning():
            try:
                self.dashboard.set_diagnostics_status(
                    "Diagnostics are still running. Please wait before closing."
                )
            except Exception:
                pass
            event.ignore()
            return
        event.accept()

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
