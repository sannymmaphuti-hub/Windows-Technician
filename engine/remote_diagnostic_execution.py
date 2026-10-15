# ==========================================
# Windows Technician V1.0
# REMOTE DIAGNOSTIC EXECUTION
# ==========================================

from uuid import uuid4

from engine.remote_operation import RemoteOperation


class RemoteDiagnosticExecution:

    def __init__(self, operations):
        if operations is None:
            raise ValueError(
                "operations is required."
            )

        if not hasattr(operations, "machine"):
            raise ValueError(
                "operations must provide a machine."
            )

        if not hasattr(operations, "session"):
            raise ValueError(
                "operations must provide a session."
            )

        if not hasattr(
            operations,
            "diagnostic_pipeline",
        ):
            raise ValueError(
                "operations must provide a diagnostic_pipeline."
            )

        self.operations = operations
        self._operation = None
        self._result = None
        self._failure = None

    @property
    def operation(self):
        return self._operation

    @property
    def result(self):
        return self._result

    @property
    def failure(self):
        return self._failure

    def execute(self, observations):
        if not self.operations.machine.is_available:
            raise ValueError(
                "Remote diagnostics require "
                "an available machine."
            )

        if self._operation is not None:
            raise ValueError(
                "remote diagnostic execution has already started."
            )

        self._operation = RemoteOperation(
            operation_id=str(uuid4()),
            machine_id=self.operations.machine_id,
            session_id=self.operations.session_id,
            operation_type="DIAGNOSTIC",
        )

        self._operation.start()

        try:
            result = self.operations.diagnose(
                observations
            )

            self._result = result
            self._operation.complete()

            return result

        except Exception as exc:
            self._failure = str(exc)
            self._operation.fail(
                self._failure
            )
            raise
