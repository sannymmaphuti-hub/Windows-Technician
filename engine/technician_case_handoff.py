import uuid
from datetime import datetime, timezone

from engine.technician_workflow import TechnicianWorkflow


class TechnicianCaseHandoff:

    def __init__(
        self,
        workflow,
        from_technician,
        to_technician,
        reason,
    ):
        if not isinstance(workflow, TechnicianWorkflow):
            raise ValueError(
                "TechnicianCaseHandoff requires a TechnicianWorkflow."
            )

        if not isinstance(from_technician, str):
            raise ValueError(
                "Handoff sender must be a string."
            )

        if not from_technician.strip():
            raise ValueError(
                "Handoff sender cannot be empty."
            )

        if not isinstance(to_technician, str):
            raise ValueError(
                "Handoff receiver must be a string."
            )

        if not to_technician.strip():
            raise ValueError(
                "Handoff receiver cannot be empty."
            )

        if not isinstance(reason, str):
            raise ValueError(
                "Handoff reason must be a string."
            )

        if not reason.strip():
            raise ValueError(
                "Handoff reason cannot be empty."
            )

        self._workflow = workflow
        self._handoff_id = str(uuid.uuid4())
        self._created_at = datetime.now(timezone.utc)
        self._from_technician = from_technician
        self._to_technician = to_technician
        self._reason = reason

    @property
    def workflow(self):
        return self._workflow

    @property
    def case_id(self):
        return self._workflow.case.case_id

    @property
    def handoff_id(self):
        return self._handoff_id

    @property
    def created_at(self):
        return self._created_at

    @property
    def from_technician(self):
        return self._from_technician

    @property
    def to_technician(self):
        return self._to_technician

    @property
    def reason(self):
        return self._reason