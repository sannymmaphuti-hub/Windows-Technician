 # ==========================================
# Windows Technician
# DIAGNOSTIC CONFIDENCE
# ==========================================


class ConfidenceCalculator:

    MIN_CONFIDENCE = 0.0
    MAX_CONFIDENCE = 1.0

    def calculate(self, evidence_strength):

        if evidence_strength < self.MIN_CONFIDENCE:
            return self.MIN_CONFIDENCE

        if evidence_strength > self.MAX_CONFIDENCE:
            return self.MAX_CONFIDENCE

        return float(evidence_strength)

    def classify(self, confidence):

        if confidence >= 0.80:
            return "HIGH"

        if confidence >= 0.50:
            return "MEDIUM"

        return "LOW"


class Confidence:

    VALID_LEVELS = {"LOW", "MEDIUM", "HIGH"}

    def __init__(
        self,
        subject,
        level,
        explanation,
    ):
        self._validate_text(subject, "subject")
        self._validate_text(explanation, "explanation")

        if level not in self.VALID_LEVELS:
            raise ValueError(
                "Confidence level must be LOW, MEDIUM, or HIGH."
            )

        self.subject = subject
        self.level = level
        self.explanation = explanation

    def to_evidence(self):

        return {
            "subject": self.subject,
            "level": self.level,
            "explanation": self.explanation,
        }

    @staticmethod
    def _validate_text(value, field_name):

        if not isinstance(value, str):
            raise ValueError(
                f"Confidence {field_name} must be a string."
            )

        if not value.strip():
            raise ValueError(
                f"Confidence {field_name} cannot be empty."
            )
