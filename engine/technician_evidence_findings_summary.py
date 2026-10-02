from engine.technician_recovery_cycle_history import (
    TechnicianRecoveryCycleHistory,
)
from engine.technician_workflow import TechnicianWorkflow


class TechnicianEvidenceFindingsSummary:

    def __init__(self, workflow, cycle_history):
        if not isinstance(
            workflow,
            TechnicianWorkflow,
        ):
            raise ValueError(
                "TechnicianEvidenceFindingsSummary requires a "
                "TechnicianWorkflow."
            )

        if not isinstance(
            cycle_history,
            TechnicianRecoveryCycleHistory,
        ):
            raise ValueError(
                "TechnicianEvidenceFindingsSummary requires a "
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
    def cycle_history(self):
        return self._cycle_history

    @property
    def findings(self):
        return list(self._workflow.case.findings)

    @property
    def finding_count(self):
        return len(self._workflow.case.findings)

    @property
    def correlations(self):
        return list(self._workflow.case.correlations)

    @property
    def correlation_count(self):
        return len(self._workflow.case.correlations)

    @property
    def evidence_count(self):
        return len(self._workflow.case.evidence)