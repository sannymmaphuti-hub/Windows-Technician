class Recommendation:

    VALID_PRIORITIES = {
        "LOW",
        "MEDIUM",
        "HIGH",
        "CRITICAL",
    }

    def __init__(
        self,
        recommendation_type,
        category,
        priority,
        description,
        rationale,
    ):
        self._validate_text(
            recommendation_type,
            "recommendation_type",
        )
        self._validate_text(
            category,
            "category",
        )
        self._validate_text(
            description,
            "description",
        )
        self._validate_text(
            rationale,
            "rationale",
        )

        if priority not in self.VALID_PRIORITIES:
            raise ValueError(
                "Recommendation priority must be "
                "LOW, MEDIUM, HIGH, or CRITICAL."
            )

        self.recommendation_type = recommendation_type
        self.category = category
        self.priority = priority
        self.description = description
        self.rationale = rationale

    def to_evidence(self):
        return {
            "recommendation_type": self.recommendation_type,
            "category": self.category,
            "priority": self.priority,
            "description": self.description,
            "rationale": self.rationale,
        }

    @staticmethod
    def _validate_text(value, field_name):
        if not isinstance(value, str):
            raise ValueError(
                f"Recommendation {field_name} must be a string."
            )

        if not value.strip():
            raise ValueError(
                f"Recommendation {field_name} cannot be empty."
            )
