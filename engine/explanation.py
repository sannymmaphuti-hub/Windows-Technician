class Explanation:

    VALID_CONFIDENCE_LEVELS = {
        "LOW",
        "MEDIUM",
        "HIGH",
    }

    def __init__(
        self,
        subject,
        summary,
        details,
        confidence=None,
    ):
        self._validate_text(subject, "subject")
        self._validate_text(summary, "summary")
        self._validate_text(details, "details")

        if confidence is not None:
            if confidence not in self.VALID_CONFIDENCE_LEVELS:
                raise ValueError(
                    "Explanation confidence must be "
                    "LOW, MEDIUM, or HIGH."
                )

        self.subject = subject
        self.summary = summary
        self.details = details
        self.confidence = confidence

    def __eq__(self, other):
        if not isinstance(other, Explanation):
            return NotImplemented

        return (
            self.subject == other.subject
            and self.summary == other.summary
            and self.details == other.details
            and self.confidence == other.confidence
        )

    def to_evidence(self):
        evidence = {
            "subject": self.subject,
            "summary": self.summary,
            "details": self.details,
        }

        if self.confidence is not None:
            evidence["confidence"] = self.confidence

        return evidence

    @staticmethod
    def _validate_text(value, field_name):
        if not isinstance(value, str):
            raise ValueError(
                f"Explanation {field_name} must be a string."
            )

        if not value.strip():
            raise ValueError(
                f"Explanation {field_name} cannot be empty."
            )

