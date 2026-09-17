from engine.finding import Finding
from engine.recommendation import Recommendation
from engine.recommendation_rule import RecommendationRule


class RiskAwareRecommendationRule(RecommendationRule):

    def matches(self, finding):
        if not isinstance(finding, Finding):
            raise ValueError(
                "Risk-aware recommendation subject "
                "must be a Finding."
            )

        return finding.finding_type == "MEMORY_PRESSURE"

    def create_recommendation(self, finding):
        if not isinstance(finding, Finding):
            raise ValueError(
                "Risk-aware recommendation subject "
                "must be a Finding."
            )

        if finding.severity == "CRITICAL":
            recommendation_type = "ESCALATE_MEMORY_ISSUE"

        elif finding.severity == "HIGH":
            recommendation_type = "PRIORITIZE_MEMORY_REVIEW"

        else:
            recommendation_type = "REVIEW_MEMORY"

        return Recommendation(
            recommendation_type=recommendation_type,
            category=finding.category,
            priority=finding.severity,
            description=(
                "Review the memory issue carefully."
            ),
            rationale=(
                f"The finding severity is "
                f"{finding.severity}."
            ),
        )