from engine.technician_workflow import TechnicianWorkflow


class TechnicianCaseTimeline:

    def __init__(self, workflow):
        if not isinstance(workflow, TechnicianWorkflow):
            raise ValueError(
                "TechnicianCaseTimeline requires a TechnicianWorkflow."
            )

        self._workflow = workflow

    @property
    def workflow(self):
        return self._workflow

    @property
    def events(self):
        return self._workflow.history