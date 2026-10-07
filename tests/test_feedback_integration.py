from copy import deepcopy

import pytest

from engine.feedback_integration import FeedbackIntegration
from engine.intelligence_feedback import IntelligenceFeedback


def test_build_prediction_feedback():
    integration = FeedbackIntegration()

    feedback = integration.build_prediction_feedback(
        "case-1",
        "machine-1",
        "SYSTEM",
        "HEALTH_PREDICTION",
        {"status": "healthy"},
    )

    assert isinstance(feedback, IntelligenceFeedback)
    assert feedback.case_id == "CASE-1"
    assert feedback.machine_id == "MACHINE-1"


def test_capture_outcome():
    integration = FeedbackIntegration()

    feedback = integration.build_prediction_feedback(
        "case-1",
        "machine-1",
        "SYSTEM",
        "HEALTH_PREDICTION",
        {"status": "healthy"},
    )

    captured = integration.capture_outcome(
        feedback,
        observed={"status": "healthy"},
        outcome="CONFIRMED",
    )

    assert captured.observed == {"status": "healthy"}
    assert captured.outcome == "CONFIRMED"
    assert captured.feedback_id != feedback.feedback_id


def test_compare_outcome():
    integration = FeedbackIntegration()

    feedback = integration.build_prediction_feedback(
        "case-1",
        "machine-1",
        "SYSTEM",
        "HEALTH_PREDICTION",
        {"status": "healthy"},
        observed={"status": "healthy"},
    )

    comparison = integration.compare_outcome(feedback)

    assert comparison["outcome"] == "CONFIRMED"


def test_create_learning_signal():
    integration = FeedbackIntegration()

    feedback = integration.build_prediction_feedback(
        "case-1",
        "machine-1",
        "SYSTEM",
        "HEALTH_PREDICTION",
        {"status": "healthy"},
        observed={"status": "healthy"},
        outcome="CONFIRMED",
    )

    signal = integration.create_learning_signal(
        feedback,
        signal_type="PREDICTION",
        subject_id="health-1",
    )

    assert signal.feedback_id == feedback.feedback_id
    assert signal.outcome == "CONFIRMED"
    assert signal.signal_type == "PREDICTION"


def test_process_runs_complete_feedback_pipeline():
    integration = FeedbackIntegration()

    feedback = integration.build_prediction_feedback(
        "case-1",
        "machine-1",
        "SYSTEM",
        "HEALTH_PREDICTION",
        {"status": "healthy"},
    )

    result = integration.process(
        feedback,
        observed={"status": "healthy"},
        signal_type="PREDICTION",
        subject_id="health-1",
        outcome="CONFIRMED",
    )

    assert set(result) == {
        "feedback",
        "comparison",
        "learning_signal",
    }

    assert result["comparison"]["outcome"] == "CONFIRMED"
    assert (
        result["learning_signal"]["outcome"]
        == "CONFIRMED"
    )


def test_process_preserves_original_feedback():
    integration = FeedbackIntegration()

    feedback = integration.build_prediction_feedback(
        "case-1",
        "machine-1",
        "SYSTEM",
        "HEALTH_PREDICTION",
        {"status": "healthy"},
    )

    before = deepcopy(feedback.to_dict())

    integration.process(
        feedback,
        observed={"status": "degraded"},
        signal_type="PREDICTION",
        subject_id="health-1",
        outcome="REFUTED",
    )

    assert feedback.to_dict() == before


def test_process_creates_new_learning_signal():
    integration = FeedbackIntegration()

    feedback = integration.build_prediction_feedback(
        "case-1",
        "machine-1",
        "SYSTEM",
        "HEALTH_PREDICTION",
        {"status": "healthy"},
    )

    result = integration.process(
        feedback,
        observed={"status": "degraded"},
        signal_type="PREDICTION",
        subject_id="health-1",
        outcome="REFUTED",
    )

    assert (
        result["learning_signal"]["feedback_id"]
        == result["feedback"]["feedback_id"]
    )

    assert (
        result["learning_signal"]["signal_id"]
        != result["feedback"]["feedback_id"]
    )


def test_recommendation_feedback_builder():
    integration = FeedbackIntegration()

    feedback = integration.build_recommendation_feedback(
        "case-1",
        "machine-1",
        "rec-1",
        {"action": "review"},
        {"status": "improved"},
    )

    assert feedback.recommendation_id == "REC-1"


