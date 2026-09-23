from engine.recommendation import Recommendation


class RemediationDecision:
    def __init__(self, recommendation_type, eligible):
        self.recommendation_type = recommendation_type
        self.eligible = eligible


class RemediationDecisionBoundary:

    ELIGIBLE_PRIORITIES = {
        "HIGH",
        "CRITICAL",
    }

    def evaluate(self, recommendation):
        if not isinstance(recommendation, Recommendation):
            raise ValueError(
                "Recommendation must be a Recommendation object."
            )

        eligible = (
            recommendation.priority
            in self.ELIGIBLE_PRIORITIES
        )

        return RemediationDecision(
            recommendation_type=recommendation.recommendation_type,
            eligible=eligible,
        )
