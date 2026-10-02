from engine.technician_activity_log import TechnicianActivityLog
from engine.technician_case_handoff import TechnicianCaseHandoff
from engine.technician_handoff_lifecycle import (
    TechnicianHandoffLifecycle,
)
from engine.technician_handoff_manager import TechnicianHandoffManager
from engine.technician_workflow import TechnicianWorkflow


class TechnicianHandoffIntegration:

    def __init__(self, workflow):
        if not isinstance(workflow, TechnicianWorkflow):
            raise ValueError(
                "TechnicianHandoffIntegration requires a "
                "TechnicianWorkflow."
            )

        self._workflow = workflow
        self._manager = TechnicianHandoffManager(workflow)
        self._activity_log = TechnicianActivityLog(workflow)

    @property
    def workflow(self):
        return self._workflow

    @property
    def manager(self):
        return self._manager

    @property
    def activity_log(self):
        return self._activity_log

    def create_handoff(
        self,
        from_technician,
        to_technician,
        reason,
    ):
        handoff = TechnicianCaseHandoff(
            self._workflow,
            from_technician,
            to_technician,
            reason,
        )

        self._manager.add_handoff(handoff)

        self._activity_log.record_note(
            f"Handoff created: {reason}"
        )

        return handoff

    def create_lifecycle(self, handoff):
        if not isinstance(
            handoff,
            TechnicianCaseHandoff,
        ):
            raise ValueError(
                "Handoff lifecycle requires a "
                "TechnicianCaseHandoff."
            )

        if handoff.workflow is not self._workflow:
            raise ValueError(
                "Handoff belongs to a different workflow."
            )

        return TechnicianHandoffLifecycle(handoff)

    def record_handoff_status(self, lifecycle):
        if not isinstance(
            lifecycle,
            TechnicianHandoffLifecycle,
        ):
            raise ValueError(
                "Expected a TechnicianHandoffLifecycle."
            )

        if lifecycle.handoff.workflow is not self._workflow:
            raise ValueError(
                "Handoff lifecycle belongs to a "
                "different workflow."
            )

        self._activity_log.record_escalation(
            lifecycle.state.value
        )

        return lifecycle.state