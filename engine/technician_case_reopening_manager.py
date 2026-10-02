from engine.technician_case_reopening import (
    TechnicianCaseReopening,
)
from engine.technician_case_reopening_lifecycle import (
    ReopeningState,
    TechnicianCaseReopeningLifecycle,
)
from engine.technician_workflow import (
    TechnicianWorkflow,
    WorkflowState,
)


class TechnicianCaseReopeningManager:

    def __init__(self, workflow):
        if not isinstance(workflow, TechnicianWorkflow):
            raise ValueError(
                "TechnicianCaseReopeningManager requires a "
                "TechnicianWorkflow."
            )

        self._workflow = workflow
        self._reopenings = []
        self._lifecycles = {}

    @property
    def workflow(self):
        return self._workflow

    @property
    def reopenings(self):
        return list(self._reopenings)

    @property
    def latest_reopening(self):
        if not self._reopenings:
            return None

        return self._reopenings[-1]

    def request_reopening(
        self,
        technician,
        reason,
        closure=None,
    ):
        reopening = TechnicianCaseReopening(
            self._workflow,
            technician,
            reason,
            closure=closure,
        )

        self._reopenings.append(reopening)

        lifecycle = TechnicianCaseReopeningLifecycle(
            reopening
        )

        self._lifecycles[
            reopening.reopening_id
        ] = lifecycle

        return reopening

    def create_lifecycle(self, reopening):
        if not isinstance(
            reopening,
            TechnicianCaseReopening,
        ):
            raise ValueError(
                "Expected a TechnicianCaseReopening."
            )

        if reopening.workflow is not self._workflow:
            raise ValueError(
                "Reopening belongs to a different workflow."
            )

        if reopening not in self._reopenings:
            raise ValueError(
                "Reopening is not managed by this manager."
            )

        return self._lifecycles[
            reopening.reopening_id
        ]

    def accept_reopening(self, reopening_or_lifecycle):
        lifecycle = self._resolve_lifecycle(
            reopening_or_lifecycle
        )

        if lifecycle.state is not ReopeningState.PENDING:
            raise ValueError(
                "Only a pending reopening can be accepted."
            )

        if self._workflow.state is not WorkflowState.RESOLVED:
            raise ValueError(
                "Only a resolved workflow can be reopened."
            )

        lifecycle.accept()
        self._workflow.reopen()

        return (
            reopening_or_lifecycle
            if isinstance(
                reopening_or_lifecycle,
                TechnicianCaseReopening,
            )
            else lifecycle
        )

    def reject_reopening(self, reopening_or_lifecycle):
        lifecycle = self._resolve_lifecycle(
            reopening_or_lifecycle
        )

        if lifecycle.state is not ReopeningState.PENDING:
            raise ValueError(
                "Only a pending reopening can be rejected."
            )

        lifecycle.reject()

        return lifecycle

    def complete_reopening(self, reopening_or_lifecycle):
        lifecycle = self._resolve_lifecycle(
            reopening_or_lifecycle
        )

        if lifecycle.state is not ReopeningState.ACCEPTED:
            raise ValueError(
                "Only an accepted reopening can be completed."
            )

        lifecycle.complete()

        return lifecycle

    def recover_case(self, reopening_or_lifecycle):
        lifecycle = self._resolve_lifecycle(
            reopening_or_lifecycle
        )

        if lifecycle.state is not ReopeningState.ACCEPTED:
            raise ValueError(
                "Only an accepted reopening can recover a case."
            )

        if self._workflow.state is not WorkflowState.INVESTIGATING:
            raise ValueError(
                "Case must be INVESTIGATING before recovery."
            )

        return self._workflow

    def _resolve_lifecycle(self, reopening_or_lifecycle):
        if isinstance(
            reopening_or_lifecycle,
            TechnicianCaseReopeningLifecycle,
        ):
            lifecycle = reopening_or_lifecycle

            reopening = lifecycle.reopening

            if reopening.workflow is not self._workflow:
                raise ValueError(
                    "Reopening belongs to a different workflow."
                )

            managed_lifecycle = self._lifecycles.get(
                reopening.reopening_id
            )

            if managed_lifecycle is not lifecycle:
                raise ValueError(
                    "Reopening lifecycle is not managed by "
                    "this manager."
                )

            return lifecycle

        if isinstance(
            reopening_or_lifecycle,
            TechnicianCaseReopening,
        ):
            reopening = reopening_or_lifecycle

            if reopening.workflow is not self._workflow:
                raise ValueError(
                    "Reopening belongs to a different workflow."
                )

            if reopening not in self._reopenings:
                raise ValueError(
                    "Reopening is not managed by this manager."
                )

            return self._lifecycles[
                reopening.reopening_id
            ]

        raise ValueError(
            "Expected a TechnicianCaseReopening or "
            "TechnicianCaseReopeningLifecycle."
        )