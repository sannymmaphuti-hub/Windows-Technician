from engine.finding import Finding
from engine.network_adapter_correlation_rule import NetworkAdapterCorrelationRule
from engine.local_network_failure_correlation_rule import (
    LocalNetworkFailureCorrelationRule,
)


def create_finding(
    finding_type,
    category="NETWORK",
    severity="HIGH",
    description="Network finding.",
):
    return Finding(
        finding_type=finding_type,
        category=category,
        severity=severity,
        description=description,
    )


def create_adapter_finding():
    return create_finding(
        finding_type="NETWORK_ADAPTER_DISCONNECTED",
        description="The network adapter is disconnected.",
    )


def create_gateway_finding():
    return create_finding(
        finding_type="LOCAL_NETWORK_UNREACHABLE",
        description="The local network gateway is unreachable.",
    )


def create_internet_finding():
    return create_finding(
        finding_type="INTERNET_CONNECTIVITY_FAILURE",
        description="Internet connectivity is unavailable.",
    )


def create_dns_finding():
    return create_finding(
        finding_type="DNS_RESOLUTION_FAILURE",
        severity="MEDIUM",
        description="DNS resolution is failing.",
    )


def test_network_adapter_correlation_rule_matches_adapter_failure():
    rule = NetworkAdapterCorrelationRule()

    findings = [create_adapter_finding()]

    assert rule.matches(findings) is True


def test_network_adapter_correlation_rule_ignores_unrelated_findings():
    rule = NetworkAdapterCorrelationRule()

    findings = [create_dns_finding()]

    assert rule.matches(findings) is False


def test_network_adapter_correlation_rule_creates_correlation():
    rule = NetworkAdapterCorrelationRule()

    adapter = create_adapter_finding()
    findings = [adapter]

    correlation = rule.create_correlation(findings)

    assert correlation.correlation_type == "NETWORK_ADAPTER_FAILURE"
    assert correlation.findings == findings
    assert correlation.strength == "HIGH"


def test_network_adapter_correlation_preserves_finding_object():
    rule = NetworkAdapterCorrelationRule()

    adapter = create_adapter_finding()

    correlation = rule.create_correlation([adapter])

    assert correlation.findings[0] is adapter


def test_local_network_failure_rule_matches_gateway_and_internet_failure():
    rule = LocalNetworkFailureCorrelationRule()

    findings = [
        create_gateway_finding(),
        create_internet_finding(),
    ]

    assert rule.matches(findings) is True


def test_local_network_failure_rule_requires_gateway_failure():
    rule = LocalNetworkFailureCorrelationRule()

    findings = [create_internet_finding()]

    assert rule.matches(findings) is False


def test_local_network_failure_rule_ignores_dns_failure_only():
    rule = LocalNetworkFailureCorrelationRule()

    findings = [create_dns_finding()]

    assert rule.matches(findings) is False


def test_local_network_failure_rule_creates_correlation():
    rule = LocalNetworkFailureCorrelationRule()

    gateway = create_gateway_finding()
    internet = create_internet_finding()
    findings = [gateway, internet]

    correlation = rule.create_correlation(findings)

    assert correlation.correlation_type == "LOCAL_NETWORK_FAILURE"
    assert correlation.findings == findings
    assert correlation.strength == "HIGH"


def test_local_network_failure_preserves_finding_objects():
    rule = LocalNetworkFailureCorrelationRule()

    gateway = create_gateway_finding()
    internet = create_internet_finding()

    correlation = rule.create_correlation([gateway, internet])

    assert correlation.findings[0] is gateway
    assert correlation.findings[1] is internet


def test_network_correlation_explanations_preserve_uncertainty():
    rules_and_findings = [
        (NetworkAdapterCorrelationRule(), [create_adapter_finding()]),
        (
            LocalNetworkFailureCorrelationRule(),
            [create_gateway_finding(), create_internet_finding()],
        ),
    ]

    for rule, findings in rules_and_findings:
        correlation = rule.create_correlation(findings)

        assert correlation.explanation
        assert "caused" not in correlation.explanation.lower()