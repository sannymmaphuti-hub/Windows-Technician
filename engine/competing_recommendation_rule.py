from engine.recommendation import Recommendation
from engine.recommendation_rule import RecommendationRule
from engine.root_cause_candidate import RootCauseCandidate


class CompetingRecommendationRule(RecommendationRule):

    def matches(self, subject, evidence):
        if not isinstance(subject, list):
            raise ValueError(
                "Competing recommendation candidates "
                "must be a list."
            )

        if len(subject) < 2:
            return False

        for candidate in subject:
            if not isinstance(candidate, RootCauseCandidate):
                raise ValueError(
                    "All competing candidates must be "
                    "RootCauseCandidate objects."
                )

        return evidence is None

    def create_recommendation(self, subject, evidence):
        if not isinstance(subject, list):
            raise ValueError(
                "Competing recommendation candidates "
                "must be a list."
            )

        if len(subject) < 2:
            raise ValueError(
                "At least two competing candidates are required."
            )

        for candidate in subject:
            if not isinstance(candidate, RootCauseCandidate):
                raise ValueError(
                    "All competing candidates must be "
                    "RootCauseCandidate objects."
                )

        if evidence is not None:
            raise ValueError(
                "A primary cause must not exist for "
                "a competing recommendation."
            )

        return Recommendation(
            recommendation_type="INVESTIGATE_COMPETING_CAUSES",
            category=subject[0].category,
            priority="MEDIUM",
            description=(
                "Several possible causes were identified. "
                "More evidence is needed before choosing "
                "a specific action."
            ),
            rationale=(
                "The diagnosis has competing possible causes "
                "and no primary cause has been established."
            ),
        )

