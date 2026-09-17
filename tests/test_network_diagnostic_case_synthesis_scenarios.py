from engine.correlation_engine import CorrelationEngine
from engine.dns_failure_root_cause_rule import DNSFailureRootCauseRule
from engine.dns_failure_evaluation_rule import DNSFailureEvaluationRule
from engine.finding_engine import FindingEngine
from engine.internet_connectivity_failure_rule import InternetConnectivityFailureRule
from engine.local_network_failure_root_cause_rule import (
    LocalNetworkFailureRootCauseRule,
)
from engine.local_network_failure_evaluation_rule import (
    LocalNetworkFailureEvaluationRule,
)
from engine.local_network_failure_correlation_rule import (
    LocalNetworkFailureCorrelationRule,
)
from engine.network_adapter_correlation_rule import (
    NetworkAdapterCorrelationRule,
)
from engine.network_adapter_disconnected_rule import (
    NetworkAdapterDisconnectedRule,
)
from engine.network_adapter_finding_rule import NetworkAdapterFindingRule
from engine.network_adapter_failure_root_cause_rule import (
    NetworkAdapterFailureRootCauseRule,
)
from engine.network_adapter_failure_evaluation_rule import (
    NetworkAdapterFailureEvaluationRule,
)
from engine.network_diagnostic_case_synthesis import (
    NetworkDiagnosticCaseSynthesizer,
)
from engine.network_observation_builder import NetworkObservationBuilder
from engine.network_recommendation_orchestrator import (
    NetworkRecommendationOrchestrator,
)
from engine.observation_to_signal import ObservationToSignal
from engine.dns_resolution_failed_rule import DNSResolutionFailedRule
from engine.default_gateway_unreachable_rule import (
    DefaultGatewayUnreachableRule,
)
from engine.internet_unreachable_rule import InternetUnreachableRule
from engine.root_cause_engine import RootCauseEngine
from engine.root_cause_evaluation_engine import RootCauseEvaluationEngine
from engine.root_cause_selection import RootCauseSelection


class RealNetworkPipeline:
    def __init__(self):
        self.observation_builder = NetworkObservationBuilder()
        self.signal_detector = ObservationToSignal()

        self.finding_engine = FindingEngine()
        self.finding_engine.register_rule(NetworkAdapterFindingRule())
        self.finding_engine.register_rule(
            __import__(
                "engine.local_network_unreachable_rule",
                fromlist=["LocalNetworkUnreachableRule"],
            ).LocalNetworkUnreachableRule()
        )
        self.finding_engine.register_rule(
            __import__(
                "engine.dns_resolution_failure_rule",
                fromlist=["DNSResolutionFailureRule"],
            ).DNSResolutionFailureRule()
        )
        self.finding_engine.register_rule(
            InternetConnectivityFailureRule()
        )

        self.correlation_engine = CorrelationEngine()
        self.correlation_engine.register_rule(
            NetworkAdapterCorrelationRule()
        )
        self.correlation_engine.register_rule(
            LocalNetworkFailureCorrelationRule()
        )

        self.root_cause_engine = RootCauseEngine()
        self.root_cause_engine.register_rule(
            DNSFailureRootCauseRule()
        )
        self.root_cause_engine.register_rule(
            LocalNetworkFailureRootCauseRule()
        )
        self.root_cause_engine.register_rule(
            NetworkAdapterFailureRootCauseRule()
        )

        self.evaluation_engine = RootCauseEvaluationEngine()
        self.evaluation_engine.register_rule(
            DNSFailureEvaluationRule()
        )
        self.evaluation_engine.register_rule(
            LocalNetworkFailureEvaluationRule()
        )
        self.evaluation_engine.register_rule(
            NetworkAdapterFailureEvaluationRule()
        )

        self.selection = RootCauseSelection()
        self.recommendation_orchestrator = (
            NetworkRecommendationOrchestrator()
        )

    def diagnose(self, evidence):
        observations = self.observation_builder.build(evidence)

        signals = []
        findings = []

        for observation in observations:
            signal = self.signal_detector.detect(observation)

            if signal is None:
                continue

            signals.append(signal)
            findings.extend(self.finding_engine.detect(signal))

        correlations = self.correlation_engine.detect(findings)

        candidates = self.root_cause_engine.detect(findings)

        evaluations = []

        for candidate in candidates:
            candidate_evaluations = self.evaluation_engine.evaluate(
                candidate,
                findings,
            )

            if candidate_evaluations is None:
                continue

            evaluations.extend(candidate_evaluations)

        primary_cause = self.selection.select(evaluations)

        confidences = []

        recommendations = self.recommendation_orchestrator.recommend(
            primary_cause,
            evaluations,
        )

        return {
            "observations": observations,
            "signals": signals,
            "findings": findings,
            "correlations": correlations,
            "candidates": candidates,
            "evaluations": evaluations,
            "primary_cause": primary_cause,
            "confidences": confidences,
            "explanations": [],
            "recommendation": recommendations,
        }


