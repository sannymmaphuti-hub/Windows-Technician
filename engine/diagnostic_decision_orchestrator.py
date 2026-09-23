class DiagnosticDecisionOrchestrator:
    def __init__(self):
        self.rules = []

    def register_rule(self, rule):
        if not callable(getattr(rule, "matches", None)):
            raise ValueError(
                "rule must provide a callable matches method."
            )

        if not callable(getattr(rule, "create_decision", None)):
            raise ValueError(
                "rule must provide a callable create_decision method."
            )

        self.rules.append(rule)

    def decide(self, evidence):
        if not isinstance(evidence, dict):
            raise ValueError("evidence must be a dictionary.")

        for rule in self.rules:
            if rule.matches(evidence):
                return [rule.create_decision(evidence)]

        return []
