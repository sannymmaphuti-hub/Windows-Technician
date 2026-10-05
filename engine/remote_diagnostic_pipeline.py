# ==========================================
# Windows Technician v0.8
# REMOTE DIAGNOSTIC PIPELINE
# ==========================================

from engine.remote_diagnostic_input import RemoteDiagnosticInput
from engine.observation_to_signal import ObservationToSignal
from engine.finding_engine import FindingEngine
from engine.correlation_engine import CorrelationEngine
from engine.root_cause_engine import RootCauseEngine
from engine.root_cause_evaluation_engine import (
    RootCauseEvaluationEngine,
)
from engine.root_cause_selection import RootCauseSelection
from engine.network_recommendation_orchestrator import (
    NetworkRecommendationOrchestrator,
)
from engine.confidence_engine import ConfidenceEngine


class RemoteDiagnosticPipeline:

    def __init__(
        self,
        signal_detector=None,
        finding_engine=None,
        correlation_engine=None,
        root_cause_engine=None,
        root_cause_evaluation_engine=None,
        root_cause_selection=None,
        recommendation_orchestrator=None,
        confidence_engine=None,
    ):
        self.signal_detector = (
            signal_detector
            if signal_detector is not None
            else ObservationToSignal()
        )

        self.finding_engine = (
            finding_engine
            if finding_engine is not None
            else FindingEngine()
        )

        self.correlation_engine = (
            correlation_engine
            if correlation_engine is not None
            else CorrelationEngine()
        )

        self.root_cause_engine = (
            root_cause_engine
            if root_cause_engine is not None
            else RootCauseEngine()
        )

        self.root_cause_evaluation_engine = (
            root_cause_evaluation_engine
            if root_cause_evaluation_engine is not None
            else RootCauseEvaluationEngine()
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
            else ConfidenceEngine()
        )

    def diagnose(self, remote_input):

        if not isinstance(
            remote_input,
            RemoteDiagnosticInput,
        ):
            raise ValueError(
                "RemoteDiagnosticPipeline requires "
                "a RemoteDiagnosticInput."
            )

        observations = remote_input.observations

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
            "machine_id": remote_input.machine_id,
            "hostname": remote_input.context.hostname,
            "session_id": remote_input.session_id,
            "is_remote": True,
            "observations": list(observations),
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