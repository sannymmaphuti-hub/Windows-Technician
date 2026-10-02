import uuid

from engine.technician_workflow import TechnicianWorkflow


class TechnicianInvestigation:
    def __init__(self, workflow):
        if not isinstance(workflow, TechnicianWorkflow):
            raise ValueError(
                "TechnicianInvestigation requires a TechnicianWorkflow."
            )

        self.workflow = workflow
        self.investigation_id = str(uuid.uuid4())

        self._active = False
        self._complete = False
        self._evidence_reviewed = []
        self._findings_reviewed = []

    @property
    def is_active(self):
        return self._active

    @property
    def is_complete(self):
        return self._complete

    @property
    def evidence_reviewed(self):
        return list(self._evidence_reviewed)

    @property
    def findings_reviewed(self):
        return list(self._findings_reviewed)

    def start(self):
        if self._complete:
            raise ValueError("Completed investigation cannot be restarted.")

        if self._active:
            raise ValueError("Investigation is already active.")

        if self.workflow.state != self.workflow.state.INVESTIGATING:
            raise ValueError(
                "Investigation can only start while workflow is INVESTIGATING."
            )

        self._active = True

    def review_evidence(self, evidence):
        self._require_active()

        if evidence not in self._evidence_reviewed:
            self._evidence_reviewed.append(evidence)

    def review_finding(self, finding):
        self._require_active()

        if finding not in self._findings_reviewed:
            self._findings_reviewed.append(finding)

    def complete(self):
        self._require_active()

        self._active = False
        self._complete = True

    def _require_active(self):
        if not self._active:
            raise ValueError(
                "Investigation must be active before it can be modified."
            )