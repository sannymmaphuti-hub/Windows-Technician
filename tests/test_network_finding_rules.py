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


def test_network_adapter_finding_rule_matches():
    signal = Signal(
        "NETWORK_ADAPTER_DISCONNECTED",
        "network",
        "network_adapter",
        "is_up",
        False,
    )

    rule = NetworkAdapterFindingRule()

    assert rule.matches(signal) is True


def test_network_adapter_finding_rule_creates_finding():
    signal = Signal(
        "NETWORK_ADAPTER_DISCONNECTED",
        "network",
        "network_adapter",
        "is_up",
        False,
    )

    finding = NetworkAdapterFindingRule().create_finding(signal)

    assert finding.finding_type == "NETWORK_ADAPTER_DISCONNECTED"
    assert finding.category == "NETWORK"
    assert finding.severity == "HIGH"
    assert signal in finding.supporting_signals


def test_local_network_unreachable_rule_matches():
    signal = Signal(
        "DEFAULT_GATEWAY_UNREACHABLE",
        "network",
        "network_gateway",
        "reachable",
        False,
    )

    assert LocalNetworkUnreachableRule().matches(signal) is True


def test_local_network_unreachable_rule_creates_finding():
    signal = Signal(
        "DEFAULT_GATEWAY_UNREACHABLE",
        "network",
        "network_gateway",
        "reachable",
        False,
    )

    finding = LocalNetworkUnreachableRule().create_finding(signal)

    assert finding.finding_type == "LOCAL_NETWORK_UNREACHABLE"
    assert finding.category == "NETWORK"
    assert finding.severity == "HIGH"
    assert signal in finding.supporting_signals


def test_dns_resolution_failure_rule_matches():
    signal = Signal(
        "DNS_RESOLUTION_FAILED",
        "network",
        "network_dns",
        "working",
        False,
    )

    assert DNSResolutionFailureRule().matches(signal) is True


def test_dns_resolution_failure_rule_creates_finding():
    signal = Signal(
        "DNS_RESOLUTION_FAILED",
        "network",
        "network_dns",
        "working",
        False,
    )

    finding = DNSResolutionFailureRule().create_finding(signal)

    assert finding.finding_type == "DNS_RESOLUTION_FAILURE"
    assert finding.category == "NETWORK"
    assert finding.severity == "MEDIUM"
    assert signal in finding.supporting_signals


def test_internet_connectivity_failure_rule_matches():
    signal = Signal(
        "INTERNET_UNREACHABLE",
        "network",
        "network_internet",
        "reachable",
        False,
    )

    assert InternetConnectivityFailureRule().matches(signal) is True


def test_internet_connectivity_failure_rule_creates_finding():
    signal = Signal(
        "INTERNET_UNREACHABLE",
        "network",
        "network_internet",
        "reachable",
        False,
    )

    finding = InternetConnectivityFailureRule().create_finding(signal)

    assert finding.finding_type == "INTERNET_CONNECTIVITY_FAILURE"
    assert finding.category == "NETWORK"
    assert finding.severity == "HIGH"
    assert signal in finding.supporting_signals


def test_network_finding_rules_reject_wrong_signal_types():
    signals = [
        Signal(
            "HIGH_MEMORY_USAGE",
            "memory",
            "system_memory",
            "usage_percent",
            88,
        ),
        Signal(
            "HIGH_CPU_USAGE",
            "cpu",
            "system_cpu",
            "usage_percent",
            95,
        ),
    ]

    rules = [
        NetworkAdapterFindingRule(),
        LocalNetworkUnreachableRule(),
        DNSResolutionFailureRule(),
        InternetConnectivityFailureRule(),
    ]

    for rule in rules:
        for signal in signals:
            assert rule.matches(signal) is False