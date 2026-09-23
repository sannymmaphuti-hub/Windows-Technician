from engine.finding import Finding
from engine.recommendation import Recommendation
from engine.recommendation_rule import RecommendationRule


class AudienceRecommendationRule(RecommendationRule):

    VALID_AUDIENCES = {
        "USER",
        "TECHNICIAN",
    }

    def matches(self, subject, audience):
        self._validate_finding(subject)
        self._validate_audience(audience)

        return subject.finding_type == "MEMORY_PRESSURE"

    def create_recommendation(self, subject, audience):
        self._validate_finding(subject)
        self._validate_audience(audience)

        if audience == "USER":
            description = (
                "Review which applications are using "
                "a lot of memory."
            )

            rationale = (
                "Your computer is experiencing high "
                "memory pressure."
            )

        else:
            description = (
                "Review memory-intensive processes "
                "contributing to the high memory pressure."
            )

            rationale = (
                "The finding indicates high system memory "
                "pressure and warrants process-level "
                "investigation."
            )

        return Recommendation(
            recommendation_type="REVIEW_MEMORY",
            category=subject.category,
            priority=subject.severity,
            description=description,
            rationale=rationale,
        )

    @staticmethod
    def _validate_finding(finding):
        if not isinstance(finding, Finding):
            raise ValueError(
                "Audience recommendation subject "
                "must be a Finding."
            )

    @classmethod
    def _validate_audience(cls, audience):
        if audience not in cls.VALID_AUDIENCES:
            raise ValueError(
                "Recommendation audience must be "
                "USER or TECHNICIAN."
            )
