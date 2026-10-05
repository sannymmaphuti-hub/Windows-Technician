from engine.technician_workflow import TechnicianWorkflow


class CaseHandoff:

    VALID_STATUSES = {
        "PENDING",
        "ACCEPTED",
        "DECLINED",
    }

    def __init__(self, workflow, recipient, reason):
        if not isinstance(workflow, TechnicianWorkflow):
            raise ValueError(
                "CaseHandoff requires a TechnicianWorkflow."
            )

        if recipient is None:
            raise ValueError(
                "CaseHandoff requires a recipient."
            )

        if reason is None:
            raise ValueError(
                "CaseHandoff requires a reason."
            )

        self.workflow = workflow
        self.recipient = recipient
        self.reason = reason
        self.status = "PENDING"

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

    def accept(self):
        if self.status == "PENDING":
            self.status = "ACCEPTED"

    def decline(self):
        if self.status == "PENDING":
            self.status = "DECLINED"