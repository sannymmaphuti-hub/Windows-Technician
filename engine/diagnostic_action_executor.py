from engine.diagnostic_action import DiagnosticAction
from engine.diagnostic_action_outcome import DiagnosticActionOutcome


class DiagnosticActionExecutor:
    def __init__(self):
        self.operations = {}

    def register_operation(self, action_type, operation):
        if not isinstance(action_type, str) or not action_type.strip():
            raise ValueError(
                "action_type must be a non-empty string."
            )

        if not callable(operation):
            raise ValueError(
                "operation must be callable."
            )

        self.operations[action_type] = operation

    def execute(self, action):
        if not isinstance(action, DiagnosticAction):
            raise ValueError(
                "action must be a DiagnosticAction."
            )

        operation = self.operations.get(action.action_type)

        if operation is None:
            raise ValueError(
                f"No operation registered for diagnostic action: "
                f"{action.action_type}."
            )

        evidence = operation()

        if not isinstance(evidence, dict):
            raise ValueError(
                "diagnostic operation must return an evidence dictionary."
            )

        return DiagnosticActionOutcome(
            action_type=action.action_type,
            evidence=evidence,
        )
