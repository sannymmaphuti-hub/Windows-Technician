from engine.finding_rule import FindingRule


class FindingEngine:

    def __init__(self):
        self._rules = []

    def register_rule(self, rule):
        if not isinstance(rule, FindingRule):
            raise ValueError("rule must be a FindingRule.")

        self._rules.append(rule)

    def detect(self, signal):
        findings = []

        for rule in self._rules:
            if rule.matches(signal):
                findings.append(rule.create_finding(signal))

        return findings
