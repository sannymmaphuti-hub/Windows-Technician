from engine.technician_case_closure import TechnicianCaseClosure
from engine.technician_case_reopening import (
    TechnicianCaseReopening,
)
from engine.technician_case_reopening_lifecycle import (
    TechnicianCaseReopeningLifecycle,
)
from engine.technician_workflow import TechnicianWorkflow


class TechnicianActivityLog:

    def __init__(self, workflow):
        if not isinstance(workflow, TechnicianWorkflow):
            raise ValueError(
                "TechnicianActivityLog requires a TechnicianWorkflow."
            )

        self._workflow = workflow
        self._entries = []

    @property
    def workflow(self):
        return self._workflow

    @property
    def entries(self):
        return [dict(entry) for entry in self._entries]

    def record_workflow_event(self):
        history = self._workflow.history

        if not history:
            raise ValueError(
                "Cannot record a workflow event without a transition."
            )

        previous_state, current_state = history[-1]

        self._entries.append(
            {
                "type": "WORKFLOW",
                "previous_state": previous_state,
                "state": current_state,
            }
        )

    def record_decision(self, decision):
        self._entries.append(
            {
                "type": "DECISION",
                "decision": decision,
            }
        )

    def record_note(self, note):
        self._entries.append(
            {
                "type": "NOTE",
                "note": note,
            }
        )

    def record_remediation(self, status):
        self._entries.append(
            {
                "type": "REMEDIATION",
                "status": status,
            }
        )

    def record_verification(self, verified):
        self._entries.append(
            {
                "type": "VERIFICATION",
                "verified": verified,
            }
        )

    def record_escalation(self, status):
        self._entries.append(
            {
                "type": "ESCALATION",
                "status": status,
            }
        )

    def record_closure(self, closure):
        if not isinstance(
            closure,
            TechnicianCaseClosure,
        ):
            raise ValueError(
                "Activity log requires a TechnicianCaseClosure."
            )

        if closure.workflow is not self._workflow:
            raise ValueError(
                "Closure belongs to a different workflow."
            )

        self._entries.append(
            {
                "type": "CLOSURE",
                "closure": closure,
            }
        )

    def record_reopening_request(self, reopening):
        if not isinstance(
            reopening,
            TechnicianCaseReopening,
        ):
            raise ValueError(
                "Activity log requires a TechnicianCaseReopening."
            )

        if reopening.workflow is not self._workflow:
            raise ValueError(
                "Reopening belongs to a different workflow."
            )

        self._entries.append(
            {
                "type": "REOPENING",
                "status": "REQUESTED",
                "reopening": reopening,
            }
        )

    def record_reopening_status(self, lifecycle):
        if not isinstance(
            lifecycle,
            TechnicianCaseReopeningLifecycle,
        ):
            raise ValueError(
                "Activity log requires a "
                "TechnicianCaseReopeningLifecycle."
            )

        if lifecycle.reopening.workflow is not self._workflow:
            raise ValueError(
                "Reopening belongs to a different workflow."
            )

        self._entries.append(
            {
                "type": "REOPENING",
                "status": lifecycle.state.value,
                "reopening": lifecycle.reopening,
            }
        )

    def record_reopening_recovery(self, entry):
        if not isinstance(entry, dict):
            raise ValueError(
                "Activity log recovery entry must be a dictionary."
            )

        if entry.get("type") != "REOPENING_RECOVERY":
            raise ValueError(
                "Activity log requires a reopening recovery entry."
            )

        self._entries.append(dict(entry))

        return dict(entry)