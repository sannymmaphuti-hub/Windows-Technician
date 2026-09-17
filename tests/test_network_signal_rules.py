import pytest

from engine.observation import Observation
from engine.network_adapter_disconnected_rule import (
    NetworkAdapterDisconnectedRule,
)
from engine.default_gateway_unreachable_rule import (
    DefaultGatewayUnreachableRule,
)
from engine.dns_resolution_failed_rule import (
    DNSResolutionFailedRule,
)
from engine.internet_unreachable_rule import (
    InternetUnreachableRule,
)


def test_network_adapter_disconnected_rule_matches():
    observation = Observation(
        source="network",
        subject="network_adapter",
        attribute="is_up",
        value=False,
    )

    rule = NetworkAdapterDisconnectedRule()

    assert rule.matches(observation) is True


def test_network_adapter_disconnected_rule_creates_signal():
    observation = Observation(
        source="network",
        subject="network_adapter",
        attribute="is_up",
        value=False,
    )

    signal = NetworkAdapterDisconnectedRule().create_signal(observation)

    assert signal.signal_type == "NETWORK_ADAPTER_DISCONNECTED"
    assert signal.source == "network"
    assert signal.subject == "network_adapter"
    assert signal.attribute == "is_up"
    assert signal.value is False


def test_gateway_unreachable_rule_matches():
    observation = Observation(
        source="network",
        subject="network_gateway",
        attribute="reachable",
        value=False,
    )

    assert DefaultGatewayUnreachableRule().matches(observation) is True


def test_gateway_unreachable_rule_creates_signal():
    observation = Observation(
        source="network",
        subject="network_gateway",
        attribute="reachable",
        value=False,
    )

    signal = DefaultGatewayUnreachableRule().create_signal(observation)

    assert signal.signal_type == "DEFAULT_GATEWAY_UNREACHABLE"
    assert signal.source == "network"
    assert signal.subject == "network_gateway"
    assert signal.attribute == "reachable"
    assert signal.value is False


def test_dns_resolution_failed_rule_matches():
    observation = Observation(
        source="network",
        subject="network_dns",
        attribute="working",
        value=False,
    )

    assert DNSResolutionFailedRule().matches(observation) is True


def test_dns_resolution_failed_rule_creates_signal():
    observation = Observation(
        source="network",
        subject="network_dns",
        attribute="working",
        value=False,
    )

    signal = DNSResolutionFailedRule().create_signal(observation)

    assert signal.signal_type == "DNS_RESOLUTION_FAILED"
    assert signal.source == "network"
    assert signal.subject == "network_dns"
    assert signal.attribute == "working"
    assert signal.value is False


def test_internet_unreachable_rule_matches():
    observation = Observation(
        source="network",
        subject="network_internet",
        attribute="reachable",
        value=False,
    )

    assert InternetUnreachableRule().matches(observation) is True


def test_internet_unreachable_rule_creates_signal():
    observation = Observation(
        source="network",
        subject="network_internet",
        attribute="reachable",
        value=False,
    )

    signal = InternetUnreachableRule().create_signal(observation)

    assert signal.signal_type == "INTERNET_UNREACHABLE"
    assert signal.source == "network"
    assert signal.subject == "network_internet"
    assert signal.attribute == "reachable"
    assert signal.value is False


@pytest.mark.parametrize(
    "rule, observation",
    [
        (
            NetworkAdapterDisconnectedRule(),
            Observation(
                "network",
                "network_adapter",
                "is_up",
                True,
            ),
        ),
        (
            DefaultGatewayUnreachableRule(),
            Observation(
                "network",
                "network_gateway",
                "reachable",
                True,
            ),
        ),
        (
            DNSResolutionFailedRule(),
            Observation(
                "network",
                "network_dns",
                "working",
                True,
            ),
        ),
        (
            InternetUnreachableRule(),
            Observation(
                "network",
                "network_internet",
                "reachable",
                True,
            ),
        ),
    ],
)
def test_network_signal_rules_do_not_match_healthy_values(
    rule,
    observation,
):
    assert rule.matches(observation) is False