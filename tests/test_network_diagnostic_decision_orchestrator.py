from engine.diagnostic_decision_orchestrator import (
    DiagnosticDecisionOrchestrator,
)
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


def create_network_orchestrator():
    orchestrator = DiagnosticDecisionOrchestrator()

    orchestrator.register_rule(NetworkAdapterDecisionRule())
    orchestrator.register_rule(GatewayReachabilityDecisionRule())
    orchestrator.register_rule(DNSResolutionDecisionRule())
    orchestrator.register_rule(InternetConnectivityDecisionRule())

    return orchestrator


def test_network_orchestrator_can_be_created():
    orchestrator = create_network_orchestrator()

    assert orchestrator is not None


def test_adapter_unknown_requests_adapter_check():
    orchestrator = create_network_orchestrator()

    decisions = orchestrator.decide({})

    assert len(decisions) == 1
    assert decisions[0].decision_type == "CHECK_NETWORK_ADAPTER"


def test_gateway_unknown_requests_gateway_check():
    orchestrator = create_network_orchestrator()

    evidence = {
        "active_adapter": {
            "is_up": True,
        },
    }

    decisions = orchestrator.decide(evidence)

    assert len(decisions) == 1
    assert decisions[0].decision_type == "CHECK_GATEWAY_REACHABILITY"


def test_dns_unknown_requests_dns_check():
    orchestrator = create_network_orchestrator()

    evidence = {
        "active_adapter": {
            "is_up": True,
        },
        "gateway_reachable": True,
    }

    decisions = orchestrator.decide(evidence)

    assert len(decisions) == 1
    assert decisions[0].decision_type == "CHECK_DNS_RESOLUTION"


def test_internet_unknown_requests_internet_check():
    orchestrator = create_network_orchestrator()

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


def test_adapter_failure_stops_diagnostic_progression():
    orchestrator = create_network_orchestrator()

    evidence = {
        "active_adapter": {
            "is_up": False,
        },
    }

    decisions = orchestrator.decide(evidence)

    assert decisions == []


def test_gateway_failure_stops_diagnostic_progression():
    orchestrator = create_network_orchestrator()

    evidence = {
        "active_adapter": {
            "is_up": True,
        },
        "gateway_reachable": False,
    }

    decisions = orchestrator.decide(evidence)

    assert decisions == []


def test_dns_failure_stops_diagnostic_progression():
    orchestrator = create_network_orchestrator()

    evidence = {
        "active_adapter": {
            "is_up": True,
        },
        "gateway_reachable": True,
        "dns_working": False,
    }

    decisions = orchestrator.decide(evidence)

    assert decisions == []


def test_internet_failure_is_terminal():
    orchestrator = create_network_orchestrator()

    evidence = {
        "active_adapter": {
            "is_up": True,
        },
        "gateway_reachable": True,
        "dns_working": True,
        "internet_reachable": False,
    }

    decisions = orchestrator.decide(evidence)

    assert decisions == []


def test_complete_healthy_network_evidence_requires_no_more_checks():
    orchestrator = create_network_orchestrator()

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


def test_orchestrator_returns_only_one_next_action():
    orchestrator = create_network_orchestrator()

    evidence = {
        "active_adapter": {
            "is_up": True,
        },
    }

    decisions = orchestrator.decide(evidence)

    assert len(decisions) == 1