from engine.finding import Finding
from engine.recommendation import Recommendation
from engine.recommendation_rule import RecommendationRule


class MemoryRecommendationRule(RecommendationRule):

    def matches(self, finding):
        if not isinstance(finding, Finding):
            raise ValueError(
                "Memory recommendation subject must be a Finding."
            )

        return finding.finding_type == "MEMORY_PRESSURE"

    def create_recommendation(self, finding):
        if not isinstance(finding, Finding):
            raise ValueError(
                "Memory recommendation subject must be a Finding."
            )

        return Recommendation(
            recommendation_type="REVIEW_MEMORY",
            category="MEMORY",
            priority=finding.severity,
            description=(
                "Review memory-intensive processes."
            ),
            rationale=(
                "High memory pressure was detected."
            ),
        )
