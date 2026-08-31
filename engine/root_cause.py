# ==========================================
# Windows Technician v0.3
# ROOT CAUSE CANDIDATE
# ==========================================


class RootCauseCandidate:

    def __init__(
        self,
        cause,
        category,
        confidence,
        evidence=None,
        reason=""
    ):

        self.cause = cause
        self.category = category
        self.confidence = confidence
        self.evidence = evidence or []
        self.reason = reason

        self._validate()

    def _validate(self):

        if not isinstance(self.cause, str):
            raise ValueError(
                "Root cause must be a string."
            )

        if not self.cause.strip():
            raise ValueError(
                "Root cause cannot be empty."
            )

        if not isinstance(self.category, str):
            raise ValueError(
                "Root cause category must be a string."
            )

        if not isinstance(
            self.confidence,
            (int, float)
        ):
            raise ValueError(
                "Root cause confidence must be numeric."
            )

        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                "Root cause confidence must be between 0.0 and 1.0."
            )

        if not isinstance(
            self.evidence,
            list
        ):
            raise ValueError(
                "Root cause evidence must be a list."
            )

        if not isinstance(
            self.reason,
            str
        ):
            raise ValueError(
                "Root cause reason must be a string."
            )

    def confidence_level(self):

        if self.confidence >= 0.80:
            return "HIGH"

        if self.confidence >= 0.50:
            return "MEDIUM"

        return "LOW"

    def to_dict(self):

        return {
            "cause": self.cause,
            "category": self.category,
            "confidence": self.confidence,
            "confidence_level": self.confidence_level(),
            "evidence": self.evidence,
            "reason": self.reason
        }
