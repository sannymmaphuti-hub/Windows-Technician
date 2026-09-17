from engine.explanation import Explanation
from engine.explanation_rule import ExplanationRule
from engine.root_cause_candidate import RootCauseCandidate


class RootCauseExplanationRule(ExplanationRule):

    def matches(self, subject, evidence):
        if not isinstance(subject, RootCauseCandidate):
            raise ValueError(
                "Root cause explanation subject must be "
                "a RootCauseCandidate."
            )

        for evaluation in evidence:
            if evaluation.candidate is subject:
                return True

        return False

    def create_explanation(self, subject, evidence):
        if not isinstance(subject, RootCauseCandidate):
            raise ValueError(
                "Root cause explanation subject must be "
                "a RootCauseCandidate."
            )

        evaluation = None

        for item in evidence:
            if item.candidate is subject:
                evaluation = item
                break

        if evaluation is None:
            raise ValueError(
                "Root cause evaluation is required."
            )

        if evaluation.assessment == "INSUFFICIENT":
            summary = (
                "A possible cause has been identified, "
                "but there is not enough evidence yet."
            )
            details = (
                "The available evidence is insufficient to "
                "support this cause. Further investigation is "
                "needed."
            )

        elif evaluation.assessment == "SUPPORTED":
            summary = (
                "The evidence supports this as a possible cause."
            )
            details = (
                "The available evidence supports this cause, "
                "but it has not been established as the only "
                "possible explanation."
            )

        elif evaluation.assessment == "STRONGLY_SUPPORTED":
            summary = (
                "Strong evidence supports this as a likely cause."
            )
            details = (
                "The available evidence strongly supports this "
                "cause, although diagnosis should still avoid "
                "claiming absolute certainty."
            )

        else:
            raise ValueError(
                "Unsupported root cause assessment."
            )

        return Explanation(
            subject=subject.cause_type,
            summary=summary,
            details=details,
        )