from engine.correlation_engine import CorrelationEngine
from engine.finding_engine import FindingEngine
from engine.local_network_failure_correlation_rule import (
    LocalNetworkFailureCorrelationRule,
)
from engine.network_adapter_correlation_rule import (
    NetworkAdapterCorrelationRule,
)
from engine.network_adapter_finding_rule import NetworkAdapterFindingRule
from engine.local_network_unreachable_rule import LocalNetworkUnreachableRule
from engine.dns_resolution_failure_rule import DNSResolutionFailureRule
from engine.internet_connectivity_failure_rule import (
    InternetConnectivityFailureRule,
)
from engine.network_observation_builder import NetworkObservationBuilder
from engine.observation_to_signal import ObservationToSignal


def create_finding_engine():
    engine = FindingEngine()

    engine.register_rule(NetworkAdapterFindingRule())
    engine.register_rule(LocalNetworkUnreachableRule())
    engine.register_rule(DNSResolutionFailureRule())
    engine.register_rule(InternetConnectivityFailureRule())

    return engine


def create_correlation_engine():
    engine = CorrelationEngine()

    engine.register_rule(NetworkAdapterCorrelationRule())
    engine.register_rule(LocalNetworkFailureCorrelationRule())

    return engine


def diagnose_network_pipeline(evidence):
    observation_builder = NetworkObservationBuilder()
    signal_detector = ObservationToSignal()
    finding_engine = create_finding_engine()
    correlation_engine = create_correlation_engine()

    observations = observation_builder.build(evidence)

    signals = []
    findings = []

    for observation in observations:
        signal = signal_detector.detect(observation)

        if signal is None:
            continue

        signals.append(signal)
        findings.extend(finding_engine.detect(signal))

    correlations = correlation_engine.detect(findings)

    return observations, signals, findings, correlations


def create_disconnected_adapter_evidence():
    return {
        "active_adapter": {
            "is_up": False,
            "addresses": [],
        },
        "gateway": None,
        "gateway_reachable": False,
        "internet_reachable": False,
        "dns_working": True,
    }


def create_local_network_failure_evidence():
    return {
        "active_adapter": {
            "is_up": True,
            "addresses": [
                {
                    "type": "IPv4",
                    "address": "192.168.1.20",
                    "classification": "PRIVATE",
                }
            ],
        },
        "gateway": "192.168.1.1",
        "gateway_reachable": False,
        "internet_reachable": False,
        "dns_working": False,
    }


def create_healthy_network_evidence():
    return {
        "active_adapter": {
            "is_up": True,
            "addresses": [
                {
                    "type": "IPv4",
                    "address": "192.168.1.20",
                    "classification": "PRIVATE",
                }
            ],
        },
        "gateway": "192.168.1.1",
        "gateway_reachable": True,
        "internet_reachable": True,
        "dns_working": True,
    }


def test_network_pipeline_detects_adapter_correlation():
    _, _, findings, correlations = diagnose_network_pipeline(
        create_disconnected_adapter_evidence()
    )

    assert any(
        finding.finding_type == "NETWORK_ADAPTER_DISCONNECTED"
        for finding in findings
    )

    assert any(
        correlation.correlation_type == "NETWORK_ADAPTER_FAILURE"
        for correlation in correlations
    )


def test_network_pipeline_detects_local_network_correlation():
    _, _, findings, correlations = diagnose_network_pipeline(
        create_local_network_failure_evidence()
    )

    finding_types = {
        finding.finding_type
        for finding in findings
    }

    correlation_types = {
        correlation.correlation_type
        for correlation in correlations
    }

    assert "LOCAL_NETWORK_UNREACHABLE" in finding_types
    assert "INTERNET_CONNECTIVITY_FAILURE" in finding_types
    assert "LOCAL_NETWORK_FAILURE" in correlation_types


def test_network_pipeline_preserves_findings_inside_correlations():
    _, _, findings, correlations = diagnose_network_pipeline(
        create_local_network_failure_evidence()
    )

    local_correlation = next(
        correlation
        for correlation in correlations
        if correlation.correlation_type == "LOCAL_NETWORK_FAILURE"
    )

    assert local_correlation.findings
    assert all(
        finding in findings
        for finding in local_correlation.findings
    )


def test_network_pipeline_produces_no_correlations_for_healthy_network():
    _, signals, findings, correlations = diagnose_network_pipeline(
        create_healthy_network_evidence()
    )

    assert signals == []
    assert findings == []
    assert correlations == []