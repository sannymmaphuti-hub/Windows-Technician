class DiagnosticAction:
    def __init__(
        self,
        action_type,
        category,
        description,
    ):
        if not isinstance(action_type, str) or not action_type.strip():
            raise ValueError(
                "action_type must be a non-empty string."
            )

        if not isinstance(category, str) or not category.strip():
            raise ValueError(
                "category must be a non-empty string."
            )

        if not isinstance(description, str) or not description.strip():
            raise ValueError(
                "description must be a non-empty string."
            )

        self.action_type = action_type
        self.category = category
        self.description = description

    def to_dict(self):
        return {
            "action_type": self.action_type,
            "category": self.category,
            "description": self.description,
        }