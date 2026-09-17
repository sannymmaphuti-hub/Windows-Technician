from engine.diagnostic_action_selection_rule import (
    DiagnosticActionSelectionRule,
)


class StubActionSelectionRule(DiagnosticActionSelectionRule):
    def matches(self, decision_type):
        raise NotImplementedError

    def create_action(self, decision_type):
        raise NotImplementedError


def test_action_selection_rule_defines_matches_contract():
    rule = StubActionSelectionRule()

    assert callable(rule.matches)


def test_action_selection_rule_defines_create_action_contract():
    rule = StubActionSelectionRule()

    assert callable(rule.create_action)


def test_base_rule_matches_is_not_implemented():
    rule = StubActionSelectionRule()

    try:
        rule.matches("CHECK_GATEWAY_REACHABILITY")
    except NotImplementedError:
        pass
    else:
        raise AssertionError("Expected NotImplementedError")


def test_base_rule_create_action_is_not_implemented():
    rule = StubActionSelectionRule()

    try:
        rule.create_action("CHECK_GATEWAY_REACHABILITY")
    except NotImplementedError:
        pass
    else:
        raise AssertionError("Expected NotImplementedError")