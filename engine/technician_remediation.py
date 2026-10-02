from engine.recommendation_remediation_adapter import (
    RecommendationRemediationAdapter,
)
from engine.remediation_action_planner import RemediationActionPlanner
from engine.remediation_coordinator import RemediationCoordinator
from engine.technician_decision import (
    TechnicianDecision,
    TechnicianDecisionType,
)
from engine.technician_workflow import (
    TechnicianWorkflow,
    WorkflowState,
)


class TechnicianRemediation:

    def __init__(
        self,
        workflow,
        adapter=None,
        planner=None,
        coordinator=None,
    ):
        if not isinstance(workflow, TechnicianWorkflow):
            raise ValueError(
                "TechnicianRemediation requires a TechnicianWorkflow."
            )

        self._workflow = workflow
        self._adapter = (
            adapter or RecommendationRemediationAdapter()
        )
        self._planner = (
            planner or RemediationActionPlanner()
        )
        self._coordinator = (
            coordinator or RemediationCoordinator()
        )

        self._decision = None
        self._action = None
        self._result = None
        self._active = False

    @property
    def workflow(self):
        return self._workflow

    @property
    def decision(self):
        return self._decision

    @property
    def recommendation(self):
        if self._decision is None:
            return None

        return self._decision.recommendation

    @property
    def action(self):
        return self._action

    @property
    def result(self):
        return self._result

    @property
    def is_active(self):
        return self._active

    @property
    def is_complete(self):
        return self._result is not None

    def start(self, decision):
        if not isinstance(decision, TechnicianDecision):
            raise ValueError(
                "TechnicianRemediation requires a TechnicianDecision."
            )

        if decision.workflow is not self._workflow:
            raise ValueError(
                "TechnicianDecision belongs to a different workflow."
            )

        if decision.decision_type is not TechnicianDecisionType.ACCEPT:
            raise ValueError(
                "Only an ACCEPT decision can start remediation."
            )

        if self._active:
            raise ValueError(
                "Remediation is already active."
            )

        if self._result is not None:
            raise ValueError(
                "Completed remediation cannot be restarted."
            )

        if self._workflow.state not in {
            WorkflowState.ACTION_REQUIRED,
            WorkflowState.REMEDIATING,
        }:
            raise ValueError(
                "Remediation can only start while workflow is "
                "ACTION_REQUIRED or REMEDIATING."
            )

        self._decision = decision

        if self._workflow.state is WorkflowState.ACTION_REQUIRED:
            self._workflow.start_remediation()

        self._active = True

    def execute(self, expected=None, observed=None):
        if not self._active:
            raise ValueError(
                "Remediation must be active before execution."
            )

        if self._result is not None:
            raise ValueError(
                "Remediation has already been executed."
            )

        planner_input = self._adapter.to_planner_input(
            self.recommendation
        )

        action = self._planner.create_action(
            planner_input
        )

        if action is None:
            raise ValueError(
                "Recommendation could not be converted into "
                "a remediation action."
            )

        result = self._coordinator.execute(
            action,
            expected=expected,
            observed=observed,
        )

        self._action = action
        self._result = result
        self._active = False

        if result.execution_status == "EXECUTED":
            self._workflow.start_verification()

        return result