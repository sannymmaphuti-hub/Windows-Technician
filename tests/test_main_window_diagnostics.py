import threading

import pytest

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication

from engine.application_state import ApplicationState
from engine.main_window import MainWindow


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


class FakeDiagnosticController:
    def __init__(self, outcome=None, error=None):
        self.outcome = outcome
        self.error = error
        self.calls = 0

    def run_diagnostics(self):
        self.calls += 1
        if self.error is not None:
            raise self.error
        return self.outcome


@pytest.fixture
def successful_outcome():
    return {
        "success": True,
        "partial": False,
        "domains_requested": ["memory", "storage", "process"],
        "domains_completed": 3,
        "failures": [],
        "workflow_state": "INVESTIGATING",
        "intelligence": {
            "health": {"status": "WARNING", "score": 74},
            "system_findings": [
                {"title": "High memory pressure", "severity": "WARNING"}
            ],
        },
        "summary": "Diagnostics completed.",
    }


def wait_for_completion(qtbot, window):
    qtbot.waitUntil(
        lambda: (
            window._diagnostic_thread is None
            and window.dashboard.run_diagnostics_button.isEnabled()
        ),
        timeout=5000,
    )


def test_dashboard_button_invokes_controller_in_background(
    qapp, qtbot, successful_outcome
):
    window = MainWindow(ApplicationState())
    controller = FakeDiagnosticController(successful_outcome)
    window.diagnostic_controller = controller

    window.dashboard.run_diagnostics_button.click()

    assert not window.dashboard.run_diagnostics_button.isEnabled()

    wait_for_completion(qtbot, window)

    assert controller.calls == 1


def test_successful_diagnostics_update_dashboard(
    qapp, qtbot, successful_outcome
):
    window = MainWindow(ApplicationState())
    window.diagnostic_controller = FakeDiagnosticController(
        successful_outcome
    )

    window.dashboard.run_diagnostics_button.click()
    wait_for_completion(qtbot, window)

    assert window.dashboard.health_status_label.value_label.text() == "WARNING"
    assert window.dashboard.health_score_label.value_label.text() == "74"
    assert window.dashboard.findings_label.value_label.text() == "1"

    status = window.dashboard.diagnostics_status_label.text()
    assert "completed successfully" in status.lower()
    assert "3 registered domains" in status
    assert "No repairs were executed." in status


def test_partial_results_are_reported(qapp, qtbot):
    outcome = {
        "success": True,
        "partial": True,
        "domains_requested": ["memory", "storage", "process"],
        "domains_completed": 2,
        "failures": ["process"],
        "workflow_state": "INVESTIGATING",
        "intelligence": {
            "health": {"status": "PARTIAL", "score": None},
            "system_findings": [],
        },
        "summary": "Partial results.",
    }

    window = MainWindow(ApplicationState())
    window.diagnostic_controller = FakeDiagnosticController(outcome)

    window.dashboard.run_diagnostics_button.click()
    wait_for_completion(qtbot, window)

    status = window.dashboard.diagnostics_status_label.text()
    assert "some domain failures" in status.lower()
    assert "2 of 3 domains completed" in status
    assert "1 failed" in status
    assert "No repairs were executed." in status


def test_unsuccessful_diagnostics_are_reported(qapp, qtbot):
    outcome = {
        "success": False,
        "partial": False,
        "domains_requested": ["memory", "storage"],
        "domains_completed": 0,
        "failures": ["memory", "storage"],
        "workflow_state": "INVESTIGATING",
        "intelligence": {},
        "summary": "No results.",
    }

    window = MainWindow(ApplicationState())
    window.diagnostic_controller = FakeDiagnosticController(outcome)

    window.dashboard.run_diagnostics_button.click()
    wait_for_completion(qtbot, window)

    status = window.dashboard.diagnostics_status_label.text()
    assert "could not produce a successful result" in status.lower()
    assert "0 of 2 domains completed" in status
    assert "No repairs were executed." in status


def test_worker_exception_is_visible_and_button_recovers(qapp, qtbot):
    window = MainWindow(ApplicationState())
    window.diagnostic_controller = FakeDiagnosticController(
        error=RuntimeError("diagnostic service unavailable")
    )

    window.dashboard.run_diagnostics_button.click()
    wait_for_completion(qtbot, window)

    status = window.dashboard.diagnostics_status_label.text()
    assert "could not be completed" in status.lower()
    assert "RuntimeError" in status
    assert "diagnostic service unavailable" in status
    assert "No repairs were executed." in status


def test_overlapping_diagnostic_runs_are_rejected(qapp, qtbot):
    started = threading.Event()
    release = threading.Event()

    class BlockingController:
        def __init__(self):
            self.calls = 0

        def run_diagnostics(self):
            self.calls += 1
            started.set()

            if not release.wait(timeout=3):
                raise RuntimeError("Timed out waiting for test release.")

            return {
                "success": True,
                "partial": False,
                "domains_requested": ["memory"],
                "domains_completed": 1,
                "failures": [],
                "workflow_state": "INVESTIGATING",
                "intelligence": {
                    "health": {"status": "NORMAL", "score": 100},
                    "system_findings": [],
                },
                "summary": "Complete.",
            }

    window = MainWindow(ApplicationState())
    controller = BlockingController()
    window.diagnostic_controller = controller

    try:
        window.dashboard.run_diagnostics_button.click()

        assert started.wait(timeout=2)
        assert not window.dashboard.run_diagnostics_button.isEnabled()

        # A second direct request must not start another worker.
        window.run_diagnostics()

        assert controller.calls == 1

    finally:
        release.set()

    wait_for_completion(qtbot, window)
    assert controller.calls == 1


