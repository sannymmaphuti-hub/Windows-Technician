from engine.technician_workflow import TechnicianWorkflow


class TechnicianWorkspace:
    def __init__(self, workflow):
        if not isinstance(workflow, TechnicianWorkflow):
            raise ValueError(
                "TechnicianWorkspace requires a TechnicianWorkflow."
            )

        self.workflow = workflow

    @property
    def case(self):
        return self.workflow.case

    @property
    def case_id(self):
        return self.case.case_id

    @property
    def state(self):
        return self.workflow.state

    @property
    def is_terminal(self):
        return self.workflow.is_terminal

    @property
    def history(self):
        return self.workflow.history

    @property
    def findings(self):
        return list(self.case.findings)

    @property
    def root_causes(self):
        return list(self.case.root_causes)

    @property
    def recommendations(self):
        return list(self.case.recommendations)

    @property
    def machine_id(self):
        return self.case.machine_id


    @property
    def hostname(self):
        return self.case.hostname