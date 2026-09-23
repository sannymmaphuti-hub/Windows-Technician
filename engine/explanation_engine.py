from engine.explanation_rule import ExplanationRule


class ExplanationEngine:

    def __init__(self):
        self._rules = []

    def register_rule(self, rule):
        if not isinstance(rule, ExplanationRule):
            raise ValueError(
                "rule must be an ExplanationRule."
            )

        self._rules.append(rule)

    def evaluate(self, subject, evidence):
        explanations = []

        for rule in self._rules:
            if rule.matches(subject, evidence):
                explanations.append(
                    rule.create_explanation(
                        subject,
                        evidence,
                    )
                )

        return explanations
