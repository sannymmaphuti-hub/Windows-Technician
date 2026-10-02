import uuid
from datetime import datetime, timezone

from engine.technician_workflow import (
    TechnicianWorkflow,
    WorkflowState,
)


class TechnicianCaseClosure:

    def __init__(
        self,
        workflow,
        technician,
        reason,
    ):
        if not isinstance(workflow, TechnicianWorkflow):
            raise ValueError(
                "TechnicianCaseClosure requires a TechnicianWorkflow."
            )

        if not isinstance(technician, str):
            raise ValueError(
                "Closure technician must be a string."
            )

        if not technician.strip():
            raise ValueError(
                "Closure technician cannot be empty."
            )

        if not isinstance(reason, str):
            raise ValueError(
                "Closure reason must be a string."
            )

        if not reason.strip():
            raise ValueError(
                "Closure reason cannot be empty."
            )

        if workflow.state is not WorkflowState.RESOLVED:
            raise ValueError(
                "A case can only be closed after it is RESOLVED."
            )

        self._workflow = workflow
        self._closure_id = str(uuid.uuid4())
        self._created_at = datetime.now(timezone.utc)
        self._technician = technician
        self._reason = reason
        self._workflow_state = workflow.state

    @property
    def workflow(self):
        return self._workflow

    @property
    def closure_id(self):
        return self._closure_id

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