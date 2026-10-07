# ==========================================
# Windows Technician v0.9
# PHASE 7.4
# RECOMMENDATION FEEDBACK
# ==========================================

import pytest

from engine.recommendation_feedback import (
    RecommendationFeedback,
)


def make_feedback():
    return RecommendationFeedback(
        case_id="CASE-01",
        machine_id="MACHINE-01",
        recommendation_id="REC-01",
        recommendation={
            "action": "REVIEW_MEMORY_USAGE",
            "priority": "HIGH",
        },
        expected_effect={
            "finding_type": "MEMORY_PRESSURE",
            "severity": "WARNING",
        },
    )


def test_recommendation_feedback_requires_case_id():
    with pytest.raises(ValueError):
        RecommendationFeedback(
            case_id="",
            machine_id="MACHINE-01",
            recommendation_id="REC-01",
            recommendation={},
            expected_effect={},
        )


def test_recommendation_feedback_requires_machine_id():
    with pytest.raises(ValueError):
        RecommendationFeedback(
            case_id="CASE-01",
            machine_id="",
            recommendation_id="REC-01",
            recommendation={},
            expected_effect={},
        )


def test_recommendation_feedback_requires_recommendation_id():
    with pytest.raises(ValueError):
        RecommendationFeedback(
            case_id="CASE-01",
            machine_id="MACHINE-01",
            recommendation_id="",
            recommendation={},
            expected_effect={},
        )


def test_recommendation_feedback_requires_recommendation():
    with pytest.raises(ValueError):
        RecommendationFeedback(
            case_id="CASE-01",
            machine_id="MACHINE-01",
            recommendation_id="REC-01",
            recommendation=None,
            expected_effect={},
        )


def test_recommendation_feedback_requires_expected_effect():
    with pytest.raises(ValueError):
        RecommendationFeedback(
            case_id="CASE-01",
            machine_id="MACHINE-01",
            recommendation_id="REC-01",
            recommendation={},
            expected_effect=None,
        )


def test_recommendation_feedback_normalizes_identifiers():
    feedback = RecommendationFeedback(
        case_id=" case-01 ",
        machine_id=" machine-01 ",
        recommendation_id=" rec-01 ",
        recommendation={
            "action": "REVIEW_MEMORY_USAGE",
        },
        expected_effect={
            "finding_type": "MEMORY_PRESSURE",
        },
    )

    assert feedback.case_id == "CASE-01"
    assert feedback.machine_id == "MACHINE-01"
    assert feedback.recommendation_id == "REC-01"


def test_recommendation_feedback_preserves_recommendation():
    feedback = make_feedback()

    assert feedback.recommendation == {
        "action": "REVIEW_MEMORY_USAGE",
        "priority": "HIGH",
    }


def test_recommendation_feedback_preserves_expected_effect():
    feedback = make_feedback()

    assert feedback.expected_effect == {
        "finding_type": "MEMORY_PRESSURE",
        "severity": "WARNING",
    }


def test_recommendation_is_defensively_copied():
    recommendation = {
        "action": "REVIEW_MEMORY_USAGE",
    }

    feedback = RecommendationFeedback(
        case_id="CASE-01",
        machine_id="MACHINE-01",
        recommendation_id="REC-01",
        recommendation=recommendation,
        expected_effect={},
    )

    recommendation["action"] = "CHANGED"

    assert feedback.recommendation == {
        "action": "REVIEW_MEMORY_USAGE",
    }


def test_expected_effect_is_defensively_copied():
    expected = {
        "finding_type": "MEMORY_PRESSURE",
    }

    feedback = RecommendationFeedback(
        case_id="CASE-01",
        machine_id="MACHINE-01",
        recommendation_id="REC-01",
        recommendation={},
        expected_effect=expected,
    )

    expected["finding_type"] = "CHANGED"

    assert feedback.expected_effect == {
        "finding_type": "MEMORY_PRESSURE",
    }


def test_observed_effect_defaults_to_none():
    feedback = make_feedback()

    assert feedback.observed_effect is None


def test_outcome_defaults_to_unknown():
    feedback = make_feedback()

    assert feedback.outcome == "UNKNOWN"


@pytest.mark.parametrize(
    "outcome",
    [
        "CONFIRMED",
        "PARTIAL",
        "REFUTED",
        "UNKNOWN",
    ],
)
def test_supported_outcomes_are_accepted(outcome):
    feedback = RecommendationFeedback(
        case_id="CASE-01",
        machine_id="MACHINE-01",
        recommendation_id="REC-01",
        recommendation={},
        expected_effect={},
        outcome=outcome,
    )

    assert feedback.outcome == outcome


def test_outcome_is_normalized():
    feedback = RecommendationFeedback(
        case_id="CASE-01",
        machine_id="MACHINE-01",
        recommendation_id="REC-01",
        recommendation={},
        expected_effect={},
        outcome=" confirmed ",
    )

    assert feedback.outcome == "CONFIRMED"


def test_invalid_outcome_is_rejected():
    with pytest.raises(ValueError):
        RecommendationFeedback(
            case_id="CASE-01",
            machine_id="MACHINE-01",
            recommendation_id="REC-01",
            recommendation={},
            expected_effect={},
            outcome="INVALID",
        )


