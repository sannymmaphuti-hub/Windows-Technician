from engine.technician_activity_log import (
    TechnicianActivityLog,
)
from engine.technician_case_reopening import (
    TechnicianCaseReopening,
)
from engine.technician_recovery_cycle import (
    TechnicianRecoveryCycle,
)
from engine.technician_recovery_cycle_history import (
    TechnicianRecoveryCycleHistory,
)
from engine.technician_reopening_recovery_record import (
    TechnicianReopeningRecoveryRecord,
)
from engine.technician_workflow import TechnicianWorkflow


class TechnicianReopeningRecoveryIntegration:

    def __init__(self, workflow):
        if not isinstance(
            workflow,
            TechnicianWorkflow,
        ):
            raise ValueError(
                "TechnicianReopeningRecoveryIntegration requires a "
                "TechnicianWorkflow."
            )

        self._workflow = workflow

        self._recovery_record = (
            TechnicianReopeningRecoveryRecord(workflow)
        )

        self._activity_log = TechnicianActivityLog(
            workflow
        )

        self._cycle_history = (
            TechnicianRecoveryCycleHistory(workflow)
        )

    @property
    def workflow(self):
        return self._workflow

    @property
    def recovery_record(self):
        return self._recovery_record

    @property
    def activity_log(self):
        return self._activity_log

    @property
    def cycle_history(self):
        return self._cycle_history

    def record_recovery(self, reopening):
        if not isinstance(
            reopening,
            TechnicianCaseReopening,
        ):
            raise ValueError(
                "Recovery integration requires a "
                "TechnicianCaseReopening."
            )

        if reopening.workflow is not self._workflow:
            raise ValueError(
                "Reopening belongs to a different workflow."
            )

        entry = self._recovery_record.record_recovery(
            reopening
        )

        current_cycle = self._cycle_history.latest_cycle

        recovery_cycle = current_cycle.start_recovery_cycle()

        self._cycle_history.record_cycle(
            recovery_cycle
        )

        self._activity_log.record_reopening_recovery(
            entry
        )

        return dict(entry)