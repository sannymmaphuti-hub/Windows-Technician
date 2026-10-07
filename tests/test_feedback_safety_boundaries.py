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


def test_feedback_objects_do_not_expose_execution():
    objects = [
        IntelligenceFeedback(
            "case-1",
            "machine-1",
            "TEST",
            "PREDICTION",
        ),
        RecommendationFeedback(
            "case-1",
            "machine-1",
            "rec-1",
            {"action": "review"},
            {"status": "improved"},
        ),
        RootCauseFeedback(
            "case-1",
            "machine-1",
            "cause-1",
            {"cause_type": "TEST"},
            {"status": "improved"},
        ),
        DiagnosticConfidenceFeedback(
            "case-1",
            "machine-1",
            "diag-1",
            "MEDIUM",
        ),
        LearningSignal(
            "case-1",
            "machine-1",
            "PREDICTION",
            "subject-1",
            "UNKNOWN",
        ),
    ]

    for obj in objects:
        assert not hasattr(obj, "execute")
        assert not hasattr(obj, "executed")
        assert not hasattr(obj, "remediate")
        assert not hasattr(obj, "authorize")


def test_learning_signal_does_not_expose_recommendation_generation():
    signal = LearningSignal(
        "case-1",
        "machine-1",
        "PREDICTION",
        "subject-1",
        "CONFIRMED",
    )

    assert not hasattr(signal, "recommend")
    assert not hasattr(signal, "recommendations")


def test_learning_signal_does_not_expose_diagnostic_mutation():
    signal = LearningSignal(
        "case-1",
        "machine-1",
        "PREDICTION",
        "subject-1",
        "CONFIRMED",
    )

    assert not hasattr(signal, "diagnostic_case")
    assert not hasattr(signal, "modify_diagnosis")
    assert not hasattr(signal, "update_diagnosis")


def test_learning_signal_does_not_expose_root_cause_mutation():
    signal = LearningSignal(
        "case-1",
        "machine-1",
        "ROOT_CAUSE",
        "cause-1",
        "CONFIRMED",
    )

    assert not hasattr(signal, "root_cause")
    assert not hasattr(signal, "root_causes")
    assert not hasattr(signal, "update_root_cause")


def test_learning_signal_does_not_expose_confidence_mutation():
    signal = LearningSignal(
        "case-1",
        "machine-1",
        "CONFIDENCE",
        "diag-1",
        "CONFIRMED",
    )

    assert not hasattr(signal, "confidence")
    assert not hasattr(signal, "update_confidence")


def test_feedback_is_append_only_observation():
    feedback = IntelligenceFeedback(
        "case-1",
        "machine-1",
        "TEST",
        "PREDICTION",
        expected={"status": "healthy"},
        observed={"status": "healthy"},
        outcome="CONFIRMED",
    )

    before = deepcopy(feedback.to_dict())

    comparison = OutcomeComparison().compare(feedback)

    after = feedback.to_dict()

    assert comparison["outcome"] == "CONFIRMED"
    assert after == before


def test_outcome_capture_does_not_modify_original():
    original = IntelligenceFeedback(
        "case-1",
        "machine-1",
        "TEST",
        "PREDICTION",
        expected={"status": "healthy"},
    )

    before = deepcopy(original.to_dict())

    captured = OutcomeCapture().capture(
        original,
        observed={"status": "degraded"},
        outcome="REFUTED",
    )

    after = original.to_dict()

    assert after == before
    assert captured.feedback_id != original.feedback_id


def test_learning_signal_does_not_modify_evidence():
    evidence = {
        "finding": {
            "severity": "HIGH",
        }
    }

    before = deepcopy(evidence)

    signal = LearningSignal(
        "case-1",
        "machine-1",
        "PREDICTION",
        "finding-1",
        "CONFIRMED",
        evidence=evidence,
    )

    signal.evidence["finding"]["severity"] = "LOW"

    assert evidence == before


def test_learning_signal_does_not_create_remediation_state():
    signal = LearningSignal(
        "case-1",
        "machine-1",
        "RECOMMENDATION",
        "rec-1",
        "CONFIRMED",
    )

    data = signal.to_dict()

    forbidden = {
        "execute",
        "executed",
        "remediate",
        "authorization",
        "authorized",
        "remediation",
    }

    assert forbidden.isdisjoint(data.keys())


def test_feedback_pipeline_has_no_automatic_learning_method():
    signal = LearningSignal(
        "case-1",
        "machine-1",
        "CONFIDENCE",
        "diag-1",
        "CONFIRMED",
    )

    assert not hasattr(signal, "learn")
    assert not hasattr(signal, "train")
    assert not hasattr(signal, "update_model")
    assert not hasattr(signal, "self_modify")
