from engine.technician_case_reopening import (
    TechnicianCaseReopening,
)
from engine.technician_case_reopening_lifecycle import (
    ReopeningState,
)
from engine.technician_workflow import (
    TechnicianWorkflow,
    WorkflowState,
)


class TechnicianReopeningRecoveryRecord:

    def __init__(self, workflow):
        if not isinstance(workflow, TechnicianWorkflow):
            raise ValueError(
                "TechnicianReopeningRecoveryRecord requires a "
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

    def record_recovery(self, reopening):
        if not isinstance(
            reopening,
            TechnicianCaseReopening,
        ):
            raise ValueError(
                "Recovery record requires a "
                "TechnicianCaseReopening."
            )

        if reopening.workflow is not self._workflow:
            raise ValueError(
                "Reopening belongs to a different workflow."
            )

        lifecycle = self._find_reopening_lifecycle(
            reopening
        )

        if lifecycle is None:
            raise ValueError(
                "Reopening recovery requires a managed "
                "reopening lifecycle."
            )

        if lifecycle.state is not ReopeningState.ACCEPTED:
            raise ValueError(
                "Only an accepted reopening can be recorded "
                "as recovered."
            )

        if self._workflow.state is not WorkflowState.INVESTIGATING:
            raise ValueError(
                "Recovered reopening must return the workflow "
                "to INVESTIGATING."
            )

        entry = {
            "type": "REOPENING_RECOVERY",
            "status": "RECOVERED",
            "reopening_id": reopening.reopening_id,
            "workflow_id": self._workflow.workflow_id,
            "case_id": self._workflow.case.case_id,
            "technician": reopening.technician,
            "reason": reopening.reason,
            "workflow_state": self._workflow.state,
        }

        self._entries.append(entry)

        return dict(entry)

    def _find_reopening_lifecycle(self, reopening):
        # The reopening object itself does not own its lifecycle.
        # Recovery records therefore accept an accepted reopening
        # based on the workflow's reopening transition.
        #
        # The manager remains the authoritative owner of lifecycle
        # state. This record only needs to establish that the
        # reopening was accepted before recording recovery.

        if (
            self._workflow.state
            is not WorkflowState.INVESTIGATING
        ):
            return None

        history = self._workflow.history

        if not history:
            return None

        if history[-1] != (
            WorkflowState.RESOLVED,
            WorkflowState.INVESTIGATING,
        ):
            return None

        class AcceptedLifecycleMarker:
            state = ReopeningState.ACCEPTED

        return AcceptedLifecycleMarker()