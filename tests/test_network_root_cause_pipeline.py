from engine.correlation_engine import CorrelationEngine
from engine.dns_failure_root_cause_rule import DNSFailureRootCauseRule
from engine.finding_engine import FindingEngine
from engine.dns_resolution_failure_rule import DNSResolutionFailureRule
from engine.internet_connectivity_failure_rule import (
    InternetConnectivityFailureRule,
)
from engine.local_network_failure_correlation_rule import (
    LocalNetworkFailureCorrelationRule,
)
from engine.local_network_failure_root_cause_rule import (
    LocalNetworkFailureRootCauseRule,
)
from engine.local_network_unreachable_rule import (
    LocalNetworkUnreachableRule,
)
from engine.network_adapter_correlation_rule import (
    NetworkAdapterCorrelationRule,
)
from engine.network_adapter_failure_evaluation_rule import (
    NetworkAdapterFailureEvaluationRule,
)
from engine.network_adapter_failure_root_cause_rule import (
    NetworkAdapterFailureRootCauseRule,
)
from engine.network_adapter_finding_rule import (
    NetworkAdapterFindingRule,
)
from engine.network_observation_builder import NetworkObservationBuilder
from engine.observation_to_signal import ObservationToSignal
from engine.root_cause_engine import RootCauseEngine
from engine.root_cause_evaluation_engine import RootCauseEvaluationEngine
from engine.root_cause_evaluation_pipeline import (
    RootCauseEvaluationPipeline,
)
from engine.root_cause_selection import RootCauseSelection
from engine.dns_failure_evaluation_rule import DNSFailureEvaluationRule
from engine.local_network_failure_evaluation_rule import (
    LocalNetworkFailureEvaluationRule,
)


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


def create_root_cause_engine():
    engine = RootCauseEngine()

    engine.register_rule(DNSFailureRootCauseRule())
    engine.register_rule(LocalNetworkFailureRootCauseRule())
    engine.register_rule(NetworkAdapterFailureRootCauseRule())

    return engine


def create_evaluation_engine():
    engine = RootCauseEvaluationEngine()

    engine.register_rule(DNSFailureEvaluationRule())
    engine.register_rule(LocalNetworkFailureEvaluationRule())
    engine.register_rule(NetworkAdapterFailureEvaluationRule())

    return engine


def diagnose_network_root_cause(evidence):
    observation_builder = NetworkObservationBuilder()
    signal_detector = ObservationToSignal()
    finding_engine = create_finding_engine()
    correlation_engine = create_correlation_engine()
    root_cause_engine = create_root_cause_engine()
    evaluation_engine = create_evaluation_engine()

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

    candidates = root_cause_engine.detect(findings)

    evaluation_pipeline = RootCauseEvaluationPipeline(
        evaluation_engine=evaluation_engine
    )

    evaluations = evaluation_pipeline.evaluate(
        candidates,
        findings,
    )

    selection = RootCauseSelection()
    primary_cause = selection.select(evaluations)

    return (
        observations,
        signals,
        findings,
        correlations,
        candidates,
        evaluations,
        primary_cause,
    )


def disconnected_adapter_evidence():
    return {
        "active_adapter": {
            "is_up": False,
            "addresses": [],
        },
        "gateway": None,
        "gateway_reachable": None,
        "internet_reachable": None,
        "dns_working": None,
    }

def local_network_failure_evidence():
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


def dns_failure_evidence():
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
        "dns_working": False,
    }


def internet_failure_evidence():
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
        "internet_reachable": False,
        "dns_working": True,
    }


def healthy_network_evidence():
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


def test_disconnected_adapter_reaches_network_root_cause():
    result = diagnose_network_root_cause(
        disconnected_adapter_evidence()
    )

    _, _, findings, correlations, candidates, evaluations, primary = result

    assert any(
        finding.finding_type == "NETWORK_ADAPTER_DISCONNECTED"
        for finding in findings
    )

    assert any(
        correlation.correlation_type == "NETWORK_ADAPTER_FAILURE"
        for correlation in correlations
    )

    assert any(
        candidate.cause_type == "NETWORK_ADAPTER_FAILURE"
        for candidate in candidates
    )

    assert any(
        evaluation.candidate.cause_type
        == "NETWORK_ADAPTER_FAILURE"
        for evaluation in evaluations
    )

    assert primary is not None
    assert primary.cause_type == "NETWORK_ADAPTER_FAILURE"


def test_local_network_failure_reaches_network_root_cause():
    result = diagnose_network_root_cause(
        local_network_failure_evidence()
    )

    _, _, findings, correlations, candidates, evaluations, primary = result

    assert any(
        finding.finding_type == "LOCAL_NETWORK_UNREACHABLE"
        for finding in findings
    )

    assert any(
        finding.finding_type == "INTERNET_CONNECTIVITY_FAILURE"
        for finding in findings
    )

    assert any(
        correlation.correlation_type == "LOCAL_NETWORK_FAILURE"
        for correlation in correlations
    )

    assert any(
        candidate.cause_type == "LOCAL_NETWORK_FAILURE"
        for candidate in candidates
    )

    assert any(
        evaluation.candidate.cause_type
        == "LOCAL_NETWORK_FAILURE"
        for evaluation in evaluations
    )

    assert primary is not None
    assert primary.cause_type == "LOCAL_NETWORK_FAILURE"


def test_dns_failure_reaches_network_root_cause():
    result = diagnose_network_root_cause(
        dns_failure_evidence()
    )

    _, _, findings, _, candidates, evaluations, primary = result

    assert any(
        finding.finding_type == "DNS_RESOLUTION_FAILURE"
        for finding in findings
    )

    assert any(
        candidate.cause_type == "DNS_FAILURE"
        for candidate in candidates
    )

    assert any(
        evaluation.candidate.cause_type == "DNS_FAILURE"
        for evaluation in evaluations
    )

    assert primary is not None
    assert primary.cause_type == "DNS_FAILURE"


def test_internet_failure_alone_does_not_select_specific_root_cause():
    result = diagnose_network_root_cause(
        internet_failure_evidence()
    )

    _, _, findings, correlations, candidates, evaluations, primary = result

    assert any(
        finding.finding_type == "INTERNET_CONNECTIVITY_FAILURE"
        for finding in findings
    )

    assert correlations == []
    assert candidates == []
    assert evaluations == []
    assert primary is None


def test_healthy_network_produces_no_network_root_cause():
    result = diagnose_network_root_cause(
        healthy_network_evidence()
    )

    _, signals, findings, correlations, candidates, evaluations, primary = result

    assert signals == []
    assert findings == []
    assert correlations == []
    assert candidates == []
    assert evaluations == []
    assert primary is None