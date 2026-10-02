from engine.technician_recovery_cycle_history import (
    TechnicianRecoveryCycleHistory,
)


class TechnicianRecoveryCycleSummary:

    def __init__(self, history):
        if not isinstance(
            history,
            TechnicianRecoveryCycleHistory,
        ):
            raise ValueError(
                "TechnicianRecoveryCycleSummary requires a "
                "TechnicianRecoveryCycleHistory."
            )

        self._history = history

    @property
    def history(self):
        return self._history

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