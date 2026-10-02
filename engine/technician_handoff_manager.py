from engine.technician_case_handoff import TechnicianCaseHandoff
from engine.technician_workflow import TechnicianWorkflow


class TechnicianHandoffManager:

    def __init__(self, workflow):
        if not isinstance(workflow, TechnicianWorkflow):
            raise ValueError(
                "TechnicianHandoffManager requires a TechnicianWorkflow."
            )

        self._workflow = workflow
        self._handoffs = []

    @property
    def workflow(self):
        return self._workflow

    @property
    def handoffs(self):
        return list(self._handoffs)

    @property
    def latest_handoff(self):
        if not self._handoffs:
            return None

        return self._handoffs[-1]

    def add_handoff(self, handoff):
        if not isinstance(handoff, TechnicianCaseHandoff):
            raise ValueError(
                "Handoff manager requires a TechnicianCaseHandoff."
            )

        if handoff.workflow is not self._workflow:
            raise ValueError(
                "Handoff belongs to a different workflow."
            )

        self._handoffs.append(handoff)

        return handoff