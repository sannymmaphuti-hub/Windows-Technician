from engine.confidence import Confidence
from engine.explanation import Explanation
from engine.explanation_rule import ExplanationRule
from engine.root_cause_candidate import RootCauseCandidate


class CompetingRootCauseExplanationRule(ExplanationRule):

    def matches(self, subject, evidence):
        self._validate_candidates(subject)

        if not isinstance(evidence, dict):
            raise ValueError(
                "Competing root cause evidence must be a dictionary."
            )

        primary_cause = evidence.get("primary_cause")

        if primary_cause is not None:
            return False

        return len(subject) >= 2

    def create_explanation(self, subject, evidence):
        self._validate_candidates(subject)

        if not isinstance(evidence, dict):
            raise ValueError(
                "Competing root cause evidence must be a dictionary."
            )

        if len(subject) < 2:
            raise ValueError(
                "At least two root cause candidates are required."
            )

        if evidence.get("primary_cause") is not None:
            raise ValueError(
                "Competing root cause explanation requires "
                "no primary cause."
            )

        confidences = evidence.get("confidences", [])

        confidence_levels = []

        for confidence in confidences:
            if not isinstance(confidence, Confidence):
                continue

            for candidate in subject:
                if confidence.subject == candidate.cause_type:
                    confidence_levels.append(confidence.level)
                    break

        explanation_confidence = None

        if confidence_levels:
            if all(
                level == "HIGH"
                for level in confidence_levels
            ):
                explanation_confidence = "HIGH"

            elif all(
                level in {"MEDIUM", "HIGH"}
                for level in confidence_levels
            ):
                explanation_confidence = "MEDIUM"

            else:
                explanation_confidence = "LOW"

        return Explanation(
            subject="COMPETING_ROOT_CAUSES",
            summary=(
                "Several possible causes were identified, "
                "but there is not enough evidence to establish "
                "a single primary cause."
            ),
            details=(
                "The available evidence supports more than one "
                "possible explanation. Further investigation is "
                "needed to determine which cause best explains "
                "the problem."
            ),
            confidence=explanation_confidence,
        )

    @staticmethod
    def _validate_candidates(candidates):
        if not isinstance(candidates, list):
            raise ValueError(
                "Root cause candidates must be provided as a list."
            )

        for candidate in candidates:
            if not isinstance(candidate, RootCauseCandidate):
                raise ValueError(
                    "All root cause candidates must be "
                    "RootCauseCandidate objects."
                )