def test_root_cause_feedback_builder():
    integration = FeedbackIntegration()

    feedback = integration.build_root_cause_feedback(
        "case-1",
        "machine-1",
        "cause-1",
        {"cause_type": "RESOURCE"},
        {"status": "improved"},
    )

    assert feedback.root_cause_id == "CAUSE-1"


def test_confidence_feedback_builder():
    integration = FeedbackIntegration()

    feedback = integration.build_confidence_feedback(
        "case-1",
        "machine-1",
        "diag-1",
        "MEDIUM",
    )

    assert feedback.diagnostic_id == "DIAG-1"
    assert feedback.confidence == "MEDIUM"


def test_invalid_feedback_is_rejected():
    integration = FeedbackIntegration()

    with pytest.raises(ValueError):
        integration.capture_outcome(
            object(),
            observed={"status": "healthy"},
        )

    with pytest.raises(ValueError):
        integration.compare_outcome(object())

    with pytest.raises(ValueError):
        integration.create_learning_signal(
            object(),
            "PREDICTION",
            "subject-1",
        )


def test_metadata_is_not_shared_mutably():
    integration = FeedbackIntegration()

    metadata = {
        "source": "test",
        "context": {
            "value": 1,
        },
    }

    feedback = integration.build_prediction_feedback(
        "case-1",
        "machine-1",
        "SYSTEM",
        "TEST",
        {"status": "healthy"},
        metadata=metadata,
    )

    result = integration.process(
        feedback,
        observed={"status": "healthy"},
        signal_type="PREDICTION",
        subject_id="test-1",
    )

    result["learning_signal"]["metadata"]["context"]["value"] = 99

    assert metadata["context"]["value"] == 1


def test_learning_signal_contains_comparison_evidence():
    integration = FeedbackIntegration()

    feedback = integration.build_prediction_feedback(
        "case-1",
        "machine-1",
        "SYSTEM",
        "TEST",
        {
            "status": "healthy",
            "severity": "LOW",
        },
    )

    result = integration.process(
        feedback,
        observed={
            "status": "healthy",
            "severity": "HIGH",
        },
        signal_type="PREDICTION",
        subject_id="test-1",
    )

    evidence = result["learning_signal"]["evidence"]

    assert evidence["matched_fields"] == 1
    assert evidence["compared_fields"] == 2


def test_unknown_outcome_remains_unknown_when_values_missing():
    integration = FeedbackIntegration()

    feedback = integration.build_prediction_feedback(
        "case-1",
        "machine-1",
        "SYSTEM",
        "TEST",
        None,
    )

    result = integration.process(
        feedback,
        observed=None,
        signal_type="PREDICTION",
        subject_id="test-1",
    )

    assert result["comparison"]["outcome"] == "UNKNOWN"
    assert result["learning_signal"]["outcome"] == "UNKNOWN"


def test_no_remediation_surface_is_created():
    integration = FeedbackIntegration()

    feedback = integration.build_prediction_feedback(
        "case-1",
        "machine-1",
        "SYSTEM",
        "TEST",
        {"status": "healthy"},
    )

    result = integration.process(
        feedback,
        observed={"status": "healthy"},
        signal_type="PREDICTION",
        subject_id="test-1",
    )

    assert "remediation" not in result
    assert "execute" not in result
    assert "authorization" not in result


def test_no_recommendation_generation_surface_is_created():
    integration = FeedbackIntegration()

    feedback = integration.build_prediction_feedback(
        "case-1",
        "machine-1",
        "SYSTEM",
        "TEST",
        {"status": "healthy"},
    )

    result = integration.process(
        feedback,
        observed={"status": "healthy"},
        signal_type="PREDICTION",
        subject_id="test-1",
    )

    assert "recommendations" not in result
    assert "recommendation" not in result


def test_feedback_integration_is_observational():
    integration = FeedbackIntegration()

    feedback = integration.build_prediction_feedback(
        "case-1",
        "machine-1",
        "SYSTEM",
        "TEST",
        {"status": "healthy"},
    )

    result = integration.process(
        feedback,
        observed={"status": "healthy"},
        signal_type="PREDICTION",
        subject_id="test-1",
    )

    assert result["feedback"]["case_id"] == "CASE-1"
    assert result["learning_signal"]["case_id"] == "CASE-1"
