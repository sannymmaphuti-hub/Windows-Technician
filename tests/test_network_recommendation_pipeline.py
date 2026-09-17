from engine.finding_engine import FindingEngine
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
from engine.network_observation_builder import (
    NetworkObservationBuilder,
)
from engine.observation_to_signal import ObservationToSignal
from engine.correlation_engine import CorrelationEngine
from engine.network_adapter_correlation_rule import (
    NetworkAdapterCorrelationRule,
)
from engine.local_network_failure_correlation_rule import (
    LocalNetworkFailureCorrelationRule,
)
from engine.root_cause_engine import RootCauseEngine
from engine.dns_failure_root_cause_rule import (
    DNSFailureRootCauseRule,
)
from engine.local_network_failure_root_cause_rule import (
    LocalNetworkFailureRootCauseRule,
)
from engine.network_adapter_failure_root_cause_rule import (
    NetworkAdapterFailureRootCauseRule,
)
from engine.root_cause_evaluation_engine import (
    RootCauseEvaluationEngine,
)
from engine.dns_failure_evaluation_rule import (
    DNSFailureEvaluationRule,
)
from engine.local_network_failure_evaluation_rule import (
    LocalNetworkFailureEvaluationRule,
)
from engine.network_adapter_failure_evaluation_rule import (
    NetworkAdapterFailureEvaluationRule,
)
from engine.root_cause_selection import RootCauseSelection
from engine.network_root_cause_recommendation_rule import (
    NetworkRootCauseRecommendationRule,
)

from engine.network_recommendation_orchestrator import (
    NetworkRecommendationOrchestrator,
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


def diagnose_network(evidence):
    observation_builder = NetworkObservationBuilder()
    signal_detector = ObservationToSignal()
    finding_engine = create_finding_engine()
    correlation_engine = create_correlation_engine()
    root_cause_engine = create_root_cause_engine()
    evaluation_engine = create_evaluation_engine()
    selection = RootCauseSelection()
    recommendation_orchestrator = (
            NetworkRecommendationOrchestrator()
        )

    observations = observation_builder.build(evidence)

    signals = []

    for observation in observations:
        signal = signal_detector.detect(observation)

        if signal is not None:
            signals.append(signal)

    findings = []

    for signal in signals:
        findings.extend(
            finding_engine.detect(signal)
        )

    correlations = correlation_engine.detect(findings)

    candidates = root_cause_engine.detect(findings)

    evaluations = []

    for candidate in candidates:
        evaluations.extend(
            evaluation_engine.evaluate(
                candidate,
                findings,
            )
        )

    primary_cause = selection.select(evaluations)

    recommendations = (
        recommendation_orchestrator.recommend(
            primary_cause,
            evaluations,
        )
    )

    recommendation = (
        recommendations[0]
        if recommendations
        else None
    )

    return {
        "observations": observations,
        "signals": signals,
        "findings": findings,
        "correlations": correlations,
        "candidates": candidates,
        "evaluations": evaluations,
        "primary_cause": primary_cause,
        "recommendation": recommendation,
    }



def test_dns_failure_produces_dns_recommendation():
    result = diagnose_network(
        {
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
    )

    assert result["primary_cause"].cause_type == "DNS_FAILURE"
    assert result["recommendation"] is not None
    assert (
        result["recommendation"].recommendation_type
        == "REVIEW_DNS_CONFIGURATION"
    )


def test_local_network_failure_produces_local_network_recommendation():
    result = diagnose_network(
        {
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
    )

    assert (
        result["primary_cause"].cause_type
        == "LOCAL_NETWORK_FAILURE"
    )
    assert result["recommendation"] is not None
    assert (
        result["recommendation"].recommendation_type
        == "REVIEW_LOCAL_NETWORK"
    )


def test_network_adapter_failure_produces_adapter_recommendation():
    result = diagnose_network(
        {
            "active_adapter": {
                "is_up": False,
                "addresses": [],
            }
        }
    )

    assert (
        result["primary_cause"].cause_type
        == "NETWORK_ADAPTER_FAILURE"
    )
    assert result["recommendation"] is not None
    assert (
        result["recommendation"].recommendation_type
        == "REVIEW_NETWORK_ADAPTER"
    )


def test_internet_failure_alone_produces_no_root_cause_recommendation():
    result = diagnose_network(
        {
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
    )

    assert result["primary_cause"] is None
    assert result["recommendation"] is None
