from engine.root_cause import RootCauseCandidate
from engine.technician_recovery_cycle_history import (
    TechnicianRecoveryCycleHistory,
)
from engine.technician_workflow import TechnicianWorkflow


class TechnicianRootCauseDetail:

    def __init__(
        self,
        workflow,
        cycle_history,
        root_cause,
    ):
        if not isinstance(
            workflow,
            TechnicianWorkflow,
        ):
            raise ValueError(
                "TechnicianRootCauseDetail requires a "
                "TechnicianWorkflow."
            )

        if not isinstance(
            cycle_history,
            TechnicianRecoveryCycleHistory,
        ):
            raise ValueError(
                "TechnicianRootCauseDetail requires a "
                "TechnicianRecoveryCycleHistory."
            )

        if cycle_history.workflow is not workflow:
            raise ValueError(
                "Recovery cycle history belongs to a "
                "different workflow."
            )

        if not isinstance(
            root_cause,
            RootCauseCandidate,
        ):
            raise ValueError(
                "TechnicianRootCauseDetail requires a "
                "RootCauseCandidate."
            )

        if root_cause not in workflow.case.root_causes:
            raise ValueError(
                "Root cause does not belong to the workflow case."
            )

        self._workflow = workflow
        self._cycle_history = cycle_history
        self._root_cause = root_cause

    @property
    def workflow(self):
        return self._workflow

    @property
    def cycle_history(self):
        return self._cycle_history

    @property
    def root_cause(self):
        return self._root_cause

    @property
    def cause(self):
        return self._root_cause.cause

    @property
    def category(self):
        return self._root_cause.category

    @property
    def confidence(self):
        return self._root_cause.confidence

    @property
    def confidence_level(self):
        return self._root_cause.confidence_level()

    @property
    def evidence(self):
        return list(self._root_cause.evidence)

    @property
    def reason(self):
        return self._root_cause.reason