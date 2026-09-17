from engine.recommendation import Recommendation


class RecommendationRemediationAdapter:

    PRIORITY_TO_SEVERITY = {
        "LOW": "NORMAL",
        "MEDIUM": "WARNING",
        "HIGH": "WARNING",
        "CRITICAL": "CRITICAL",
    }

    def to_planner_input(self, recommendation):
        if not isinstance(recommendation, Recommendation):
            raise ValueError(
                "recommendation must be a Recommendation."
            )

        return {
            "recommendation": recommendation.description,
            "category": recommendation.category,
            "severity": self.PRIORITY_TO_SEVERITY[
                recommendation.priority
            ],
        }