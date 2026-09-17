from engine.correlation_engine import CorrelationEngine
from engine.finding import Finding
from engine.local_network_failure_correlation_rule import (
    LocalNetworkFailureCorrelationRule,
)
from engine.network_adapter_correlation_rule import (
    NetworkAdapterCorrelationRule,
)


def create_finding(
    finding_type,
    severity="HIGH",
    description="Network finding.",
):
    return Finding(
        finding_type=finding_type,
        category="NETWORK",
        severity=severity,
        description=description,
    )


def create_network_correlation_engine():
    engine = CorrelationEngine()

    engine.register_rule(NetworkAdapterCorrelationRule())
    engine.register_rule(LocalNetworkFailureCorrelationRule())

    return engine


def test_correlation_engine_detects_network_adapter_failure():
    engine = create_network_correlation_engine()

    findings = [
        create_finding("NETWORK_ADAPTER_DISCONNECTED"),
    ]

    correlations = engine.detect(findings)

    assert len(correlations) == 1
    assert correlations[0].correlation_type == "NETWORK_ADAPTER_FAILURE"


def test_correlation_engine_detects_local_network_failure():
    engine = create_network_correlation_engine()

    findings = [
        create_finding("LOCAL_NETWORK_UNREACHABLE"),
        create_finding("INTERNET_CONNECTIVITY_FAILURE"),
    ]

    correlations = engine.detect(findings)

    assert len(correlations) == 1
    assert correlations[0].correlation_type == "LOCAL_NETWORK_FAILURE"


def test_correlation_engine_returns_no_network_correlation_for_healthy_findings():
    engine = create_network_correlation_engine()

    findings = [
        create_finding(
            "DNS_RESOLUTION_FAILURE",
            severity="MEDIUM",
            description="DNS resolution is failing.",
        ),
    ]

    correlations = engine.detect(findings)

    assert correlations == []


def test_correlation_engine_preserves_network_finding_objects():
    engine = create_network_correlation_engine()

    adapter = create_finding("NETWORK_ADAPTER_DISCONNECTED")

    correlations = engine.detect([adapter])

    assert correlations[0].findings[0] is adapter


def test_correlation_engine_can_detect_multiple_network_correlations():
    engine = create_network_correlation_engine()

    adapter = create_finding("NETWORK_ADAPTER_DISCONNECTED")
    gateway = create_finding("LOCAL_NETWORK_UNREACHABLE")
    internet = create_finding("INTERNET_CONNECTIVITY_FAILURE")

    correlations = engine.detect(
        [adapter, gateway, internet]
    )

    correlation_types = {
        correlation.correlation_type
        for correlation in correlations
    }

    assert correlation_types == {
        "NETWORK_ADAPTER_FAILURE",
        "LOCAL_NETWORK_FAILURE",
    }