from engine.dns_resolution_decision_rule import DNSResolutionDecisionRule


def test_rule_can_be_created():
    rule = DNSResolutionDecisionRule()

    assert rule is not None


def test_rule_matches_when_dns_status_is_missing():
    rule = DNSResolutionDecisionRule()

    evidence = {
        "active_adapter": {
            "is_up": True,
        },
        "gateway_reachable": True,
    }

    assert rule.matches(evidence) is True


def test_rule_does_not_match_when_dns_is_working():
    rule = DNSResolutionDecisionRule()

    evidence = {
        "active_adapter": {
            "is_up": True,
        },
        "gateway_reachable": True,
        "dns_working": True,
    }

    assert rule.matches(evidence) is False


def test_rule_does_not_match_when_dns_is_failing():
    rule = DNSResolutionDecisionRule()

    evidence = {
        "active_adapter": {
            "is_up": True,
        },
        "gateway_reachable": True,
        "dns_working": False,
    }

    assert rule.matches(evidence) is False


def test_rule_does_not_match_when_gateway_is_unreachable():
    rule = DNSResolutionDecisionRule()

    evidence = {
        "active_adapter": {
            "is_up": True,
        },
        "gateway_reachable": False,
    }

    assert rule.matches(evidence) is False


def test_rule_does_not_match_when_adapter_is_not_up():
    rule = DNSResolutionDecisionRule()

    evidence = {
        "active_adapter": {
            "is_up": False,
        },
        "gateway_reachable": True,
    }

    assert rule.matches(evidence) is False


def test_rule_creates_dns_resolution_decision():
    rule = DNSResolutionDecisionRule()

    evidence = {
        "active_adapter": {
            "is_up": True,
        },
        "gateway_reachable": True,
    }

    decision = rule.create_decision(evidence)

    assert decision.decision_type == "CHECK_DNS_RESOLUTION"
    assert decision.category == "NETWORK"
    assert decision.priority == "HIGH"


def test_rule_decision_explains_unknown_dns_status():
    rule = DNSResolutionDecisionRule()

    evidence = {
        "active_adapter": {
            "is_up": True,
        },
        "gateway_reachable": True,
    }

    decision = rule.create_decision(evidence)

    assert "dns" in decision.reason.lower()
    assert "unknown" in decision.reason.lower()