from engine.root_cause_rule import RootCauseRule


class RootCauseEngine:

    def __init__(self):
        self._rules = []

    def register_rule(self, rule):
        if not isinstance(rule, RootCauseRule):
            raise ValueError(
                "rule must be a RootCauseRule."
            )

        self._rules.append(rule)

    def detect(self, findings):
        candidates = []

        for rule in self._rules:
            if rule.matches(findings):
                candidates.append(
                    rule.create_candidate(findings)
                )

        return candidates