def test_observed_effect_can_be_recorded():
    observed = {
        "finding_type": "MEMORY_PRESSURE",
        "severity": "LOW",
    }

    feedback = RecommendationFeedback(
        case_id="CASE-01",
        machine_id="MACHINE-01",
        recommendation_id="REC-01",
        recommendation={},
        expected_effect={
            "finding_type": "MEMORY_PRESSURE",
        },
        observed_effect=observed,
    )

    assert feedback.observed_effect == observed


def test_observed_effect_is_defensively_copied():
    observed = {
        "finding_type": "MEMORY_PRESSURE",
    }

    feedback = RecommendationFeedback(
        case_id="CASE-01",
        machine_id="MACHINE-01",
        recommendation_id="REC-01",
        recommendation={},
        expected_effect={},
        observed_effect=observed,
    )

    observed["finding_type"] = "CHANGED"

    assert feedback.observed_effect == {
        "finding_type": "MEMORY_PRESSURE",
    }


def test_recommendation_feedback_has_unique_id():
    first = make_feedback()
    second = make_feedback()

    assert first.feedback_id != second.feedback_id


def test_recommendation_feedback_has_timestamp():
    feedback = make_feedback()

    assert feedback.timestamp is not None


def test_to_dict_exposes_canonical_surface():
    feedback = RecommendationFeedback(
        case_id="CASE-01",
        machine_id="MACHINE-01",
        recommendation_id="REC-01",
        recommendation={
            "action": "REVIEW_MEMORY_USAGE",
        },
        expected_effect={
            "finding_type": "MEMORY_PRESSURE",
        },
        observed_effect={
            "finding_type": "MEMORY_PRESSURE",
        },
        outcome="CONFIRMED",
    )

    result = feedback.to_dict()

    assert result["feedback_id"] == (
        feedback.feedback_id
    )
    assert result["case_id"] == "CASE-01"
    assert result["machine_id"] == "MACHINE-01"
    assert result["recommendation_id"] == "REC-01"
    assert result["recommendation"] == {
        "action": "REVIEW_MEMORY_USAGE",
    }
    assert result["expected_effect"] == {
        "finding_type": "MEMORY_PRESSURE",
    }
    assert result["observed_effect"] == {
        "finding_type": "MEMORY_PRESSURE",
    }
    assert result["outcome"] == "CONFIRMED"
    assert result["timestamp"] == feedback.timestamp


def test_to_dict_is_defensively_copied():
    feedback = make_feedback()

    result = feedback.to_dict()

    result["recommendation"]["action"] = "CHANGED"
    result["expected_effect"]["finding_type"] = "CHANGED"

    assert feedback.recommendation == {
        "action": "REVIEW_MEMORY_USAGE",
        "priority": "HIGH",
    }

    assert feedback.expected_effect == {
        "finding_type": "MEMORY_PRESSURE",
        "severity": "WARNING",
    }


def test_recommendation_feedback_does_not_execute():
    feedback = make_feedback()

    result = feedback.to_dict()

    assert "execute" not in result
    assert "executed" not in result
    assert "authorization" not in result
    assert "remediation" not in result


def test_recommendation_feedback_does_not_authorize():
    feedback = make_feedback()

    result = feedback.to_dict()

    assert "authorized" not in result
    assert "authorization" not in result


def test_recommendation_feedback_does_not_generate_new_recommendations():
    feedback = make_feedback()

    result = feedback.to_dict()

    assert "recommendations" not in result


def test_recommendation_feedback_does_not_contain_root_cause():
    feedback = make_feedback()

    result = feedback.to_dict()

    assert "root_cause" not in result
    assert "root_causes" not in result


def test_recommendation_feedback_preserves_unknown_without_observation():
    feedback = RecommendationFeedback(
        case_id="CASE-01",
        machine_id="MACHINE-01",
        recommendation_id="REC-01",
        recommendation={
            "action": "REVIEW_MEMORY_USAGE",
        },
        expected_effect={
            "finding_type": "MEMORY_PRESSURE",
        },
    )

    assert feedback.observed_effect is None
    assert feedback.outcome == "UNKNOWN"


def test_recommendation_feedback_preserves_metadata():
    feedback = RecommendationFeedback(
        case_id="CASE-01",
        machine_id="MACHINE-01",
        recommendation_id="REC-01",
        recommendation={},
        expected_effect={},
        metadata={
            "domain": "MEMORY",
            "source_case": "CASE-01",
        },
    )

    assert feedback.metadata == {
        "domain": "MEMORY",
        "source_case": "CASE-01",
    }


def test_metadata_is_defensively_copied():
    metadata = {
        "domain": "MEMORY",
    }

    feedback = RecommendationFeedback(
        case_id="CASE-01",
        machine_id="MACHINE-01",
        recommendation_id="REC-01",
        recommendation={},
        expected_effect={},
        metadata=metadata,
    )

    metadata["domain"] = "PROCESS"

    assert feedback.metadata == {
        "domain": "MEMORY",
    }
