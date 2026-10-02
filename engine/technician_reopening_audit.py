from engine.technician_case_reopening import (
    TechnicianCaseReopening,
)
from engine.technician_case_reopening_lifecycle import (
    TechnicianCaseReopeningLifecycle,
)
from engine.technician_workflow import TechnicianWorkflow


class TechnicianReopeningAudit:

    def __init__(self, workflow):
        if not isinstance(workflow, TechnicianWorkflow):
            raise ValueError(
                "TechnicianReopeningAudit requires a "
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

    def record_request(self, reopening):
        if not isinstance(
            reopening,
            TechnicianCaseReopening,
        ):
            raise ValueError(
                "Reopening audit requires a "
                "TechnicianCaseReopening."
            )

        self._validate_workflow(
            reopening.workflow
        )

        closure_id = None

        if reopening.closure is not None:
            closure_id = reopening.closure.closure_id

        entry = {
            "type": "REOPENING",
            "status": "REQUESTED",
            "reopening_id": reopening.reopening_id,
            "technician": reopening.technician,
            "reason": reopening.reason,
            "closure_id": closure_id,
            "created_at": reopening.created_at,
        }

        self._entries.append(entry)

        return dict(entry)

    def record_status(self, lifecycle):
        if not isinstance(
            lifecycle,
            TechnicianCaseReopeningLifecycle,
        ):
            raise ValueError(
                "Reopening audit requires a "
                "TechnicianCaseReopeningLifecycle."
            )

        reopening = lifecycle.reopening

        self._validate_workflow(
            reopening.workflow
        )

        entry = {
            "type": "REOPENING",
            "status": lifecycle.state.value,
            "reopening_id": reopening.reopening_id,
            "technician": reopening.technician,
            "reason": reopening.reason,
            "closure_id": (
                reopening.closure.closure_id
                if reopening.closure is not None
                else None
            ),
            "created_at": lifecycle.reopening.created_at,
        }

        self._entries.append(entry)

        return dict(entry)

    def _validate_workflow(self, workflow):
        if workflow is not self._workflow:
            raise ValueError(
                "Reopening belongs to a different workflow."
            )
            