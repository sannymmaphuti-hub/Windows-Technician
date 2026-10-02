from engine.correlation import Correlation
from engine.technician_recovery_cycle_history import (
    TechnicianRecoveryCycleHistory,
)
from engine.technician_workflow import TechnicianWorkflow


class TechnicianCorrelationDetail:

    def __init__(
        self,
        workflow,
        cycle_history,
        correlation,
    ):
        if not isinstance(
            workflow,
            TechnicianWorkflow,
        ):
            raise ValueError(
                "TechnicianCorrelationDetail requires a "
                "TechnicianWorkflow."
            )

        if not isinstance(
            cycle_history,
            TechnicianRecoveryCycleHistory,
        ):
            raise ValueError(
                "TechnicianCorrelationDetail requires a "
                "TechnicianRecoveryCycleHistory."
            )

        if cycle_history.workflow is not workflow:
            raise ValueError(
                "Recovery cycle history belongs to a "
                "different workflow."
            )

        if not isinstance(
            correlation,
            Correlation,
        ):
            raise ValueError(
                "TechnicianCorrelationDetail requires a "
                "Correlation."
            )

        if correlation not in workflow.case.correlations:
            raise ValueError(
                "Correlation does not belong to the workflow case."
            )

        self._workflow = workflow
        self._cycle_history = cycle_history
        self._correlation = correlation

    @property
    def workflow(self):
        return self._workflow

    @property
    def cycle_history(self):
        return self._cycle_history

    @property
    def correlation(self):
        return self._correlation

    @property
    def correlation_type(self):
        return self._correlation.correlation_type

    @property
    def findings(self):
        return list(self._correlation.findings)

    @property
    def strength(self):
        return self._correlation.strength

    @property
    def explanation(self):
        return self._correlation.explanation