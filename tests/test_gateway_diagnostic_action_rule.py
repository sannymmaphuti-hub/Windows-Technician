from engine.diagnostic_action import DiagnosticAction
from engine.gateway_diagnostic_action_rule import (
    GatewayDiagnosticActionRule,
)


def test_gateway_action_rule_matches_gateway_decision():
    rule = GatewayDiagnosticActionRule()

    assert rule.matches("CHECK_GATEWAY_REACHABILITY") is True


def test_gateway_action_rule_does_not_match_other_decisions():
    rule = GatewayDiagnosticActionRule()

    assert rule.matches("CHECK_DNS_RESOLUTION") is False
    assert rule.matches("CHECK_INTERNET_CONNECTIVITY") is False


def test_gateway_action_rule_creates_diagnostic_action():
    rule = GatewayDiagnosticActionRule()

    action = rule.create_action("CHECK_GATEWAY_REACHABILITY")

    assert isinstance(action, DiagnosticAction)
    assert action.action_type == "PING_DEFAULT_GATEWAY"
    assert action.category == "NETWORK"


def test_gateway_action_rule_rejects_invalid_decision():
    rule = GatewayDiagnosticActionRule()

    try:
        rule.create_action("UNKNOWN_DECISION")
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")


def test_gateway_action_rule_description_is_meaningful():
    rule = GatewayDiagnosticActionRule()

    action = rule.create_action("CHECK_GATEWAY_REACHABILITY")

    assert action.description
    assert "gateway" in action.description.lower()