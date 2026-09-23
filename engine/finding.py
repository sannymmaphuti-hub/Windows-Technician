class Finding:

    VALID_SEVERITIES = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}

    def __init__(
        self,
        finding_type,
        category,
        severity,
        description,
        supporting_signals=None,
    ):
        self._validate_text(finding_type, "finding_type")
        self._validate_text(category, "category")
        self._validate_text(description, "description")

        if severity not in self.VALID_SEVERITIES:
            raise ValueError(
                "Finding severity must be LOW, MEDIUM, HIGH, or CRITICAL."
            )

        if supporting_signals is None:
            supporting_signals = []

        self.finding_type = finding_type
        self.category = category
        self.severity = severity
        self.description = description
        self.supporting_signals = supporting_signals

    def to_evidence(self):
        return {
            "finding_type": self.finding_type,
            "category": self.category,
            "severity": self.severity,
            "description": self.description,
            "supporting_signals": self.supporting_signals,
        }

    @staticmethod
    def _validate_text(value, field_name):
        if not isinstance(value, str):
            raise ValueError(
                f"Finding {field_name} must be a string."
            )

        if not value.strip():
            raise ValueError(
                f"Finding {field_name} cannot be empty."
            )
