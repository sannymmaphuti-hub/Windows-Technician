from engine.confidence import Confidence
from engine.recommendation import Recommendation
from engine.recommendation_rule import RecommendationRule
from engine.root_cause_candidate import RootCauseCandidate


class ConfidenceAwareRecommendationRule(RecommendationRule):

    def matches(self, subject, evidence):
        if not isinstance(subject, RootCauseCandidate):
            raise ValueError(
                "Confidence-aware recommendation subject "
                "must be a RootCauseCandidate."
            )

        if not isinstance(evidence, list):
            raise ValueError(
                "Confidence-aware recommendation evidence "
                "must be a list."
            )

        for item in evidence:
            if not isinstance(item, Confidence):
                continue

            if item.subject == subject.cause_type:
                return True

        return False

    def create_recommendation(self, subject, evidence):
        if not isinstance(subject, RootCauseCandidate):
            raise ValueError(
                "Confidence-aware recommendation subject "
                "must be a RootCauseCandidate."
            )

        if not isinstance(evidence, list):
            raise ValueError(
                "Confidence-aware recommendation evidence "
                "must be a list."
            )

        confidence = None

        for item in evidence:
            if not isinstance(item, Confidence):
                continue

            if item.subject == subject.cause_type:
                confidence = item
                break

        if confidence is None:
            raise ValueError(
                "No confidence found for candidate."
            )

        if confidence.level == "HIGH":
            recommendation_type = "REVIEW_MEMORY_PROCESS"
            priority = "HIGH"
            description = (
                "Review the memory-intensive process."
            )

        elif confidence.level == "MEDIUM":
            recommendation_type = (
                "INVESTIGATE_MEMORY_PROCESS"
            )
            priority = "MEDIUM"
            description = (
                "Investigate the memory-intensive process."
            )

        else:
            recommendation_type = "GATHER_MORE_EVIDENCE"
            priority = "LOW"
            description = (
                "Gather more evidence before acting "
                "on the suspected cause."
            )

        return Recommendation(
            recommendation_type=recommendation_type,
            category=subject.category,
            priority=priority,
            description=description,
            rationale=(
                f"Recommendation confidence is "
                f"{confidence.level}."
            ),
        )
