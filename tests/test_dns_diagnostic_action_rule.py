from engine.diagnostic_action import DiagnosticAction
from engine.dns_diagnostic_action_rule import (
    DNSDiagnosticActionRule,
)


def test_dns_action_rule_matches_dns_decision():
    rule = DNSDiagnosticActionRule()

    assert rule.matches("CHECK_DNS_RESOLUTION") is True


def test_dns_action_rule_does_not_match_other_decisions():
    rule = DNSDiagnosticActionRule()

    assert rule.matches("CHECK_GATEWAY_REACHABILITY") is False
    assert rule.matches("CHECK_INTERNET_CONNECTIVITY") is False


def test_dns_action_rule_creates_diagnostic_action():
    rule = DNSDiagnosticActionRule()

    action = rule.create_action("CHECK_DNS_RESOLUTION")

    assert isinstance(action, DiagnosticAction)
    assert action.action_type == "TEST_DNS_RESOLUTION"
    assert action.category == "NETWORK"


def test_dns_action_rule_rejects_invalid_decision():
    rule = DNSDiagnosticActionRule()

    try:
        rule.create_action("UNKNOWN_DECISION")
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")


def test_dns_action_rule_description_is_meaningful():
    rule = DNSDiagnosticActionRule()

    action = rule.create_action("CHECK_DNS_RESOLUTION")

    assert action.description
    assert "dns" in action.description.lower()