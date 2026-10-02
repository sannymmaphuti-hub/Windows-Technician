from engine.recommendation import Recommendation
from engine.technician_recovery_cycle_history import (
    TechnicianRecoveryCycleHistory,
)
from engine.technician_workflow import TechnicianWorkflow


class TechnicianRecommendationDetail:

    def __init__(
        self,
        workflow,
        cycle_history,
        recommendation,
    ):
        if not isinstance(
            workflow,
            TechnicianWorkflow,
        ):
            raise ValueError(
                "TechnicianRecommendationDetail requires a "
                "TechnicianWorkflow."
            )

        if not isinstance(
            cycle_history,
            TechnicianRecoveryCycleHistory,
        ):
            raise ValueError(
                "TechnicianRecommendationDetail requires a "
                "TechnicianRecoveryCycleHistory."
            )

        if cycle_history.workflow is not workflow:
            raise ValueError(
                "Recovery cycle history belongs to a "
                "different workflow."
            )

        if not isinstance(
            recommendation,
            Recommendation,
        ):
            raise ValueError(
                "TechnicianRecommendationDetail requires a "
                "Recommendation."
            )

        if recommendation not in workflow.case.recommendations:
            raise ValueError(
                "Recommendation does not belong to the workflow case."
            )

        self._workflow = workflow
        self._cycle_history = cycle_history
        self._recommendation = recommendation

    @property
    def workflow(self):
        return self._workflow

    @property
    def cycle_history(self):
        return self._cycle_history

    @property
    def recommendation(self):
        return self._recommendation

    @property
    def recommendation_type(self):
        return self._recommendation.recommendation_type

    @property
    def category(self):
        return self._recommendation.category

    @property
    def priority(self):
        return self._recommendation.priority

    @property
    def description(self):
        return self._recommendation.description

    @property
    def rationale(self):
        return self._recommendation.rationale