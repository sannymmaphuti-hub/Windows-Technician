from engine.recommendation import Recommendation
from engine.recommendation_rule import RecommendationRule
from engine.root_cause_candidate import RootCauseCandidate
from engine.root_cause_evaluation import RootCauseEvaluation


class RootCauseRecommendationRule(RecommendationRule):

    def matches(self, subject, evidence):
        if not isinstance(subject, RootCauseCandidate):
            raise ValueError(
                "Root cause recommendation subject "
                "must be a RootCauseCandidate."
            )

        if not isinstance(evidence, list):
            raise ValueError(
                "Root cause recommendation evidence "
                "must be a list."
            )

        for item in evidence:
            if not isinstance(item, RootCauseEvaluation):
                continue

            if item.candidate is not subject:
                continue

            if item.assessment in {
                "SUPPORTED",
                "STRONGLY_SUPPORTED",
            }:
                return True

        return False

    def create_recommendation(self, subject, evidence):
        if not isinstance(subject, RootCauseCandidate):
            raise ValueError(
                "Root cause recommendation subject "
                "must be a RootCauseCandidate."
            )

        if not isinstance(evidence, list):
            raise ValueError(
                "Root cause recommendation evidence "
                "must be a list."
            )

        evaluation = None

        for item in evidence:
            if not isinstance(item, RootCauseEvaluation):
                continue

            if item.candidate is subject:
                evaluation = item
                break

        if evaluation is None:
            raise ValueError(
                "No root cause evaluation found for candidate."
            )

        if evaluation.assessment == "STRONGLY_SUPPORTED":
            priority = "HIGH"
        else:
            priority = "MEDIUM"

        return Recommendation(
            recommendation_type="REVIEW_MEMORY_PROCESS",
            category="MEMORY",
            priority=priority,
            description=(
                "Review the memory-intensive process."
            ),
            rationale=(
                "Evidence supports a memory-intensive "
                "process as a possible contributor."
            ),
        )