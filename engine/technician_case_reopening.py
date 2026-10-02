import uuid
from datetime import datetime, timezone

from engine.technician_case_closure import TechnicianCaseClosure
from engine.technician_workflow import (
    TechnicianWorkflow,
    WorkflowState,
)


class TechnicianCaseReopening:

    def __init__(
        self,
        workflow,
        technician,
        reason,
        closure=None,
    ):
        if not isinstance(workflow, TechnicianWorkflow):
            raise ValueError(
                "TechnicianCaseReopening requires a TechnicianWorkflow."
            )

        if not isinstance(technician, str):
            raise ValueError(
                "Reopening technician must be a string."
            )

        if not technician.strip():
            raise ValueError(
                "Reopening technician cannot be empty."
            )

        if not isinstance(reason, str):
            raise ValueError(
                "Reopening reason must be a string."
            )

        if not reason.strip():
            raise ValueError(
                "Reopening reason cannot be empty."
            )

        if workflow.state is not WorkflowState.RESOLVED:
            raise ValueError(
                "A case can only be reopened after it is RESOLVED."
            )

        if closure is not None:
            if not isinstance(
                closure,
                TechnicianCaseClosure,
            ):
                raise ValueError(
                    "Reopening closure must be a "
                    "TechnicianCaseClosure."
                )

            if closure.workflow is not workflow:
                raise ValueError(
                    "Closure belongs to a different workflow."
                )

        self._workflow = workflow
        self._reopening_id = str(uuid.uuid4())
        self._created_at = datetime.now(timezone.utc)
        self._technician = technician
        self._reason = reason
        self._workflow_state = workflow.state
        self._closure = closure

    @property
    def workflow(self):
        return self._workflow

    @property
    def reopening_id(self):
        return self._reopening_id

    @property
    def case_id(self):
        return self._workflow.case.case_id

    @property
    def workflow_id(self):
        return self._workflow.workflow_id

    @property
    def created_at(self):
        return self._created_at

    @property
    def technician(self):
        return self._technician

    @property
    def reason(self):
        return self._reason

    @property
    def workflow_state(self):
        return self._workflow_state

    @property
    def closure(self):
        return self._closure