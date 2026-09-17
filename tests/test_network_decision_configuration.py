from engine.network_adapter_decision_rule import (
    NetworkAdapterDecisionRule,
)
from engine.gateway_reachability_decision_rule import (
    GatewayReachabilityDecisionRule,
)
from engine.dns_resolution_decision_rule import (
    DNSResolutionDecisionRule,
)
from engine.internet_connectivity_decision_rule import (
    InternetConnectivityDecisionRule,
)
from engine.network_decision_configuration import (
    create_network_decision_orchestrator,
)


def test_network_decision_orchestrator_can_be_created():
    orchestrator = create_network_decision_orchestrator()

    assert orchestrator is not None


def test_network_decision_orchestrator_contains_four_rules():
    orchestrator = create_network_decision_orchestrator()

    assert len(orchestrator.rules) == 4


def test_network_rules_are_registered_in_dependency_order():
    orchestrator = create_network_decision_orchestrator()

    assert isinstance(
        orchestrator.rules[0],
        NetworkAdapterDecisionRule,
    )
    assert isinstance(
        orchestrator.rules[1],
        GatewayReachabilityDecisionRule,
    )
    assert isinstance(
        orchestrator.rules[2],
        DNSResolutionDecisionRule,
    )
    assert isinstance(
        orchestrator.rules[3],
        InternetConnectivityDecisionRule,
    )


def test_default_configuration_checks_adapter_first():
    orchestrator = create_network_decision_orchestrator()

    decisions = orchestrator.decide({})

    assert len(decisions) == 1
    assert decisions[0].decision_type == "CHECK_NETWORK_ADAPTER"


def test_default_configuration_checks_gateway_after_adapter():
    orchestrator = create_network_decision_orchestrator()

    evidence = {
        "active_adapter": {
            "is_up": True,
        },
    }

    decisions = orchestrator.decide(evidence)

    assert len(decisions) == 1
    assert decisions[0].decision_type == "CHECK_GATEWAY_REACHABILITY"


def test_default_configuration_checks_dns_after_gateway():
    orchestrator = create_network_decision_orchestrator()

    evidence = {
        "active_adapter": {
            "is_up": True,
        },
        "gateway_reachable": True,
    }

    decisions = orchestrator.decide(evidence)

    assert len(decisions) == 1
    assert decisions[0].decision_type == "CHECK_DNS_RESOLUTION"


def test_default_configuration_checks_internet_last():
    orchestrator = create_network_decision_orchestrator()

    evidence = {
        "active_adapter": {
            "is_up": True,
        },
        "gateway_reachable": True,
        "dns_working": True,
    }

    decisions = orchestrator.decide(evidence)

    assert len(decisions) == 1
    assert decisions[0].decision_type == "CHECK_INTERNET_CONNECTIVITY"


def test_default_configuration_stops_when_network_is_healthy():
    orchestrator = create_network_decision_orchestrator()

    evidence = {
        "active_adapter": {
            "is_up": True,
        },
        "gateway_reachable": True,
        "dns_working": True,
        "internet_reachable": True,
    }

    decisions = orchestrator.decide(evidence)

    assert decisions == []