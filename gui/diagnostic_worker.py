"""Background-safe diagnostic worker for Windows Technician."""

from PySide6.QtCore import QObject, Signal


class DiagnosticWorker(QObject):
    """Run diagnostic work and communicate results through Qt signals."""

    result = Signal(object)
    finished = Signal()
    error = Signal(str)
    error_details = Signal(str)

    def __init__(self, technician_app):
        super().__init__()
        self.technician_app = technician_app

    def _execute(self):
        """Execute diagnostics and return the result without touching UI."""
        return self.technician_app.run_diagnostics()

    def run(self):
        """Execute once, emit a result or error, and always finish."""
        try:
            outcome = self._execute()
        except Exception as exc:
            self.error.emit(str(exc))
            self.error_details.emit(f"{type(exc).__name__}: {exc}")
        else:
            self.result.emit(outcome)
        finally:
            self.finished.emit()
