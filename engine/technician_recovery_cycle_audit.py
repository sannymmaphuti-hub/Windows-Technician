from engine.technician_recovery_cycle import (
    TechnicianRecoveryCycle,
)
from engine.technician_workflow import TechnicianWorkflow


class TechnicianRecoveryCycleAudit:

    def __init__(self, workflow):
        if not isinstance(
            workflow,
            TechnicianWorkflow,
        ):
            raise ValueError(
                "TechnicianRecoveryCycleAudit requires a "
                "TechnicianWorkflow."
            )

        self._workflow = workflow
        self._entries = []

    @property
    def workflow(self):
        return self._workflow

    @property
    def entries(self):
        return [dict(entry) for entry in self._entries]

    def record_cycle(self, cycle):
        if not isinstance(
            cycle,
            TechnicianRecoveryCycle,
        ):
            raise ValueError(
                "Recovery cycle audit requires a "
                "TechnicianRecoveryCycle."
            )

        if cycle.workflow is not self._workflow:
            raise ValueError(
                "Recovery cycle belongs to a different workflow."
            )

        entry = {
            "type": "RECOVERY_CYCLE",
            "cycle_number": cycle.cycle_number,
            "workflow_id": self._workflow.workflow_id,
            "case_id": self._workflow.case.case_id,
            "started_at": cycle.started_at,
            "is_original": cycle.is_original,
            "is_recovery": cycle.is_recovery,
        }

        self._entries.append(entry)

        return dict(entry)