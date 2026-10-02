from engine.technician_recovery_cycle_audit import (
    TechnicianRecoveryCycleAudit,
)
from engine.technician_recovery_cycle_history import (
    TechnicianRecoveryCycleHistory,
)
from engine.technician_recovery_cycle_report import (
    TechnicianRecoveryCycleReport,
)
from engine.technician_workflow import TechnicianWorkflow


class TechnicianRecoveryCycleReportingIntegration:

    def __init__(self, workflow):
        if not isinstance(
            workflow,
            TechnicianWorkflow,
        ):
            raise ValueError(
                "TechnicianRecoveryCycleReportingIntegration "
                "requires a TechnicianWorkflow."
            )

        self._workflow = workflow

        self._cycle_history = (
            TechnicianRecoveryCycleHistory(
                workflow
            )
        )

        self._cycle_audit = (
            TechnicianRecoveryCycleAudit(
                workflow
            )
        )

        self._cycle_report = (
            TechnicianRecoveryCycleReport(
                self._cycle_history,
                audit=self._cycle_audit,
            )
        )

    @property
    def workflow(self):
        return self._workflow

    @property
    def cycle_history(self):
        return self._cycle_history

    @property
    def cycle_audit(self):
        return self._cycle_audit

    @property
    def cycle_report(self):
        return self._cycle_report