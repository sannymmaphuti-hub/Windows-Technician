from copy import deepcopy

from engine.correlation_engine import CorrelationEngine
from engine.dns_failure_evaluation_rule import DNSFailureEvaluationRule
from engine.dns_failure_root_cause_rule import DNSFailureRootCauseRule
from engine.dns_resolution_failure_rule import DNSResolutionFailureRule
from engine.finding_engine import FindingEngine
from engine.internet_connectivity_failure_rule import (
    InternetConnectivityFailureRule,
)
from engine.local_network_failure_correlation_rule import (
    LocalNetworkFailureCorrelationRule,
)
from engine.local_network_failure_evaluation_rule import (
    LocalNetworkFailureEvaluationRule,
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
from engine.network_adapter_disconnected_rule import (
    NetworkAdapterDisconnectedRule,
)
from engine.network_adapter_failure_evaluation_rule import (
    NetworkAdapterFailureEvaluationRule,
)
from engine.network_adapter_failure_root_cause_rule import (
    NetworkAdapterFailureRootCauseRule,
)
from engine.network_adapter_finding_rule import NetworkAdapterFindingRule
from engine.network_diagnostic_case_synthesis import (
    NetworkDiagnosticCaseSynthesizer,
)
from engine.network_observation_builder import NetworkObservationBuilder
from engine.network_recommendation_orchestrator import (
    NetworkRecommendationOrchestrator,
)
from engine.observation_to_signal import ObservationToSignal
from engine.root_cause_engine import RootCauseEngine
from engine.root_cause_evaluation_engine import RootCauseEvaluationEngine
from engine.root_cause_selection import RootCauseSelection


class RealNetworkPipeline:
    def __init__(self):
        self.observation_builder = NetworkObservationBuilder()
        self.signal_detector = ObservationToSignal()

        self.finding_engine = FindingEngine()
        self.finding_engine.register_rule(NetworkAdapterFindingRule())
        self.finding_engine.register_rule(LocalNetworkUnreachableRule())
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
            findings.extend(
                self.finding_engine.detect(signal)
            )

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
            "recommendation": self.recommendation_orchestrator.recommend(
                primary_cause,
                evaluations,
            ),
        }


def build_synthesizer():
    return NetworkDiagnosticCaseSynthesizer(
        RealNetworkPipeline()
    )


def complete_network_evidence():
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
        "dns_working": True,
    }


def test_empty_evidence_produces_empty_diagnostic_case():
    case = build_synthesizer().synthesize({})

    assert case.observations == []
    assert case.signals == []
    assert case.findings == []
    assert case.correlations == []
    assert case.candidates == []
    assert case.evaluations == []
    assert case.primary_cause is None
    assert case.confidences == []
    assert case.explanations == []
    assert case.recommendations == []


def test_missing_network_fields_do_not_create_findings():
    case = build_synthesizer().synthesize(
        {
            "active_adapter": {
                "name": "Wi-Fi",
                "is_up": True,
                "addresses": [],
            }
        }
    )

    assert case.findings == []
    assert case.candidates == []
    assert case.primary_cause is None
    assert case.recommendations == []


def test_missing_active_adapter_does_not_invent_adapter_failure():
    case = build_synthesizer().synthesize(
        {
            "gateway": "192.168.1.1",
            "gateway_reachable": True,
            "internet_reachable": True,
            "dns_working": True,
        }
    )

    assert case.primary_cause is None
    assert case.recommendations == []


def test_missing_gateway_does_not_invent_local_network_failure():
    evidence = complete_network_evidence()
    del evidence["gateway"]
    del evidence["gateway_reachable"]

    case = build_synthesizer().synthesize(evidence)

    assert case.primary_cause is None
    assert case.recommendations == []


def test_missing_dns_status_does_not_invent_dns_failure():
    evidence = complete_network_evidence()
    del evidence["dns_working"]

    case = build_synthesizer().synthesize(evidence)

    assert case.primary_cause is None
    assert case.recommendations == []


def test_missing_internet_status_does_not_invent_internet_failure():
    evidence = complete_network_evidence()
    del evidence["internet_reachable"]

    case = build_synthesizer().synthesize(evidence)

    assert case.primary_cause is None
    assert case.recommendations == []