def test_worker_keeps_ui_responsive_while_diagnostics_run(qapp, qtbot):
    started = threading.Event()
    release = threading.Event()

    class BlockingController:
        def run_diagnostics(self):
            started.set()

            if not release.wait(timeout=3):
                raise RuntimeError("Timed out waiting for test release.")

            return {
                "success": True,
                "partial": False,
                "domains_requested": ["memory"],
                "domains_completed": 1,
                "failures": [],
                "workflow_state": "INVESTIGATING",
                "intelligence": {
                    "health": {"status": "NORMAL", "score": 100},
                    "system_findings": [],
                },
                "summary": "Complete.",
            }

    window = MainWindow(ApplicationState())
    window.diagnostic_controller = BlockingController()

    try:
        window.dashboard.run_diagnostics_button.click()

        assert started.wait(timeout=2)

        # The UI thread can still process events during worker execution.
        window.setWindowTitle("UI remains responsive")
        QApplication.processEvents()

        assert window.windowTitle() == "UI remains responsive"
        assert not window.dashboard.run_diagnostics_button.isEnabled()

    finally:
        release.set()

    wait_for_completion(qtbot, window)
    assert window.dashboard.run_diagnostics_button.isEnabled()


def test_worker_always_emits_finished_on_error(qtbot):
    from gui.diagnostic_worker import DiagnosticWorker

    worker = DiagnosticWorker(
        FakeDiagnosticController(error=RuntimeError("worker failure"))
    )

    with qtbot.waitSignal(worker.finished, timeout=1000):
        worker.run()


def test_window_close_is_rejected_while_diagnostics_are_running(qapp, qtbot):
    from PySide6.QtGui import QCloseEvent

    class RunningThread:
        def isRunning(self):
            return True

    window = MainWindow(ApplicationState())
    window._diagnostic_thread = RunningThread()

    event = QCloseEvent()
    window.closeEvent(event)

    assert not event.isAccepted()
    assert "wait" in window.dashboard.diagnostics_status_label.text().lower()


def test_window_close_is_accepted_when_diagnostics_are_not_running(qapp, qtbot):
    from PySide6.QtGui import QCloseEvent

    class FinishedThread:
        def isRunning(self):
            return False

    window = MainWindow(ApplicationState())
    window._diagnostic_thread = FinishedThread()

    event = QCloseEvent()
    window.closeEvent(event)

    assert event.isAccepted()


def test_window_close_protection_with_real_running_thread(qapp, qtbot):
    import time
    from PySide6.QtCore import QThread
    from PySide6.QtGui import QCloseEvent

    class SlowDiagnosticThread(QThread):
        def run(self):
            time.sleep(0.4)

    window = MainWindow(ApplicationState())
    thread = SlowDiagnosticThread()
    window._diagnostic_thread = thread

    thread.start()
    try:
        assert thread.isRunning()

        running_event = QCloseEvent()
        window.closeEvent(running_event)
        assert not running_event.isAccepted()

        assert thread.wait(3000), "Diagnostic thread did not finish in time."

        finished_event = QCloseEvent()
        window.closeEvent(finished_event)
        assert finished_event.isAccepted()
    finally:
        if thread.isRunning():
            thread.wait(3000)
        window._diagnostic_thread = None
        window.close()


def test_window_close_protection_with_real_running_thread(qapp, qtbot):
    import time
    from PySide6.QtCore import QThread
    from PySide6.QtGui import QCloseEvent

    class SlowDiagnosticThread(QThread):
        def run(self):
            time.sleep(0.4)

    window = MainWindow(ApplicationState())
    thread = SlowDiagnosticThread()
    window._diagnostic_thread = thread

    thread.start()
    try:
        assert thread.isRunning()

        running_event = QCloseEvent()
        window.closeEvent(running_event)
        assert not running_event.isAccepted()

        assert thread.wait(3000), "Diagnostic thread did not finish in time."

        finished_event = QCloseEvent()
        window.closeEvent(finished_event)
        assert finished_event.isAccepted()
    finally:
        if thread.isRunning():
            thread.wait(3000)
        window._diagnostic_thread = None
        window.close()


def test_diagnostic_thread_completion_restores_window_state(qapp, qtbot):
    window = MainWindow(ApplicationState())

    class FinishedThread:
        def isRunning(self):
            return False

    window._diagnostic_thread = FinishedThread()
    window._diagnostic_worker = object()

    window._on_diagnostic_thread_finished()

    assert window._diagnostic_thread is None
    assert window._diagnostic_worker is None
    assert window.dashboard.run_diagnostics_button.isEnabled()

    window.close()
