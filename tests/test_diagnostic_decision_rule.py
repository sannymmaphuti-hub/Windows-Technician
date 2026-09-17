import pytest

from engine.diagnostic_decision_rule import DiagnosticDecisionRule


def test_diagnostic_decision_rule_is_abstract():
    with pytest.raises(TypeError):
        DiagnosticDecisionRule()


def test_diagnostic_decision_rule_requires_matches():
    class IncompleteRule(DiagnosticDecisionRule):
        def create_decision(self, evidence):
            return None

    with pytest.raises(TypeError):
        IncompleteRule()


def test_diagnostic_decision_rule_requires_create_decision():
    class IncompleteRule(DiagnosticDecisionRule):
        def matches(self, evidence):
            return True

    with pytest.raises(TypeError):
        IncompleteRule()


def test_diagnostic_decision_rule_can_be_implemented():
    class TestRule(DiagnosticDecisionRule):
        def matches(self, evidence):
            return evidence.get("ready") is True

        def create_decision(self, evidence):
            return "decision"

    rule = TestRule()

    assert rule.matches({"ready": True}) is True
    assert rule.create_decision({"ready": True}) == "decision"