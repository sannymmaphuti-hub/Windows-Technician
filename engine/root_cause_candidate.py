class RootCauseCandidate:

    def __init__(
        self,
        cause_type,
        category,
        explanation,
    ):
        self._validate_text(cause_type, "cause_type")
        self._validate_text(category, "category")
        self._validate_text(explanation, "explanation")

        self.cause_type = cause_type
        self.category = category
        self.explanation = explanation

    def to_evidence(self):
        return {
            "cause_type": self.cause_type,
            "category": self.category,
            "explanation": self.explanation,
        }

    @staticmethod
    def _validate_text(value, field_name):
        if not isinstance(value, str):
            raise ValueError(
                f"Root cause candidate {field_name} must be a string."
            )

        if not value.strip():
            raise ValueError(
                f"Root cause candidate {field_name} cannot be empty."
            )