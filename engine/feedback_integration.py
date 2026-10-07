from copy import deepcopy

from engine.intelligence_feedback import IntelligenceFeedback
from engine.learning_signal import LearningSignal
from engine.outcome_capture import OutcomeCapture
from engine.outcome_comparison import OutcomeComparison
from engine.recommendation_feedback import RecommendationFeedback
from engine.root_cause_feedback import RootCauseFeedback
from engine.diagnostic_confidence_feedback import (
    DiagnosticConfidenceFeedback,
)


class FeedbackIntegration:
    """
    Coordinates the Phase 7 feedback pipeline.

    Flow:

        feedback
            -> outcome capture
            -> comparison
            -> learning signal

    Feedback remains observational. Integration does not
    modify diagnosis, root causes, confidence, recommendations,
    or remediation state.
    """

    def capture_outcome(
        self,
        feedback,
        observed,
        outcome="UNKNOWN",
        metadata=None,
    ):
        if not isinstance(
            feedback,
            IntelligenceFeedback,
        ):
            raise ValueError(
                "Feedback integration requires "
                "an IntelligenceFeedback record."
            )

        return OutcomeCapture().capture(
            feedback,
            observed=observed,
            outcome=outcome,
            metadata=metadata,
        )

    def compare_outcome(self, feedback):
        if not isinstance(
            feedback,
            IntelligenceFeedback,
        ):
            raise ValueError(
                "Feedback integration requires "
                "an IntelligenceFeedback record."
            )

        return OutcomeComparison().compare(feedback)

    def create_learning_signal(
        self,
        feedback,
        signal_type,
        subject_id,
        outcome=None,
        evidence=None,
        metadata=None,
    ):
        if not isinstance(
            feedback,
            IntelligenceFeedback,
        ):
            raise ValueError(
                "Feedback integration requires "
                "an IntelligenceFeedback record."
            )

        signal_outcome = (
            feedback.outcome
            if outcome is None
            else outcome
        )

        signal_evidence = (
            feedback.observed
            if evidence is None
            else evidence
        )

        signal_metadata = deepcopy(
            feedback.metadata
        )

        if not isinstance(signal_metadata, dict):
            signal_metadata = {}

        if metadata is not None:
            if not isinstance(metadata, dict):
                raise ValueError(
                    "Learning signal metadata "
                    "must be a dictionary."
                )
            signal_metadata.update(
                deepcopy(metadata)
            )

        return LearningSignal(
            case_id=feedback.case_id,
            machine_id=feedback.machine_id,
            signal_type=signal_type,
            subject_id=subject_id,
            outcome=signal_outcome,
            feedback_id=feedback.feedback_id,
            evidence=signal_evidence,
            metadata=signal_metadata,
        )

    def build_prediction_feedback(
        self,
        case_id,
        machine_id,
        source,
        event,
        expected,
        observed=None,
        outcome="UNKNOWN",
        confidence="NONE",
        metadata=None,
    ):
        return IntelligenceFeedback(
            case_id=case_id,
            machine_id=machine_id,
            source=source,
            event=event,
            expected=expected,
            observed=observed,
            outcome=outcome,
            confidence=confidence,
            metadata=metadata,
        )

    def build_recommendation_feedback(
        self,
        case_id,
        machine_id,
        recommendation_id,
        recommendation,
        expected_effect,
        observed_effect=None,
        outcome="UNKNOWN",
        metadata=None,
    ):
        return RecommendationFeedback(
            case_id=case_id,
            machine_id=machine_id,
            recommendation_id=recommendation_id,
            recommendation=recommendation,
            expected_effect=expected_effect,
            observed_effect=observed_effect,
            outcome=outcome,
            metadata=metadata,
        )

    def build_root_cause_feedback(
        self,
        case_id,
        machine_id,
        root_cause_id,
        root_cause,
        expected_effect,
        observed_effect=None,
        outcome="UNKNOWN",
        metadata=None,
    ):
        return RootCauseFeedback(
            case_id=case_id,
            machine_id=machine_id,
            root_cause_id=root_cause_id,
            root_cause=root_cause,
            expected_effect=expected_effect,
            observed_effect=observed_effect,
            outcome=outcome,
            metadata=metadata,
        )

    def build_confidence_feedback(
        self,
        case_id,
        machine_id,
        diagnostic_id,
        confidence,
        expected_confidence="NONE",
        observed_confidence="NONE",
        outcome="UNKNOWN",
        evidence=None,
        metadata=None,
    ):
        return DiagnosticConfidenceFeedback(
            case_id=case_id,
            machine_id=machine_id,
            diagnostic_id=diagnostic_id,
            confidence=confidence,
            expected_confidence=expected_confidence,
            observed_confidence=observed_confidence,
            outcome=outcome,
            evidence=evidence,
            metadata=metadata,
        )

    def process(
        self,
        feedback,
        observed,
        signal_type,
        subject_id,
        outcome="UNKNOWN",
        metadata=None,
    ):
        captured = self.capture_outcome(
            feedback,
            observed=observed,
            outcome=outcome,
            metadata=metadata,
        )

        comparison = self.compare_outcome(
            captured
        )

        learning_outcome = (
            comparison["outcome"]
            if captured.outcome == "UNKNOWN"
            else captured.outcome
        )

        signal = self.create_learning_signal(
            captured,
            signal_type=signal_type,
            subject_id=subject_id,
            outcome=learning_outcome,
            evidence={
                "expected": deepcopy(
                    comparison["expected"]
                ),
                "observed": deepcopy(
                    comparison["observed"]
                ),
                "matched_fields": comparison[
                    "matched_fields"
                ],
                "compared_fields": comparison[
                    "compared_fields"
                ],
                "comparison_outcome": comparison[
                    "outcome"
                ],
            },
        )

        return {
            "feedback": captured.to_dict(),
            "comparison": comparison,
            "learning_signal": signal.to_dict(),
        }
