import pytest

from engine.diagnostic_action_selection_rule import (
    DiagnosticActionSelectionRule,
)


def test_action_selection_rule_cannot_be_instantiated_directly():
    with pytest.raises(TypeError):
        DiagnosticActionSelectionRule()


def test_action_selection_rule_requires_matches_implementation():
    class IncompleteRule(DiagnosticActionSelectionRule):
        def create_action(self, decision_type):
            return {"type": decision_type}

    with pytest.raises(TypeError):
        IncompleteRule()


def test_action_selection_rule_requires_create_action_implementation():
    class IncompleteRule(DiagnosticActionSelectionRule):
        def matches(self, decision_type):
            return True

    with pytest.raises(TypeError):
        IncompleteRule()


def test_concrete_action_selection_rule_implements_both_methods():
    class ConcreteRule(DiagnosticActionSelectionRule):
        def matches(self, decision_type):
            return decision_type == "CHECK_GATEWAY_REACHABILITY"

        def create_action(self, decision_type):
            return {"type": decision_type}

    rule = ConcreteRule()

    assert rule.matches("CHECK_GATEWAY_REACHABILITY") is True
    assert rule.matches("OTHER_ACTION") is False
    assert rule.create_action("CHECK_GATEWAY_REACHABILITY") == {
        "type": "CHECK_GATEWAY_REACHABILITY"
    }
