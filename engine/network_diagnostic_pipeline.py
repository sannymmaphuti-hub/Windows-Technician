from engine.network_observation_builder import (
    NetworkObservationBuilder,
)
from engine.observation_to_signal import (
    ObservationToSignal,
)
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
from engine.confidence_engine import ConfidenceEngine
from engine.root_cause_confidence_rule import (
    RootCauseConfidenceRule,
)
from engine.observation import Observation

class NetworkDiagnosticPipeline:

    def __init__(
        self,
        observation_builder=None,
        signal_detector=None,
        finding_engine=None,
        correlation_engine=None,
        root_cause_engine=None,
        root_cause_evaluation_engine=None,
        root_cause_selection=None,
        recommendation_orchestrator=None,
        confidence_engine=None,
    ):
        self.observation_builder = (
            observation_builder
            if observation_builder is not None
            else NetworkObservationBuilder()
        )

        self.signal_detector = (
            signal_detector
            if signal_detector is not None
            else ObservationToSignal()
        )

        self.finding_engine = (
            finding_engine
            if finding_engine is not None
            else self._create_finding_engine()
        )

        self.correlation_engine = (
            correlation_engine
            if correlation_engine is not None
            else self._create_correlation_engine()
        )

        self.root_cause_engine = (
            root_cause_engine
            if root_cause_engine is not None
            else self._create_root_cause_engine()
        )

        self.root_cause_evaluation_engine = (
            root_cause_evaluation_engine
            if root_cause_evaluation_engine is not None
            else self._create_root_cause_evaluation_engine()
        )

        self.root_cause_selection = (
            root_cause_selection
            if root_cause_selection is not None
            else RootCauseSelection()
        )

        self.recommendation_orchestrator = (
            recommendation_orchestrator
            if recommendation_orchestrator is not None
            else NetworkRecommendationOrchestrator()
        )

        self.confidence_engine = (
            confidence_engine
            if confidence_engine is not None
            else self._create_confidence_engine()
        )

        self._adaptive_observations = []
        self._adaptive_signals = []
        self._adaptive_findings = []

    @staticmethod
    def _create_finding_engine():

        engine = FindingEngine()

        engine.register_rule(
            NetworkAdapterFindingRule()
        )

        engine.register_rule(
            LocalNetworkUnreachableRule()
        )

        engine.register_rule(
            DNSResolutionFailureRule()
        )

        engine.register_rule(
            InternetConnectivityFailureRule()
        )

        return engine

    @staticmethod
    def _create_correlation_engine():

        engine = CorrelationEngine()

        engine.register_rule(
            NetworkAdapterCorrelationRule()
        )

        engine.register_rule(
            LocalNetworkFailureCorrelationRule()
        )

        return engine

    @staticmethod
    def _create_root_cause_engine():

        engine = RootCauseEngine()

        engine.register_rule(
            DNSFailureRootCauseRule()
        )

        engine.register_rule(
            LocalNetworkFailureRootCauseRule()
        )

        engine.register_rule(
            NetworkAdapterFailureRootCauseRule()
        )

        return engine

    @staticmethod
    def _create_root_cause_evaluation_engine():

        engine = RootCauseEvaluationEngine()

        engine.register_rule(
            DNSFailureEvaluationRule()
        )

        engine.register_rule(
            LocalNetworkFailureEvaluationRule()
        )

        engine.register_rule(
            NetworkAdapterFailureEvaluationRule()
        )

        return engine

    @staticmethod
    def _create_confidence_engine():

        engine = ConfidenceEngine()

        engine.register_rule(
            RootCauseConfidenceRule()
        )

        return engine

    def diagnose(self, evidence):

        observations = self.observation_builder.build(
            evidence
        )

        signals = []
        findings = []

        for observation in observations:

            signal = self.signal_detector.detect(
                observation
            )

            if signal is None:
                continue

            signals.append(signal)

            findings.extend(
                self.finding_engine.detect(
                    signal
                )
            )

        correlations = (
            self.correlation_engine.detect(
                findings
            )
        )

        candidates = (
            self.root_cause_engine.detect(
                findings
            )
        )

        evaluations = []

        for candidate in candidates:

            evaluations.extend(
                self.root_cause_evaluation_engine.evaluate(
                    candidate,
                    findings,
                )
            )

        primary_cause = (
            self.root_cause_selection.select(
                evaluations
            )
        )

        confidences = []

        for candidate in candidates:

            candidate_confidences = (
                self.confidence_engine.evaluate(
                    candidate,
                    evaluations,
                )
            )

            confidences.extend(
                candidate_confidences
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
            "confidences": confidences,
            "explanations": [],
            "recommendation": recommendation,
        }

    def process_observation(self, observation):
        normalized_observations = (
            self.normalize_observation(observation)
        )

        if not isinstance(
            normalized_observations,
            list,
        ):
            normalized_observations = [
                normalized_observations
            ]

        for normalized_observation in (
            normalized_observations
        ):
            self._adaptive_observations.append(
                normalized_observation
            )

            signal = self.signal_detector.detect(
                normalized_observation
            )

            if signal is None:
                continue

            self._adaptive_signals.append(
                signal
            )

            findings = self.finding_engine.detect(
                signal
            )

            self._adaptive_findings.extend(
                findings
            )

        correlations = self.correlation_engine.detect(
            self._adaptive_findings
        )

        candidates = self.root_cause_engine.detect(
            self._adaptive_findings
        )

        evaluations = []

        for candidate in candidates:
            evaluations.extend(
                self.root_cause_evaluation_engine.evaluate(
                    candidate,
                    self._adaptive_findings,
                )
            )

        primary_cause = self.root_cause_selection.select(
            evaluations
        )

        confidences = []

        for candidate in candidates:
            candidate_confidences = (
                self.confidence_engine.evaluate(
                    candidate,
                    evaluations,
                )
            )

            confidences.extend(
                candidate_confidences
            )

        recommendation = (
            self.recommendation_orchestrator.recommend(
                primary_cause,
                evaluations,
            )
        )

        return {
            "observations": list(
                self._adaptive_observations
            ),
            "signals": list(
                self._adaptive_signals
            ),
            "findings": list(
                self._adaptive_findings
            ),
            "correlations": correlations,
            "candidates": candidates,
            "evaluations": evaluations,
            "primary_cause": primary_cause,
            "confidences": confidences,
            "explanations": [],
            "recommendation": recommendation,
        }

    def get_adaptive_result(self):
        correlations = self.correlation_engine.detect(
            self._adaptive_findings
        )

        candidates = self.root_cause_engine.detect(
            self._adaptive_findings
        )

        evaluations = []

        for candidate in candidates:
            evaluations.extend(
                self.root_cause_evaluation_engine.evaluate(
                    candidate,
                    self._adaptive_findings,
                )
            )

        primary_cause = self.root_cause_selection.select(
            evaluations
        )

        confidences = []

        for candidate in candidates:
            confidences.extend(
                self.confidence_engine.evaluate(
                    candidate,
                    evaluations,
                )
            )

        recommendation = (
            self.recommendation_orchestrator.recommend(
                primary_cause,
                evaluations,
            )
        )

        return {
            "observations": list(
                self._adaptive_observations
            ),
            "signals": list(
                self._adaptive_signals
            ),
            "findings": list(
                self._adaptive_findings
            ),
            "correlations": correlations,
            "candidates": candidates,
            "evaluations": evaluations,
            "primary_cause": primary_cause,
            "confidences": confidences,
            "explanations": [],
            "recommendation": recommendation,
        }
    def reset_adaptive(self):
        self._adaptive_observations = []
        self._adaptive_signals = []
        self._adaptive_findings = []

    def normalize_observation(self, observation):

        if not isinstance(observation, Observation):
            raise ValueError(
                "observation must be an Observation."
            )

        if observation.source != "diagnostic_action":
            return observation

        if (
            observation.subject == "network_gateway"
            and observation.attribute == "reachable"
        ):
            return Observation(
                source="network",
                subject="network_gateway",
                attribute="reachable",
                value=observation.value,
            )

        if (
            observation.subject == "dns"
            and observation.attribute == "resolution_working"
        ):
            return Observation(
                source="network",
                subject="network_dns",
                attribute="working",
                value=observation.value,
            )

        if (
            observation.subject == "internet"
            and observation.attribute == "reachable"
        ):
            return Observation(
                source="network",
                subject="network_internet",
                attribute="reachable",
                value=observation.value,
            )

        if (
            observation.subject == "network_adapter"
            and observation.attribute == "state"
        ):
            if not isinstance(observation.value, list):
                raise ValueError(
                    "Network adapter observation value must be a list."
                )

            normalized_observations = []

            for adapter in observation.value:
                if not isinstance(adapter, dict):
                    raise ValueError(
                        "Network adapter entry must be a dictionary."
                    )

                if "is_up" not in adapter:
                    raise ValueError(
                        "Network adapter entry must contain 'is_up'."
                    )

                normalized_observations.append(
                    Observation(
                        source="network",
                        subject="network_adapter",
                        attribute="is_up",
                        value=adapter["is_up"],
                    )
                )

            return normalized_observations

        raise ValueError(
            "Unsupported diagnostic network observation."
        )
