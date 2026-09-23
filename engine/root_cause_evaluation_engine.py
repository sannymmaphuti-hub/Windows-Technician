from engine.root_cause_evaluation_rule import (
    RootCauseEvaluationRule,
)


class RootCauseEvaluationEngine:

    def __init__(self):
        self._rules = []

    def register_rule(self, rule):

        if not isinstance(
            rule,
            RootCauseEvaluationRule,
        ):
            raise ValueError(
                "rule must be a RootCauseEvaluationRule."
            )

        self._rules.append(rule)

    def evaluate(
        self,
        candidate,
        findings,
    ):
        evaluations = []

        for rule in self._rules:

            if rule.matches(
                candidate,
                findings,
            ):
                evaluations.append(
                    rule.create_evaluation(
                        candidate,
                        findings,
                    )
                )

        return evaluations
