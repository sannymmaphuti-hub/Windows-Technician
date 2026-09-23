from engine.root_cause_candidate import RootCauseCandidate


class RootCauseEvaluation:

    VALID_ASSESSMENTS = {
        "INSUFFICIENT",
        "SUPPORTED",
        "STRONGLY_SUPPORTED",
    }

    def __init__(
        self,
        candidate,
        supporting_evidence,
        assessment,
        explanation,
    ):
        if not isinstance(
            candidate,
            RootCauseCandidate,
        ):
            raise ValueError(
                "Root cause evaluation candidate "
                "must be a RootCauseCandidate."
            )

        if not isinstance(
            supporting_evidence,
            list,
        ):
            raise ValueError(
                "Root cause evaluation supporting_evidence "
                "must be a list."
            )

        if assessment not in self.VALID_ASSESSMENTS:
            raise ValueError(
                "Root cause evaluation assessment must be "
                "INSUFFICIENT, SUPPORTED, or STRONGLY_SUPPORTED."
            )

        self._validate_text(
            explanation,
            "explanation",
        )

        self.candidate = candidate
        self.supporting_evidence = supporting_evidence
        self.assessment = assessment
        self.explanation = explanation

    def to_evidence(self):
        return {
            "candidate": self.candidate,
            "supporting_evidence": self.supporting_evidence,
            "assessment": self.assessment,
            "explanation": self.explanation,
        }

    @staticmethod
    def _validate_text(value, field_name):

        if not isinstance(value, str):
            raise ValueError(
                f"Root cause evaluation {field_name} "
                "must be a string."
            )

        if not value.strip():
            raise ValueError(
                f"Root cause evaluation {field_name} "
                "cannot be empty."
            )
