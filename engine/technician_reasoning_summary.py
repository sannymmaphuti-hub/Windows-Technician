from engine.technician_recovery_cycle_history import (
    TechnicianRecoveryCycleHistory,
)
from engine.technician_workflow import TechnicianWorkflow


class TechnicianReasoningSummary:

    def __init__(self, workflow, cycle_history):
        if not isinstance(
            workflow,
            TechnicianWorkflow,
        ):
            raise ValueError(
                "TechnicianReasoningSummary requires a "
                "TechnicianWorkflow."
            )

        if not isinstance(
            cycle_history,
            TechnicianRecoveryCycleHistory,
        ):
            raise ValueError(
                "TechnicianReasoningSummary requires a "
                "TechnicianRecoveryCycleHistory."
            )

        if cycle_history.workflow is not workflow:
            raise ValueError(
                "Recovery cycle history belongs to a "
                "different workflow."
            )

        self._workflow = workflow
        self._cycle_history = cycle_history

    @property
    def workflow(self):
        return self._workflow

    @property
    def case_id(self):
        return self._workflow.case.case_id

    @property
    def workflow_id(self):
        return self._workflow.workflow_id

    @property
    def cycle_history(self):
        return self._cycle_history

    @property
    def findings(self):
        return list(self._workflow.case.findings)

    @property
    def correlations(self):
        return list(self._workflow.case.correlations)

    @property
    def root_causes(self):
        return list(self._workflow.case.root_causes)

    @property
    def recommendations(self):
        return list(self._workflow.case.recommendations)

    @property
    def finding_count(self):
        return len(self._workflow.case.findings)

    @property
    def correlation_count(self):
        return len(self._workflow.case.correlations)

    @property
    def root_cause_count(self):
        return len(self._workflow.case.root_causes)

    @property
    def recommendation_count(self):
        return len(self._workflow.case.recommendations)

    @property
    def overview(self):
        return {
            "finding_count": self.finding_count,
            "correlation_count": self.correlation_count,
            "root_cause_count": self.root_cause_count,
            "recommendation_count": self.recommendation_count,
            "findings": self.findings,
            "correlations": self.correlations,
            "root_causes": self.root_causes,
            "recommendations": self.recommendations,
        }