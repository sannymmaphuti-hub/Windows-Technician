from engine.technician_workflow import TechnicianWorkflow


class CaseTimeline:

    def __init__(self, workflow):
        if not isinstance(workflow, TechnicianWorkflow):
            raise ValueError(
                "CaseTimeline requires a TechnicianWorkflow."
            )

        self.workflow = workflow

    @property
    def case(self):
        return self.workflow.case

    @property
    def case_id(self):
        return self.case.case_id

    @property
    def machine_id(self):
        return self.case.machine_id

    @property
    def hostname(self):
        return self.case.hostname

    @property
    def history(self):
        return self.workflow.history

    @property
    def state(self):
        return self.workflow.state

    @property
    def is_terminal(self):
        return self.workflow.is_terminal
        