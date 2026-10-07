from copy import deepcopy

from engine.feedback_integration import FeedbackIntegration
from engine.intelligence_feedback import IntelligenceFeedback


def test_phase7_complete_prediction_feedback_flow():
    integration = FeedbackIntegration()

    original = integration.build_prediction_feedback(
        "case-100",
        "machine-100",
        "SYSTEM_HEALTH",
        "HEALTH_PREDICTION",
        {
            "status": "healthy",
            "severity": "LOW",
        },
        confidence="MEDIUM",
    )

    before = deepcopy(original.to_dict())

    result = integration.process(
        original,
        observed={
            "status": "healthy",
            "severity": "HIGH",
        },
        signal_type="PREDICTION",
        subject_id="health-prediction-100",
        outcome="PARTIAL",
    )

    assert result["comparison"]["outcome"] == "PARTIAL"
    assert (
        result["learning_signal"]["outcome"]
        == "PARTIAL"
    )

    assert original.to_dict() == before


def test_phase7_feedback_preserves_case_identity():
    integration = FeedbackIntegration()

    feedback = integration.build_prediction_feedback(
        "case-200",
        "machine-200",
        "SYSTEM",
        "TEST",
        {"status": "healthy"},
    )

    result = integration.process(
        feedback,
        observed={"status": "degraded"},
        signal_type="PREDICTION",
        subject_id="test-200",
        outcome="REFUTED",
    )

    assert result["feedback"]["case_id"] == "CASE-200"
    assert result["learning_signal"]["case_id"] == "CASE-200"
    assert (
        result["learning_signal"]["feedback_id"]
        == result["feedback"]["feedback_id"]
    )


def test_phase7_supports_all_learning_signal_types():
    integration = FeedbackIntegration()

    for signal_type in (
        "PREDICTION",
        "RECOMMENDATION",
        "ROOT_CAUSE",
        "CONFIDENCE",
    ):
        feedback = integration.build_prediction_feedback(
            "case-300",
            "machine-300",
            "SYSTEM",
            "TEST",
            {"status": "healthy"},
            observed={"status": "healthy"},
            outcome="CONFIRMED",
        )

        result = integration.process(
            feedback,
            observed={"status": "healthy"},
            signal_type=signal_type,
            subject_id=f"subject-{signal_type}",
        )

        assert (
            result["learning_signal"]["signal_type"]
            == signal_type
        )


def test_phase7_supports_all_outcomes():
    integration = FeedbackIntegration()

    for outcome in (
        "CONFIRMED",
        "PARTIAL",
        "REFUTED",
        "UNKNOWN",
    ):
        feedback = integration.build_prediction_feedback(
            "case-400",
            "machine-400",
            "SYSTEM",
            "TEST",
            {"status": "healthy"},
        )

        observed = (
            {"status": "healthy"}
            if outcome != "UNKNOWN"
            else None
        )

        result = integration.process(
            feedback,
            observed=observed,
            signal_type="PREDICTION",
            subject_id=f"subject-{outcome}",
            outcome=outcome,
        )

        assert (
            result["learning_signal"]["outcome"]
            == outcome
        )


def test_phase7_learning_signal_contains_structured_evidence():
    integration = FeedbackIntegration()

    feedback = integration.build_prediction_feedback(
        "case-500",
        "machine-500",
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
        subject_id="subject-500",
    )

    evidence = result["learning_signal"]["evidence"]

    assert evidence["expected"]["status"] == "healthy"
    assert evidence["observed"]["severity"] == "HIGH"
    assert evidence["matched_fields"] == 1
    assert evidence["compared_fields"] == 2


def test_phase7_does_not_modify_original_feedback():
    integration = FeedbackIntegration()

    feedback = integration.build_prediction_feedback(
        "case-600",
        "machine-600",
        "SYSTEM",
        "TEST",
        {
            "status": "healthy",
        },
        metadata={
            "origin": "diagnostic",
        },
    )

    before = deepcopy(feedback.to_dict())

    integration.process(
        feedback,
        observed={
            "status": "degraded",
        },
        signal_type="PREDICTION",
        subject_id="subject-600",
        outcome="REFUTED",
    )

    assert feedback.to_dict() == before


def test_phase7_has_no_remediation_surface():
    integration = FeedbackIntegration()

    feedback = integration.build_prediction_feedback(
        "case-700",
        "machine-700",
        "SYSTEM",
        "TEST",
        {"status": "healthy"},
    )

    result = integration.process(
        feedback,
        observed={"status": "healthy"},
        signal_type="PREDICTION",
        subject_id="subject-700",
    )

    forbidden = {
        "execute",
        "executed",
        "remediate",
        "remediation",
        "authorize",
        "authorization",
        "authorized",
    }

    assert forbidden.isdisjoint(result.keys())
    assert forbidden.isdisjoint(
        result["learning_signal"].keys()
    )


