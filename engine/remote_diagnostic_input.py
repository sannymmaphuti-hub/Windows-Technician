# ==========================================
# Windows Technician v0.8
# REMOTE DIAGNOSTIC INPUT
# ==========================================

from engine.remote_diagnostic_context import RemoteDiagnosticContext


class RemoteDiagnosticInput:

    def __init__(self, context, observations):
        if not isinstance(
            context,
            RemoteDiagnosticContext,
        ):
            raise ValueError(
                "RemoteDiagnosticInput requires a "
                "RemoteDiagnosticContext."
            )

        if observations is None:
            raise ValueError(
                "observations are required"
            )

        self.context = context
        self._observations = list(observations)

    @property
    def observations(self):
        return list(self._observations)

    @property
    def machine_id(self):
        return self.context.machine_id

    @property
    def session_id(self):
        return self.context.session_id

    @property
    def is_remote(self):
        return True