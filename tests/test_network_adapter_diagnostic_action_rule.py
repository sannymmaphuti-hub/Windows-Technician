from engine.diagnostic_action import DiagnosticAction
from engine.network_adapter_diagnostic_action_rule import (
    NetworkAdapterDiagnosticActionRule,
)


def test_network_adapter_action_rule_matches_adapter_decision():
    rule = NetworkAdapterDiagnosticActionRule()

    assert rule.matches("CHECK_NETWORK_ADAPTER") is True


def test_network_adapter_action_rule_does_not_match_other_decisions():
    rule = NetworkAdapterDiagnosticActionRule()

    assert rule.matches("CHECK_GATEWAY_REACHABILITY") is False
    assert rule.matches("CHECK_DNS_RESOLUTION") is False


def test_network_adapter_action_rule_creates_diagnostic_action():
    rule = NetworkAdapterDiagnosticActionRule()

    action = rule.create_action("CHECK_NETWORK_ADAPTER")

    assert isinstance(action, DiagnosticAction)
    assert action.action_type == "COLLECT_NETWORK_ADAPTER_STATE"
    assert action.category == "NETWORK"


def test_network_adapter_action_rule_rejects_invalid_decision():
    rule = NetworkAdapterDiagnosticActionRule()

    try:
        rule.create_action("UNKNOWN_DECISION")
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")


def test_network_adapter_action_rule_description_is_meaningful():
    rule = NetworkAdapterDiagnosticActionRule()

    action = rule.create_action("CHECK_NETWORK_ADAPTER")

    assert action.description
    assert "network adapter" in action.description.lower()