def test_partial_evidence_does_not_create_unrelated_root_causes():
    evidence = {
        "active_adapter": {
            "name": "Wi-Fi",
            "is_up": True,
            "addresses": [],
        },
        "dns_working": False,
    }

    case = build_synthesizer().synthesize(evidence)

    assert case.primary_cause is not None
    assert case.primary_cause.cause_type == "DNS_FAILURE"

    assert all(
        candidate.cause_type
        not in {
            "LOCAL_NETWORK_FAILURE",
            "NETWORK_ADAPTER_FAILURE",
        }
        for candidate in case.candidates
    )

    assert all(
        recommendation.recommendation_type
        != "REVIEW_LOCAL_NETWORK"
        for recommendation in case.recommendations
    )

    assert all(
        recommendation.recommendation_type
        != "REVIEW_NETWORK_ADAPTER"
        for recommendation in case.recommendations
    )


def test_healthy_complete_evidence_produces_no_diagnostic_conclusions():
    case = build_synthesizer().synthesize(
        complete_network_evidence()
    )

    assert case.signals == []
    assert case.findings == []
    assert case.correlations == []
    assert case.candidates == []
    assert case.evaluations == []
    assert case.primary_cause is None
    assert case.recommendations == []


def test_synthesis_does_not_mutate_evidence():
    evidence = complete_network_evidence()
    original = deepcopy(evidence)

    build_synthesizer().synthesize(evidence)

    assert evidence == original


def test_nested_evidence_is_not_modified():
    evidence = complete_network_evidence()
    original_adapter = deepcopy(
        evidence["active_adapter"]
    )

    build_synthesizer().synthesize(evidence)

    assert (
        evidence["active_adapter"]
        == original_adapter
    )


def test_no_findings_means_no_correlations():
    case = build_synthesizer().synthesize({})

    assert case.findings == []
    assert case.correlations == []


def test_no_candidates_means_no_evaluations():
    case = build_synthesizer().synthesize({})

    assert case.candidates == []
    assert case.evaluations == []


def test_no_primary_cause_means_no_recommendations():
    case = build_synthesizer().synthesize({})

    assert case.primary_cause is None
    assert case.recommendations == []


def test_boundary_case_preserves_observations_without_inventing_findings():
    evidence = {
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
        }
    }

    case = build_synthesizer().synthesize(evidence)

    assert case.observations
    assert case.signals == []
    assert case.findings == []
    assert case.primary_cause is None


def test_case_always_preserves_all_pipeline_layers():
    case = build_synthesizer().synthesize(
        complete_network_evidence()
    )

    assert hasattr(case, "observations")
    assert hasattr(case, "signals")
    assert hasattr(case, "findings")
    assert hasattr(case, "correlations")
    assert hasattr(case, "candidates")
    assert hasattr(case, "evaluations")
    assert hasattr(case, "primary_cause")
    assert hasattr(case, "confidences")
    assert hasattr(case, "explanations")
    assert hasattr(case, "recommendations")

def test_missing_recommendation_produces_empty_recommendations():
    class PipelineWithoutRecommendation:
        def diagnose(self, evidence):
            return {
                "observations": [],
                "signals": [],
                "findings": [],
                "correlations": [],
                "candidates": [],
                "evaluations": [],
                "primary_cause": None,
                "confidences": [],
                "explanations": [],
                "recommendation": None,
            }

    synthesizer = NetworkDiagnosticCaseSynthesizer(
        PipelineWithoutRecommendation()
    )

    case = synthesizer.synthesize({})

    assert case.recommendations == []

def test_synthesis_preserves_pipeline_layer_objects_by_identity():
    class Pipeline:
        def __init__(self):
            self.observations = [object()]
            self.signals = [object()]
            self.findings = [object()]
            self.correlations = [object()]
            self.candidates = [object()]
            self.evaluations = [object()]
            self.primary_cause = object()
            self.confidences = [object()]
            self.explanations = [object()]
            self.recommendation = object()

        def diagnose(self, evidence):
            return {
                "observations": self.observations,
                "signals": self.signals,
                "findings": self.findings,
                "correlations": self.correlations,
                "candidates": self.candidates,
                "evaluations": self.evaluations,
                "primary_cause": self.primary_cause,
                "confidences": self.confidences,
                "explanations": self.explanations,
                "recommendation": self.recommendation,
            }

    pipeline = Pipeline()
    case = NetworkDiagnosticCaseSynthesizer(
        pipeline
    ).synthesize({})

    assert case.observations[0] is pipeline.observations[0]
    assert case.signals[0] is pipeline.signals[0]
    assert case.findings[0] is pipeline.findings[0]
    assert case.correlations[0] is pipeline.correlations[0]
    assert case.candidates[0] is pipeline.candidates[0]
    assert case.evaluations[0] is pipeline.evaluations[0]
    assert case.primary_cause is pipeline.primary_cause
    assert case.confidences[0] is pipeline.confidences[0]
    assert case.explanations[0] is pipeline.explanations[0]
    assert case.recommendations[0] is pipeline.recommendation