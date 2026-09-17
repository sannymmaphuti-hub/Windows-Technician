from engine.finding_engine import FindingEngine
from engine.signal import Signal

from engine.network_adapter_finding_rule import (
    NetworkAdapterFindingRule,
)
from engine.local_network_unreachable_rule import (
    LocalNetworkUnreachableRule,
)
from engine.dns_resolution_failure_rule import (
    DNSResolutionFailureRule,
)
from engine.internet_connectivity_failure_rule import (
    InternetConnectivityFailureRule,
)


def create_network_engine():
    engine = FindingEngine()

    engine.register_rule(NetworkAdapterFindingRule())
    engine.register_rule(LocalNetworkUnreachableRule())
    engine.register_rule(DNSResolutionFailureRule())
    engine.register_rule(InternetConnectivityFailureRule())

    return engine


def test_engine_detects_disconnected_network_adapter():
    engine = create_network_engine()

    signal = Signal(
        "NETWORK_ADAPTER_DISCONNECTED",
        "network",
        "network_adapter",
        "is_up",
        False,
    )

    findings = engine.detect(signal)

    assert len(findings) == 1
    assert findings[0].finding_type == "NETWORK_ADAPTER_DISCONNECTED"


def test_engine_detects_unreachable_gateway():
    engine = create_network_engine()

    signal = Signal(
        "DEFAULT_GATEWAY_UNREACHABLE",
        "network",
        "network_gateway",
        "reachable",
        False,
    )

    findings = engine.detect(signal)

    assert len(findings) == 1
    assert findings[0].finding_type == "LOCAL_NETWORK_UNREACHABLE"


def test_engine_detects_dns_failure():
    engine = create_network_engine()

    signal = Signal(
        "DNS_RESOLUTION_FAILED",
        "network",
        "network_dns",
        "working",
        False,
    )

    findings = engine.detect(signal)

    assert len(findings) == 1
    assert findings[0].finding_type == "DNS_RESOLUTION_FAILURE"


def test_engine_detects_internet_failure():
    engine = create_network_engine()

    signal = Signal(
        "INTERNET_UNREACHABLE",
        "network",
        "network_internet",
        "reachable",
        False,
    )

    findings = engine.detect(signal)

    assert len(findings) == 1
    assert findings[0].finding_type == "INTERNET_CONNECTIVITY_FAILURE"


def test_engine_preserves_network_signal_as_supporting_evidence():
    engine = create_network_engine()

    signal = Signal(
        "DNS_RESOLUTION_FAILED",
        "network",
        "network_dns",
        "working",
        False,
    )

    findings = engine.detect(signal)

    assert findings[0].supporting_signals == [signal]


def test_engine_does_not_create_network_findings_for_healthy_signals():
    engine = create_network_engine()

    healthy_signals = [
        Signal(
            "NETWORK_ADAPTER_CONNECTED",
            "network",
            "network_adapter",
            "is_up",
            True,
        ),
        Signal(
            "DEFAULT_GATEWAY_REACHABLE",
            "network",
            "network_gateway",
            "reachable",
            True,
        ),
        Signal(
            "DNS_RESOLUTION_WORKING",
            "network",
            "network_dns",
            "working",
            True,
        ),
        Signal(
            "INTERNET_REACHABLE",
            "network",
            "network_internet",
            "reachable",
            True,
        ),
    ]

    for signal in healthy_signals:
        assert engine.detect(signal) == []


def test_engine_preserves_existing_rule_registration_behavior():
    engine = FindingEngine()

    class ExistingRule:
        pass

    # The existing engine contract requires FindingRule instances.
    # This test simply verifies network integration does not bypass
    # that contract by checking invalid registration still fails.
    try:
        engine.register_rule(ExistingRule())
    except ValueError:
        pass
    else:
        raise AssertionError(
            "FindingEngine should reject invalid rules."
        )