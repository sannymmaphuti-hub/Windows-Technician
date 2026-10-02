from datetime import datetime, timezone

from engine.technician_workflow import (
    TechnicianWorkflow,
    WorkflowState,
)


class TechnicianRecoveryCycle:

    def __init__(self, workflow, cycle_number=0):
        if not isinstance(
            workflow,
            TechnicianWorkflow,
        ):
            raise ValueError(
                "TechnicianRecoveryCycle requires a "
                "TechnicianWorkflow."
            )

        if not isinstance(cycle_number, int):
            raise ValueError(
                "Recovery cycle number must be an integer."
            )

        if cycle_number < 0:
            raise ValueError(
                "Recovery cycle number cannot be negative."
            )

        self._workflow = workflow
        self._cycle_number = cycle_number
        self._started_at = datetime.now(timezone.utc)

    @property
    def workflow(self):
        return self._workflow

    @property
    def cycle_number(self):
        return self._cycle_number

    @property
    def started_at(self):
        return self._started_at

    @property
    def is_original(self):
        return self._cycle_number == 0

    @property
    def is_recovery(self):
        return self._cycle_number > 0

    @property
    def outcome(self):
        if self._workflow.state is WorkflowState.RESOLVED:
            return "RESOLVED"

        if self._workflow.state is WorkflowState.ESCALATED:
            return "ESCALATED"

        return "ACTIVE"

    def start_recovery_cycle(self):
        if self._workflow.state is not WorkflowState.INVESTIGATING:
            raise ValueError(
                "Recovery cycle can only start while "
                "workflow is INVESTIGATING."
            )

        return TechnicianRecoveryCycle(
            self._workflow,
            cycle_number=self._cycle_number + 1,
        )