# ==========================================
# Windows Technician v0.4
# DIAGNOSTIC WORKER TEST
# ==========================================

import pytest

from gui.diagnostic_worker import DiagnosticWorker


def test_diagnostic_worker_can_be_created():
    worker = DiagnosticWorker(None)

    assert worker is not None


def test_diagnostic_worker_stores_application():
    app = object()

    worker = DiagnosticWorker(app)

    assert worker.technician_app is app


def test_diagnostic_worker_emits_finished_after_success(
    qtbot,
    monkeypatch,
):
    app = object()
    worker = DiagnosticWorker(app)

    monkeypatch.setattr(
        worker,
        "_execute",
        lambda: None,
    )

    with qtbot.waitSignal(
        worker.finished,
        timeout=1000,
    ):
        worker.run()


def test_diagnostic_worker_emits_error_when_execution_fails(
    qtbot,
    monkeypatch,
):
    app = object()
    worker = DiagnosticWorker(app)

    error = RuntimeError("Diagnostic failure")

    monkeypatch.setattr(
        worker,
        "_execute",
        lambda: (_ for _ in ()).throw(error),
    )

    with qtbot.waitSignal(
        worker.error,
        timeout=1000,
    ) as blocker:
        worker.run()

    assert blocker.args[0] == "Diagnostic failure"


def test_diagnostic_worker_executes_application_diagnostics(
    monkeypatch,
):
    calls = []

    class FakeApp:
        def run_diagnostics(self):
            calls.append("run")

    worker = DiagnosticWorker(FakeApp())

    worker.run()

    assert calls == ["run"]