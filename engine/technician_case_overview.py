from engine.technician_recovery_cycle_history import (
    TechnicianRecoveryCycleHistory,
)
from engine.technician_workflow import (
    TechnicianWorkflow,
)


class TechnicianCaseOverview:

    def __init__(self, workflow, cycle_history):
        if not isinstance(
            workflow,
            TechnicianWorkflow,
        ):
            raise ValueError(
                "TechnicianCaseOverview requires a "
                "TechnicianWorkflow."
            )

        if not isinstance(
            cycle_history,
            TechnicianRecoveryCycleHistory,
        ):
            raise ValueError(
                "TechnicianCaseOverview requires a "
                "TechnicianRecoveryCycleHistory."
            )

        if cycle_history.workflow is not workflow:
            raise ValueError(
                "Recovery cycle history belongs to a "
                "different workflow."
            )

        self._workflow = workflow
        self._cycle_history = cycle_history

    @property
    def workflow(self):
        return self._workflow

    @property
    def cycle_history(self):
        return self._cycle_history

    @property
    def case_id(self):
        return self._workflow.case.case_id

    @property
    def workflow_id(self):
        return self._workflow.workflow_id

    @property
    def workflow_state(self):
        return self._workflow.state

    @property
    def cycle_count(self):
        return self._cycle_history.cycle_count

    @property
    def current_cycle(self):
        return self._cycle_history.latest_cycle

    @property
    def current_cycle_number(self):
        return self.current_cycle.cycle_number

    @property
    def outcome(self):
        return self.current_cycle.outcome

    @property
    def is_recovery(self):
        return self.current_cycle.is_recovery