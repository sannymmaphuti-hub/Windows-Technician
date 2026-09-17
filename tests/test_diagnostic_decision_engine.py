from engine.diagnostic_decision_engine import DiagnosticDecisionEngine
from engine.diagnostic_decision import DiagnosticDecision


def test_diagnostic_decision_engine_can_be_created():
    engine = DiagnosticDecisionEngine()

    assert engine is not None


def test_engine_decides_to_check_network_adapter_for_empty_evidence():
    engine = DiagnosticDecisionEngine()

    decisions = engine.decide({})

    assert len(decisions) == 1
    assert decisions[0].decision_type == "CHECK_NETWORK_ADAPTER"


def test_engine_returns_no_decision_when_network_evidence_is_complete():
    engine = DiagnosticDecisionEngine()

    evidence = {
        "active_adapter": {
            "is_up": True,
        },
        "gateway": "192.168.1.1",
        "gateway_reachable": True,
        "dns_working": True,
        "internet_reachable": True,
    }

    decisions = engine.decide(evidence)

    assert decisions == []


def test_engine_decides_to_check_gateway_when_gateway_reachability_is_unknown():
    engine = DiagnosticDecisionEngine()

    evidence = {
        "active_adapter": {
            "is_up": True,
        },
        "gateway": "192.168.1.1",
    }

    decisions = engine.decide(evidence)

    assert len(decisions) == 1
    assert isinstance(decisions[0], DiagnosticDecision)
    assert decisions[0].decision_type == "CHECK_GATEWAY_REACHABILITY"


def test_gateway_decision_explains_missing_information():
    engine = DiagnosticDecisionEngine()

    evidence = {
        "active_adapter": {
            "is_up": True,
        },
        "gateway": "192.168.1.1",
    }

    decisions = engine.decide(evidence)

    assert "gateway" in decisions[0].reason.lower()
    assert decisions[0].category == "NETWORK"


def test_engine_does_not_decide_to_check_gateway_when_gateway_is_unreachable():
    engine = DiagnosticDecisionEngine()

    evidence = {
        "active_adapter": {
            "is_up": True,
        },
        "gateway": "192.168.1.1",
        "gateway_reachable": False,
    }

    decisions = engine.decide(evidence)

    assert all(
        decision.decision_type != "CHECK_GATEWAY_REACHABILITY"
        for decision in decisions
    )

def test_engine_decides_to_check_network_adapter_when_adapter_state_is_unknown():
    engine = DiagnosticDecisionEngine()

    evidence = {}

    decisions = engine.decide(evidence)

    assert len(decisions) == 1
    assert decisions[0].decision_type == "CHECK_NETWORK_ADAPTER"


def test_engine_does_not_check_adapter_when_adapter_state_is_known():
    engine = DiagnosticDecisionEngine()

    evidence = {
        "active_adapter": {
            "is_up": True,
        },
    }

    decisions = engine.decide(evidence)

    assert all(
        decision.decision_type != "CHECK_NETWORK_ADAPTER"
        for decision in decisions
    )

def test_engine_decides_to_check_dns_when_dns_status_is_unknown():
    engine = DiagnosticDecisionEngine()

    evidence = {
        "active_adapter": {
            "is_up": True,
        },
        "gateway": "192.168.1.1",
        "gateway_reachable": True,
    }

    decisions = engine.decide(evidence)

    assert len(decisions) == 1
    assert decisions[0].decision_type == "CHECK_DNS_RESOLUTION"


def test_engine_does_not_check_dns_when_dns_status_is_known():
    engine = DiagnosticDecisionEngine()

    evidence = {
        "active_adapter": {
            "is_up": True,
        },
        "gateway": "192.168.1.1",
        "gateway_reachable": True,
        "dns_working": True,
    }

    decisions = engine.decide(evidence)

    assert all(
        decision.decision_type != "CHECK_DNS_RESOLUTION"
        for decision in decisions
    )


