from engine.network_root_cause_recommendation_rule import (
    NetworkRootCauseRecommendationRule,
)


class NetworkRecommendationOrchestrator:

    def __init__(self, recommendation_rule=None):

        if recommendation_rule is None:
            recommendation_rule = (
                NetworkRootCauseRecommendationRule()
            )

        self.recommendation_rule = recommendation_rule

    def recommend(self, primary_cause, evaluations):

        if primary_cause is None:
            return []

        recommendations = []

        if self.recommendation_rule.matches(
            primary_cause,
            evaluations,
        ):
            recommendations.append(
                self.recommendation_rule.create_recommendation(
                    primary_cause,
                    evaluations,
                )
            )

        return recommendations
