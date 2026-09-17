from engine.internet_connectivity_decision_rule import (
    InternetConnectivityDecisionRule,
)


def test_rule_can_be_created():
    rule = InternetConnectivityDecisionRule()

    assert rule is not None


def test_rule_matches_when_internet_status_is_missing():
    rule = InternetConnectivityDecisionRule()

    evidence = {
        "active_adapter": {
            "is_up": True,
        },
        "gateway_reachable": True,
        "dns_working": True,
    }

    assert rule.matches(evidence) is True


def test_rule_does_not_match_when_internet_is_reachable():
    rule = InternetConnectivityDecisionRule()

    evidence = {
        "active_adapter": {
            "is_up": True,
        },
        "gateway_reachable": True,
        "dns_working": True,
        "internet_reachable": True,
    }

    assert rule.matches(evidence) is False


def test_rule_does_not_match_when_internet_is_unreachable():
    rule = InternetConnectivityDecisionRule()

    evidence = {
        "active_adapter": {
            "is_up": True,
        },
        "gateway_reachable": True,
        "dns_working": True,
        "internet_reachable": False,
    }

    assert rule.matches(evidence) is False


def test_rule_does_not_match_when_dns_is_unknown():
    rule = InternetConnectivityDecisionRule()

    evidence = {
        "active_adapter": {
            "is_up": True,
        },
        "gateway_reachable": True,
    }

    assert rule.matches(evidence) is False


def test_rule_does_not_match_when_dns_is_failing():
    rule = InternetConnectivityDecisionRule()

    evidence = {
        "active_adapter": {
            "is_up": True,
        },
        "gateway_reachable": True,
        "dns_working": False,
    }

    assert rule.matches(evidence) is False


def test_rule_does_not_match_when_gateway_is_unreachable():
    rule = InternetConnectivityDecisionRule()

    evidence = {
        "active_adapter": {
            "is_up": True,
        },
        "gateway_reachable": False,
        "dns_working": True,
    }

    assert rule.matches(evidence) is False


def test_rule_does_not_match_when_adapter_is_not_up():
    rule = InternetConnectivityDecisionRule()

    evidence = {
        "active_adapter": {
            "is_up": False,
        },
        "gateway_reachable": True,
        "dns_working": True,
    }

    assert rule.matches(evidence) is False


def test_rule_creates_internet_connectivity_decision():
    rule = InternetConnectivityDecisionRule()

    evidence = {
        "active_adapter": {
            "is_up": True,
        },
        "gateway_reachable": True,
        "dns_working": True,
    }

    decision = rule.create_decision(evidence)

    assert decision.decision_type == "CHECK_INTERNET_CONNECTIVITY"
    assert decision.category == "NETWORK"
    assert decision.priority == "HIGH"


def test_rule_decision_explains_unknown_internet_status():
    rule = InternetConnectivityDecisionRule()

    evidence = {
        "active_adapter": {
            "is_up": True,
        },
        "gateway_reachable": True,
        "dns_working": True,
    }

    decision = rule.create_decision(evidence)

    assert "internet" in decision.reason.lower()
    assert "unknown" in decision.reason.lower()