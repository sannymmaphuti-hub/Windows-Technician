class DiagnosticDecision:
    VALID_PRIORITIES = {"LOW", "MEDIUM", "HIGH"}

    def __init__(
        self,
        decision_type,
        category,
        reason,
        priority,
    ):
        if not isinstance(decision_type, str) or not decision_type.strip():
            raise ValueError("decision_type must be a non-empty string.")

        if not isinstance(category, str) or not category.strip():
            raise ValueError("category must be a non-empty string.")

        if not isinstance(reason, str) or not reason.strip():
            raise ValueError("reason must be a non-empty string.")

        if priority not in self.VALID_PRIORITIES:
            raise ValueError(
                f"priority must be one of {self.VALID_PRIORITIES}."
            )

        self.decision_type = decision_type
        self.category = category
        self.reason = reason
        self.priority = priority

    def to_dict(self):
        return {
            "decision_type": self.decision_type,
            "category": self.category,
            "reason": self.reason,
            "priority": self.priority,
        }