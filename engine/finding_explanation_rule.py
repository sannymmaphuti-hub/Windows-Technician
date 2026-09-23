from engine.explanation import Explanation
from engine.explanation_rule import ExplanationRule
from engine.finding import Finding


class FindingExplanationRule(ExplanationRule):

    def matches(self, subject, evidence):
        if not isinstance(subject, Finding):
            raise ValueError(
                "Finding explanation subject must be a Finding."
            )

        return subject.finding_type == "MEMORY_PRESSURE"

    def create_explanation(self, subject, evidence):
        if not isinstance(subject, Finding):
            raise ValueError(
                "Finding explanation subject must be a Finding."
            )

        return Explanation(
            subject=subject.finding_type,
            summary="Your computer is using a lot of memory.",
            details=(
                "This can make Windows and applications "
                "respond slowly."
            ),
        )
