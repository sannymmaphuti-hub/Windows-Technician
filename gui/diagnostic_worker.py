from PySide6.QtCore import QObject, Signal


class DiagnosticWorker(QObject):
    finished = Signal()
    error = Signal(str)

    def __init__(self, technician_app):
        super().__init__()

        self.technician_app = technician_app

    def _execute(self):
        self.technician_app.run_diagnostics()

    def run(self):
        try:
            self._execute()

        except Exception as exc:
            self.error.emit(str(exc))

        else:
            self.finished.emit()