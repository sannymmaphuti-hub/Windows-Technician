from engine.confidence_rule import ConfidenceRule


class ConfidenceEngine:

    def __init__(self):

        self._rules = []

    def register_rule(self, rule):

        if not isinstance(rule, ConfidenceRule):
            raise ValueError(
                "rule must be a ConfidenceRule."
            )

        self._rules.append(rule)

    def evaluate(
        self,
        subject,
        evidence,
    ):

        confidences = []

        for rule in self._rules:

            if rule.matches(
                subject,
                evidence,
            ):
                confidences.append(
                    rule.create_confidence(
                        subject,
                        evidence,
                    )
                )

        return confidences