def test_phase7_has_no_autonomous_learning_surface():
    integration = FeedbackIntegration()

    feedback = integration.build_prediction_feedback(
        "case-800",
        "machine-800",
        "SYSTEM",
        "TEST",
        {"status": "healthy"},
    )

    result = integration.process(
        feedback,
        observed={"status": "healthy"},
        signal_type="PREDICTION",
        subject_id="subject-800",
    )

    assert "learn" not in result
    assert "train" not in result
    assert "update_model" not in result
    assert "self_modify" not in result


def test_phase7_learning_signal_is_append_only():
    integration = FeedbackIntegration()

    feedback = integration.build_prediction_feedback(
        "case-900",
        "machine-900",
        "SYSTEM",
        "TEST",
        {"status": "healthy"},
    )

    result_one = integration.process(
        feedback,
        observed={"status": "healthy"},
        signal_type="PREDICTION",
        subject_id="subject-900",
    )

    result_two = integration.process(
        feedback,
        observed={"status": "degraded"},
        signal_type="PREDICTION",
        subject_id="subject-900",
        outcome="REFUTED",
    )

    assert (
        result_one["learning_signal"]["signal_id"]
        != result_two["learning_signal"]["signal_id"]
    )

    assert (
        result_one["feedback"]["feedback_id"]
        != result_two["feedback"]["feedback_id"]
    )


def test_phase7_original_intelligence_feedback_contract_remains_intact():
    feedback = IntelligenceFeedback(
        "case-1000",
        "machine-1000",
        "SYSTEM",
        "TEST",
        expected={"status": "healthy"},
        observed={"status": "healthy"},
        outcome="CONFIRMED",
        confidence="HIGH",
    )

    data = feedback.to_dict()

    assert data["case_id"] == "CASE-1000"
    assert data["machine_id"] == "MACHINE-1000"
    assert data["outcome"] == "CONFIRMED"
    assert data["confidence"] == "HIGH"


def test_phase7_is_observational_not_authoritative():
    integration = FeedbackIntegration()

    feedback = integration.build_prediction_feedback(
        "case-1100",
        "machine-1100",
        "SYSTEM",
        "ROOT_CAUSE_CANDIDATE",
        {
            "cause": "resource pressure",
        },
        confidence="HIGH",
    )

    result = integration.process(
        feedback,
        observed={
            "cause": "different cause",
        },
        signal_type="ROOT_CAUSE",
        subject_id="cause-1100",
        outcome="REFUTED",
    )

    assert (
        result["comparison"]["outcome"]
        == "REFUTED"
    )

    assert (
        result["learning_signal"]["outcome"]
        == "REFUTED"
    )

    assert "root_cause" not in result
    assert "root_causes" not in result
    assert "confidence" not in result


def test_phase7_can_feed_future_intelligence_without_doing_so_automatically():
    integration = FeedbackIntegration()

    feedback = integration.build_prediction_feedback(
        "case-1200",
        "machine-1200",
        "SYSTEM",
        "TEST",
        {"status": "healthy"},
    )

    result = integration.process(
        feedback,
        observed={"status": "healthy"},
        signal_type="PREDICTION",
        subject_id="subject-1200",
    )

    learning_signal = result["learning_signal"]

    assert learning_signal["outcome"] == "CONFIRMED"
    assert learning_signal["feedback_id"] == (
        result["feedback"]["feedback_id"]
    )

    # The signal exists for future intelligence.
    # This pipeline does not consume it automatically.
    assert "future_intelligence" not in result


def test_phase7_complete_result_is_structured():
    integration = FeedbackIntegration()

    feedback = integration.build_prediction_feedback(
        "case-1300",
        "machine-1300",
        "SYSTEM",
        "TEST",
        {"status": "healthy"},
    )

    result = integration.process(
        feedback,
        observed={"status": "healthy"},
        signal_type="PREDICTION",
        subject_id="subject-1300",
    )

    assert isinstance(result, dict)
    assert isinstance(result["feedback"], dict)
    assert isinstance(result["comparison"], dict)
    assert isinstance(
        result["learning_signal"],
        dict,
    )


def test_phase7_does_not_require_diagnostic_mutation():
    integration = FeedbackIntegration()

    feedback = integration.build_prediction_feedback(
        "case-1400",
        "machine-1400",
        "SYSTEM",
        "TEST",
        {"status": "healthy"},
    )

    result = integration.process(
        feedback,
        observed={"status": "degraded"},
        signal_type="PREDICTION",
        subject_id="subject-1400",
        outcome="REFUTED",
    )

    assert "diagnostic_case" not in result
    assert "modify_diagnosis" not in result
    assert "update_diagnosis" not in result
