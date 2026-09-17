from engine.confidence import Confidence
from engine.explanation import Explanation
from engine.explanation_rule import ExplanationRule
from engine.root_cause_candidate import RootCauseCandidate


class ConfidenceAwareExplanationRule(ExplanationRule):

    def matches(self, subject, evidence):
        if not isinstance(subject, RootCauseCandidate):
            raise ValueError(
                "Confidence-aware explanation subject must be "
                "a RootCauseCandidate."
            )

        for confidence in evidence:
            if not isinstance(confidence, Confidence):
                continue

            if confidence.subject == subject.cause_type:
                return True

        return False

    def create_explanation(self, subject, evidence):
        if not isinstance(subject, RootCauseCandidate):
            raise ValueError(
                "Confidence-aware explanation subject must be "
                "a RootCauseCandidate."
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
                "Confidence is required."
            )

        if confidence.level == "LOW":
            summary = (
                "A possible cause has been identified, "
                "but there is not enough evidence yet."
            )
            details = (
                "The evidence is uncertain, so this cause "
                "should be investigated further."
            )

        elif confidence.level == "MEDIUM":
            summary = (
                "The evidence supports this as a possible cause."
            )
            details = (
                "The available evidence supports this cause, "
                "but other explanations may still be possible."
            )

        elif confidence.level == "HIGH":
            summary = (
                "Strong evidence supports this as a likely cause."
            )
            details = (
                "The available evidence strongly supports this "
                "cause, while avoiding a claim of absolute certainty."
            )

        else:
            raise ValueError(
                "Unsupported confidence level."
            )

        return Explanation(
            subject=subject.cause_type,
            summary=summary,
            details=details,
            confidence=confidence.level,
        )