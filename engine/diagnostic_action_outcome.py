class DiagnosticActionOutcome:
    def __init__(
        self,
        action_type,
        evidence,
    ):
        if not isinstance(action_type, str) or not action_type.strip():
            raise ValueError(
                "action_type must be a non-empty string."
            )

        if not isinstance(evidence, dict):
            raise ValueError(
                "evidence must be a dictionary."
            )

        self.action_type = action_type
        self.evidence = dict(evidence)

    def to_dict(self):
        return {
            "action_type": self.action_type,
            "evidence": dict(self.evidence),
        }