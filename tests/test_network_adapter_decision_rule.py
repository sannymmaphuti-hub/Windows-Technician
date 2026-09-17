from engine.network_adapter_decision_rule import NetworkAdapterDecisionRule


def test_rule_can_be_created():
    rule = NetworkAdapterDecisionRule()

    assert rule is not None


def test_rule_matches_when_active_adapter_is_missing():
    rule = NetworkAdapterDecisionRule()

    evidence = {}

    assert rule.matches(evidence) is True


def test_rule_matches_when_active_adapter_state_is_unknown():
    rule = NetworkAdapterDecisionRule()

    evidence = {
        "active_adapter": {},
    }

    assert rule.matches(evidence) is True


def test_rule_does_not_match_when_adapter_state_is_known_up():
    rule = NetworkAdapterDecisionRule()

    evidence = {
        "active_adapter": {
            "is_up": True,
        },
    }

    assert rule.matches(evidence) is False


def test_rule_does_not_match_when_adapter_state_is_known_down():
    rule = NetworkAdapterDecisionRule()

    evidence = {
        "active_adapter": {
            "is_up": False,
        },
    }

    assert rule.matches(evidence) is False


def test_rule_creates_network_adapter_decision():
    rule = NetworkAdapterDecisionRule()

    evidence = {}

    decision = rule.create_decision(evidence)

    assert decision.decision_type == "CHECK_NETWORK_ADAPTER"
    assert decision.category == "NETWORK"
    assert decision.priority == "HIGH"


def test_rule_decision_explains_unknown_adapter_state():
    rule = NetworkAdapterDecisionRule()

    evidence = {
        "active_adapter": {},
    }

    decision = rule.create_decision(evidence)

    assert "adapter" in decision.reason.lower()
    assert "unknown" in decision.reason.lower()