from engine.technician_recovery_cycle_audit import (
    TechnicianRecoveryCycleAudit,
)
from engine.technician_recovery_cycle_history import (
    TechnicianRecoveryCycleHistory,
)


class TechnicianRecoveryCycleReport:

    def __init__(self, history, audit=None):
        if not isinstance(
            history,
            TechnicianRecoveryCycleHistory,
        ):
            raise ValueError(
                "TechnicianRecoveryCycleReport requires a "
                "TechnicianRecoveryCycleHistory."
            )

        if audit is not None:
            if not isinstance(
                audit,
                TechnicianRecoveryCycleAudit,
            ):
                raise ValueError(
                    "Recovery cycle report audit must be a "
                    "TechnicianRecoveryCycleAudit."
                )

            if audit.workflow is not history.workflow:
                raise ValueError(
                    "Recovery cycle audit belongs to a "
                    "different workflow."
                )

        self._history = history
        self._audit = audit

    @property
    def history(self):
        return self._history

    @property
    def audit(self):
        return self._audit

    @property
    def cycles(self):
        return list(self._history.cycles)

    @property
    def cycle_count(self):
        return len(self._history.cycles)

    @property
    def current_cycle(self):
        return self._history.latest_cycle

    @property
    def current_cycle_number(self):
        return self.current_cycle.cycle_number

    @property
    def is_recovery(self):
        return self.current_cycle.is_recovery

    @property
    def started_at(self):
        return self.current_cycle.started_at

    @property
    def outcome(self):
        return self.current_cycle.outcome

    @property
    def audit_entries(self):
        if self._audit is None:
            return []

        return [
            dict(entry)
            for entry in self._audit.entries
        ]