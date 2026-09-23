from engine.correlation_rule import CorrelationRule


class CorrelationEngine:

    def __init__(self):
        self._rules = []

    def register_rule(self, rule):
        if not isinstance(rule, CorrelationRule):
            raise ValueError("rule must be a CorrelationRule.")

        self._rules.append(rule)

    def detect(self, findings):
        correlations = []

        for rule in self._rules:
            if rule.matches(findings):
                correlations.append(
                    rule.create_correlation(findings)
                )

        return correlations
