from engine.diagnostic_action import DiagnosticAction


class DiagnosticActionSelectionOrchestrator:
    def __init__(self):
        self.rules = []

    def register_rule(self, rule):
        if not callable(getattr(rule, "matches", None)):
            raise ValueError(
                "rule must provide a callable matches method."
            )

        if not callable(getattr(rule, "create_action", None)):
            raise ValueError(
                "rule must provide a callable create_action method."
            )

        self.rules.append(rule)

    def select(self, decision_type):
        if not isinstance(decision_type, str) or not decision_type.strip():
            raise ValueError(
                "decision_type must be a non-empty string."
            )

        for rule in self.rules:
            if rule.matches(decision_type):
                action = rule.create_action(decision_type)

                if not isinstance(action, DiagnosticAction):
                    raise ValueError(
                        "rule create_action must return a DiagnosticAction."
                    )

                return action

        return None
