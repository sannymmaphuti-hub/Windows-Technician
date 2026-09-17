from engine.confidence import Confidence
from engine.confidence_rule import ConfidenceRule


class RootCauseConfidenceRule(ConfidenceRule):

    def matches(self, subject, evidence):
        for evaluation in evidence:
            if evaluation.candidate is subject:
                return True

        return False

    def create_confidence(self, subject, evidence):
        evaluation = None

        for item in evidence:
            if item.candidate is subject:
                evaluation = item
                break

        if evaluation.assessment == "STRONGLY_SUPPORTED":
            level = "HIGH"
        elif evaluation.assessment == "SUPPORTED":
            level = "MEDIUM"
        else:
            level = "LOW"

        return Confidence(
            subject=subject.cause_type,
            level=level,
            explanation=(
                f"Confidence is {level} because the root cause "
                f"evaluation is {evaluation.assessment}."
            ),
        )