def test_engine_decides_to_check_internet_when_internet_status_is_unknown():
    engine = DiagnosticDecisionEngine()

    evidence = {
        "active_adapter": {
            "is_up": True,
        },
        "gateway": "192.168.1.1",
        "gateway_reachable": True,
        "dns_working": True,
    }

    decisions = engine.decide(evidence)

    assert len(decisions) == 1
    assert decisions[0].decision_type == "CHECK_INTERNET_CONNECTIVITY"


def test_engine_does_not_check_internet_when_internet_status_is_known():
    engine = DiagnosticDecisionEngine()

    evidence = {
        "active_adapter": {
            "is_up": True,
        },
        "gateway": "192.168.1.1",
        "gateway_reachable": True,
        "dns_working": True,
        "internet_reachable": True,
    }

    decisions = engine.decide(evidence)

    assert decisions == []

def test_engine_stops_when_dns_resolution_is_known_to_be_failing():
    engine = DiagnosticDecisionEngine()

    evidence = {
        "active_adapter": {
            "is_up": True,
        },
        "gateway": "192.168.1.1",
        "gateway_reachable": True,
        "dns_working": False,
    }

    decisions = engine.decide(evidence)

    assert decisions == []


def test_engine_does_not_check_internet_when_dns_is_failing():
    engine = DiagnosticDecisionEngine()

    evidence = {
        "active_adapter": {
            "is_up": True,
        },
        "gateway": "192.168.1.1",
        "gateway_reachable": True,
        "dns_working": False,
    }

    decisions = engine.decide(evidence)

    assert all(
        decision.decision_type != "CHECK_INTERNET_CONNECTIVITY"
        for decision in decisions
    )


def test_engine_stops_when_internet_is_known_to_be_unreachable():
    engine = DiagnosticDecisionEngine()

    evidence = {
        "active_adapter": {
            "is_up": True,
        },
        "gateway": "192.168.1.1",
        "gateway_reachable": True,
        "dns_working": True,
        "internet_reachable": False,
    }

    decisions = engine.decide(evidence)

    assert decisions == []

def test_engine_prioritizes_gateway_before_dns_and_internet():
    engine = DiagnosticDecisionEngine()

    evidence = {
        "active_adapter": {
            "is_up": True,
        },
    }

    decisions = engine.decide(evidence)

    assert len(decisions) == 1
    assert decisions[0].decision_type == "CHECK_GATEWAY_REACHABILITY"


def test_engine_prioritizes_dns_before_internet():
    engine = DiagnosticDecisionEngine()

    evidence = {
        "active_adapter": {
            "is_up": True,
        },
        "gateway": "192.168.1.1",
        "gateway_reachable": True,
    }

    decisions = engine.decide(evidence)

    assert len(decisions) == 1
    assert decisions[0].decision_type == "CHECK_DNS_RESOLUTION"


def test_engine_prioritizes_internet_after_dns_is_confirmed():
    engine = DiagnosticDecisionEngine()

    evidence = {
        "active_adapter": {
            "is_up": True,
        },
        "gateway": "192.168.1.1",
        "gateway_reachable": True,
        "dns_working": True,
    }

    decisions = engine.decide(evidence)

    assert len(decisions) == 1
    assert decisions[0].decision_type == "CHECK_INTERNET_CONNECTIVITY"

def test_engine_rejects_non_dictionary_evidence():
    engine = DiagnosticDecisionEngine()

    invalid_evidence = None

    try:
        engine.decide(invalid_evidence)
    except ValueError:
        return

    assert False, "Expected ValueError for non-dictionary evidence."


def test_engine_rejects_invalid_active_adapter_structure():
    engine = DiagnosticDecisionEngine()

    evidence = {
        "active_adapter": "Wi-Fi",
    }

    try:
        engine.decide(evidence)
    except ValueError:
        return

    assert False, "Expected ValueError for invalid active_adapter structure."


def test_engine_treats_empty_active_adapter_as_unknown_state():
    engine = DiagnosticDecisionEngine()

    evidence = {
        "active_adapter": {},
    }

    decisions = engine.decide(evidence)

    assert len(decisions) == 1
    assert decisions[0].decision_type == "CHECK_NETWORK_ADAPTER"