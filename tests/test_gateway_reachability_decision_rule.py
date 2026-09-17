from engine.gateway_reachability_decision_rule import (
    GatewayReachabilityDecisionRule,
)


def test_rule_can_be_created():
    rule = GatewayReachabilityDecisionRule()

    assert rule is not None


def test_rule_matches_when_gateway_reachability_is_missing():
    rule = GatewayReachabilityDecisionRule()

    evidence = {
        "active_adapter": {
            "is_up": True,
        },
    }

    assert rule.matches(evidence) is True


def test_rule_does_not_match_when_gateway_is_reachable():
    rule = GatewayReachabilityDecisionRule()

    evidence = {
        "active_adapter": {
            "is_up": True,
        },
        "gateway_reachable": True,
    }

    assert rule.matches(evidence) is False


def test_rule_does_not_match_when_gateway_is_unreachable():
    rule = GatewayReachabilityDecisionRule()

    evidence = {
        "active_adapter": {
            "is_up": True,
        },
        "gateway_reachable": False,
    }

    assert rule.matches(evidence) is False


def test_rule_does_not_match_when_adapter_is_not_up():
    rule = GatewayReachabilityDecisionRule()

    evidence = {
        "active_adapter": {
            "is_up": False,
        },
    }

    assert rule.matches(evidence) is False


def test_rule_creates_gateway_reachability_decision():
    rule = GatewayReachabilityDecisionRule()

    evidence = {
        "active_adapter": {
            "is_up": True,
        },
    }

    decision = rule.create_decision(evidence)

    assert decision.decision_type == "CHECK_GATEWAY_REACHABILITY"
    assert decision.category == "NETWORK"
    assert decision.priority == "HIGH"


def test_rule_decision_explains_unknown_gateway_reachability():
    rule = GatewayReachabilityDecisionRule()

    evidence = {
        "active_adapter": {
            "is_up": True,
        },
    }

    decision = rule.create_decision(evidence)

    assert "gateway" in decision.reason.lower()
    assert "unknown" in decision.reason.lower()