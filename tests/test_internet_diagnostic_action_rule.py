from engine.diagnostic_action import DiagnosticAction
from engine.internet_diagnostic_action_rule import (
    InternetDiagnosticActionRule,
)


def test_internet_action_rule_matches_internet_decision():
    rule = InternetDiagnosticActionRule()

    assert rule.matches("CHECK_INTERNET_CONNECTIVITY") is True


def test_internet_action_rule_does_not_match_other_decisions():
    rule = InternetDiagnosticActionRule()

    assert rule.matches("CHECK_GATEWAY_REACHABILITY") is False
    assert rule.matches("CHECK_DNS_RESOLUTION") is False


def test_internet_action_rule_creates_diagnostic_action():
    rule = InternetDiagnosticActionRule()

    action = rule.create_action("CHECK_INTERNET_CONNECTIVITY")

    assert isinstance(action, DiagnosticAction)
    assert action.action_type == "TEST_INTERNET_CONNECTIVITY"
    assert action.category == "NETWORK"


def test_internet_action_rule_rejects_invalid_decision():
    rule = InternetDiagnosticActionRule()

    try:
        rule.create_action("UNKNOWN_DECISION")
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")


def test_internet_action_rule_description_is_meaningful():
    rule = InternetDiagnosticActionRule()

    action = rule.create_action("CHECK_INTERNET_CONNECTIVITY")

    assert action.description
    assert "internet" in action.description.lower()