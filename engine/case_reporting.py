from engine.technician_workflow import TechnicianWorkflow


class CaseReporting:

    def __init__(self, workflow):
        if not isinstance(workflow, TechnicianWorkflow):
            raise ValueError(
                "CaseReporting requires a TechnicianWorkflow."
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
        return getattr(self.case, "machine_id", None)

    @property
    def hostname(self):
        return getattr(self.case, "hostname", None)

    @property
    def state(self):
        return self.workflow.state

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
    def summary(self):
        return {
            "case_id": self.case_id,
            "machine_id": self.machine_id,
            "hostname": self.hostname,
            "state": self.state,
            "history": self.history,
            "findings": self.findings,
            "root_causes": self.root_causes,
            "recommendations": self.recommendations,
        }