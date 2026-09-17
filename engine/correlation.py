class Correlation:

    VALID_STRENGTHS = {"LOW", "MEDIUM", "HIGH"}

    def __init__(
        self,
        correlation_type,
        findings,
        strength,
        explanation,
    ):
        self._validate_text(correlation_type, "correlation_type")
        self._validate_findings(findings)
        self._validate_text(explanation, "explanation")

        if strength not in self.VALID_STRENGTHS:
            raise ValueError(
                "Correlation strength must be LOW, MEDIUM, or HIGH."
            )

        self.correlation_type = correlation_type
        self.findings = findings
        self.strength = strength
        self.explanation = explanation

    def to_evidence(self):
        return {
            "correlation_type": self.correlation_type,
            "findings": self.findings,
            "strength": self.strength,
            "explanation": self.explanation,
        }

    @staticmethod
    def _validate_text(value, field_name):
        if not isinstance(value, str):
            raise ValueError(
                f"Correlation {field_name} must be a string."
            )

        if not value.strip():
            raise ValueError(
                f"Correlation {field_name} cannot be empty."
            )

    @staticmethod
    def _validate_findings(findings):
        if not isinstance(findings, list) or not findings:
            raise ValueError(
                "Correlation findings must be a non-empty list."
            )