def dns_failure_evidence():
    return {
        "active_adapter": {
            "name": "Wi-Fi",
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


def local_network_failure_evidence():
    evidence = dns_failure_evidence()
    evidence["gateway_reachable"] = False
    evidence["internet_reachable"] = False
    evidence["dns_working"] = True
    return evidence


def adapter_failure_evidence():
    evidence = dns_failure_evidence()

    evidence["active_adapter"]["is_up"] = False
    evidence["gateway_reachable"] = True
    evidence["internet_reachable"] = True
    evidence["dns_working"] = True

    return evidence


def internet_only_failure_evidence():
    evidence = dns_failure_evidence()
    evidence["gateway_reachable"] = True
    evidence["internet_reachable"] = False
    evidence["dns_working"] = True
    return evidence


def healthy_network_evidence():
    evidence = dns_failure_evidence()
    evidence["gateway_reachable"] = True
    evidence["internet_reachable"] = True
    evidence["dns_working"] = True
    return evidence


def build_synthesizer():
    return NetworkDiagnosticCaseSynthesizer(
        RealNetworkPipeline()
    )


def test_dns_failure_scenario():
    case = build_synthesizer().synthesize(
        dns_failure_evidence()
    )

    assert case.primary_cause is not None
    assert case.primary_cause.cause_type == "DNS_FAILURE"

    assert any(
        recommendation.recommendation_type
        == "REVIEW_DNS_CONFIGURATION"
        for recommendation in case.recommendations
    )


def test_local_network_failure_scenario():
    case = build_synthesizer().synthesize(
        local_network_failure_evidence()
    )

    assert case.primary_cause is not None
    assert case.primary_cause.cause_type == "LOCAL_NETWORK_FAILURE"

    assert any(
        recommendation.recommendation_type
        == "REVIEW_LOCAL_NETWORK"
        for recommendation in case.recommendations
    )


def test_network_adapter_failure_scenario():
    case = build_synthesizer().synthesize(
        adapter_failure_evidence()
    )

    assert case.primary_cause is not None
    assert case.primary_cause.cause_type == "NETWORK_ADAPTER_FAILURE"

    assert any(
        recommendation.recommendation_type
        == "REVIEW_NETWORK_ADAPTER"
        for recommendation in case.recommendations
    )


def test_internet_only_failure_has_no_specific_primary_cause():
    case = build_synthesizer().synthesize(
        internet_only_failure_evidence()
    )

    assert case.primary_cause is None
    assert case.recommendations == []


def test_healthy_network_has_no_primary_cause():
    case = build_synthesizer().synthesize(
        healthy_network_evidence()
    )

    assert case.primary_cause is None
    assert case.recommendations == []


def test_dns_failure_case_preserves_network_layers():
    case = build_synthesizer().synthesize(
        dns_failure_evidence()
    )

    assert case.observations
    assert case.signals
    assert case.findings
    assert case.candidates
    assert case.evaluations


def test_local_network_failure_case_contains_correlation():
    case = build_synthesizer().synthesize(
        local_network_failure_evidence()
    )

    assert any(
        correlation.correlation_type
        == "LOCAL_NETWORK_FAILURE"
        for correlation in case.correlations
    )


def test_adapter_failure_case_contains_correlation():
    case = build_synthesizer().synthesize(
        adapter_failure_evidence()
    )

    assert any(
        correlation.correlation_type
        == "NETWORK_ADAPTER_FAILURE"
        for correlation in case.correlations
    )


def test_internet_only_failure_does_not_invent_root_cause():
    case = build_synthesizer().synthesize(
        internet_only_failure_evidence()
    )

    assert case.primary_cause is None
    assert case.recommendations == []


def test_healthy_network_does_not_produce_network_findings():
    case = build_synthesizer().synthesize(
        healthy_network_evidence()
    )

    assert case.signals == []
    assert case.findings == []
    assert case.correlations == []
    assert case.candidates == []
    assert case.evaluations == []