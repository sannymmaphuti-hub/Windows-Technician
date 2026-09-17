from engine.network_diagnostic_case_synthesis import (
    NetworkDiagnosticCase,
    NetworkDiagnosticCaseSynthesizer,
)
from engine.network_observation_builder import (
    NetworkObservationBuilder,
)
from engine.observation_to_signal import ObservationToSignal
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
from engine.network_recommendation_orchestrator import (
    NetworkRecommendationOrchestrator,
)


class RealNetworkPipeline:

    def __init__(self):

        self.observation_builder = (
            NetworkObservationBuilder()
        )

        self.signal_detector = ObservationToSignal()

        self.finding_engine = FindingEngine()

        self.finding_engine.register_rule(
            NetworkAdapterFindingRule()
        )
        self.finding_engine.register_rule(
            LocalNetworkUnreachableRule()
        )
        self.finding_engine.register_rule(
            DNSResolutionFailureRule()
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

        self.evaluation_engine = (
            RootCauseEvaluationEngine()
        )

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

        observations = (
            self.observation_builder.build(evidence)
        )

        signals = []

        for observation in observations:

            signal = self.signal_detector.detect(
                observation
            )

            if signal is not None:
                signals.append(signal)

        findings = []

        for signal in signals:

            findings.extend(
                self.finding_engine.detect(signal)
            )

        correlations = (
            self.correlation_engine.detect(findings)
        )

        candidates = (
            self.root_cause_engine.detect(findings)
        )
        evaluations = []

        for candidate in candidates:

            candidate_evaluations = (
                self.evaluation_engine.evaluate(
                    candidate,
                    findings,
                )
            )

            if candidate_evaluations is None:
                continue

            evaluations.extend(candidate_evaluations)

        primary_cause = self.selection.select(
            evaluations
        )

        recommendation = (
            self.recommendation_orchestrator.recommend(
                primary_cause,
                evaluations,
            )
        )

        return {
            "observations": observations,
            "signals": signals,
            "findings": findings,
            "correlations": correlations,
            "candidates": candidates,
            "evaluations": evaluations,
            "primary_cause": primary_cause,
            "confidences": [],
            "explanations": [],
            "recommendation": recommendation,
        }


def create_synthesizer():

    return NetworkDiagnosticCaseSynthesizer(
        pipeline=RealNetworkPipeline()
    )


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


def test_real_network_pipeline_produces_diagnostic_case():

    case = create_synthesizer().synthesize(
        dns_failure_evidence()
    )

    assert isinstance(
        case,
        NetworkDiagnosticCase,
    )


def test_real_network_pipeline_produces_observations():

    case = create_synthesizer().synthesize(
        dns_failure_evidence()
    )

    assert case.observations


def test_real_network_pipeline_produces_dns_signal():

    case = create_synthesizer().synthesize(
        dns_failure_evidence()
    )

    signal_types = [
        signal.signal_type
        for signal in case.signals
    ]

    assert "DNS_RESOLUTION_FAILED" in signal_types


def test_real_network_pipeline_produces_dns_finding():

    case = create_synthesizer().synthesize(
        dns_failure_evidence()
    )

    finding_types = [
        finding.finding_type
        for finding in case.findings
    ]

    assert "DNS_RESOLUTION_FAILURE" in finding_types


def test_real_network_pipeline_identifies_dns_root_cause():

    case = create_synthesizer().synthesize(
        dns_failure_evidence()
    )

    assert case.primary_cause is not None
    assert case.primary_cause.cause_type == "DNS_FAILURE"


def test_real_network_pipeline_produces_dns_recommendation():

    case = create_synthesizer().synthesize(
        dns_failure_evidence()
    )

    assert len(case.recommendations) == 1
    assert (
        case.recommendations[0].recommendation_type
        == "REVIEW_DNS_CONFIGURATION"
    )