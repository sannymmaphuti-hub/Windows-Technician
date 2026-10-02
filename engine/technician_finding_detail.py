from engine.finding import Finding
from engine.technician_recovery_cycle_history import (
    TechnicianRecoveryCycleHistory,
)
from engine.technician_workflow import TechnicianWorkflow


class TechnicianFindingDetail:

    def __init__(
        self,
        workflow,
        cycle_history,
        finding,
    ):
        if not isinstance(
            workflow,
            TechnicianWorkflow,
        ):
            raise ValueError(
                "TechnicianFindingDetail requires a "
                "TechnicianWorkflow."
            )

        if not isinstance(
            cycle_history,
            TechnicianRecoveryCycleHistory,
        ):
            raise ValueError(
                "TechnicianFindingDetail requires a "
                "TechnicianRecoveryCycleHistory."
            )

        if cycle_history.workflow is not workflow:
            raise ValueError(
                "Recovery cycle history belongs to a "
                "different workflow."
            )

        if not isinstance(
            finding,
            Finding,
        ):
            raise ValueError(
                "TechnicianFindingDetail requires a Finding."
            )

        if finding not in workflow.case.findings:
            raise ValueError(
                "Finding does not belong to the workflow case."
            )

        self._workflow = workflow
        self._cycle_history = cycle_history
        self._finding = finding

    @property
    def workflow(self):
        return self._workflow

    @property
    def cycle_history(self):
        return self._cycle_history

    @property
    def finding(self):
        return self._finding

    @property
    def finding_type(self):
        return self._finding.finding_type

    @property
    def description(self):
        return self._finding.description

    @property
    def category(self):
        return self._finding.category

    @property
    def severity(self):
        return self._finding.severity

    @property
    def supporting_signals(self):
        return list(
            self._finding.supporting_signals
        )