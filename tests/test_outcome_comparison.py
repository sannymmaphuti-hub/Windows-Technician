# ==========================================
# Windows Technician v0.9
# PHASE 7.3
# PREDICTION VS OUTCOME COMPARISON
# ==========================================

import pytest

from engine.intelligence_feedback import (
    IntelligenceFeedback,
)
from engine.outcome_comparison import (
    OutcomeComparison,
)


def make_feedback(
    expected=None,
    observed=None,
):
    return IntelligenceFeedback(
        case_id="CASE-01",
        machine_id="MACHINE-01",
        source="DIAGNOSTIC",
        event="PREDICTION",
        expected=expected,
        observed=observed,
        confidence="HIGH",
    )


def test_comparison_requires_feedback():
    with pytest.raises(ValueError):
        OutcomeComparison().compare(
            None,
        )


def test_comparison_requires_intelligence_feedback():
    with pytest.raises(ValueError):
        OutcomeComparison().compare(
            "invalid",
        )


def test_identical_expected_and_observed_are_confirmed():
    feedback = make_feedback(
        expected={
            "finding_type": "MEMORY_PRESSURE",
        },
        observed={
            "finding_type": "MEMORY_PRESSURE",
        },
    )

    result = OutcomeComparison().compare(
        feedback,
    )

    assert result["outcome"] == "CONFIRMED"


def test_different_expected_and_observed_are_refuted():
    feedback = make_feedback(
        expected={
            "finding_type": "MEMORY_PRESSURE",
        },
        observed={
            "finding_type": "NETWORK_FAILURE",
        },
    )

    result = OutcomeComparison().compare(
        feedback,
    )

    assert result["outcome"] == "REFUTED"


def test_missing_expected_produces_unknown():
    feedback = make_feedback(
        expected=None,
        observed={
            "finding_type": "MEMORY_PRESSURE",
        },
    )

    result = OutcomeComparison().compare(
        feedback,
    )

    assert result["outcome"] == "UNKNOWN"


def test_missing_observed_produces_unknown():
    feedback = make_feedback(
        expected={
            "finding_type": "MEMORY_PRESSURE",
        },
        observed=None,
    )

    result = OutcomeComparison().compare(
        feedback,
    )

    assert result["outcome"] == "UNKNOWN"


def test_both_missing_produce_unknown():
    feedback = make_feedback()

    result = OutcomeComparison().compare(
        feedback,
    )

    assert result["outcome"] == "UNKNOWN"


def test_string_expected_and_observed_can_match():
    feedback = make_feedback(
        expected="MEMORY_PRESSURE",
        observed="MEMORY_PRESSURE",
    )

    result = OutcomeComparison().compare(
        feedback,
    )

    assert result["outcome"] == "CONFIRMED"


def test_string_expected_and_observed_can_refute():
    feedback = make_feedback(
        expected="MEMORY_PRESSURE",
        observed="NETWORK_FAILURE",
    )

    result = OutcomeComparison().compare(
        feedback,
    )

    assert result["outcome"] == "REFUTED"


def test_nested_structures_are_compared():
    expected = {
        "finding": {
            "type": "MEMORY_PRESSURE",
            "severity": "WARNING",
        },
        "domain": "MEMORY",
    }

    observed = {
        "finding": {
            "type": "MEMORY_PRESSURE",
            "severity": "WARNING",
        },
        "domain": "MEMORY",
    }

    feedback = make_feedback(
        expected=expected,
        observed=observed,
    )

    result = OutcomeComparison().compare(
        feedback,
    )

    assert result["outcome"] == "CONFIRMED"


def test_nested_difference_is_refuted():
    expected = {
        "finding": {
            "type": "MEMORY_PRESSURE",
            "severity": "WARNING",
        },
    }

    observed = {
        "finding": {
            "type": "MEMORY_PRESSURE",
            "severity": "CRITICAL",
        },
    }

    feedback = make_feedback(
        expected=expected,
        observed=observed,
    )

    result = OutcomeComparison().compare(
        feedback,
    )

    assert result["outcome"] == "REFUTED"


def test_partial_matching_fields_are_partial():
    expected = {
        "finding_type": "MEMORY_PRESSURE",
        "domain": "MEMORY",
        "severity": "WARNING",
    }

    observed = {
        "finding_type": "MEMORY_PRESSURE",
        "domain": "MEMORY",
        "severity": "HIGH",
    }

    feedback = make_feedback(
        expected=expected,
        observed=observed,
    )

    result = OutcomeComparison().compare(
        feedback,
    )

    assert result["outcome"] == "PARTIAL"


def test_no_matching_fields_are_refuted():
    expected = {
        "finding_type": "MEMORY_PRESSURE",
        "domain": "MEMORY",
    }

    observed = {
        "finding_type": "NETWORK_FAILURE",
        "domain": "NETWORK",
    }

    feedback = make_feedback(
        expected=expected,
        observed=observed,
    )

    result = OutcomeComparison().compare(
        feedback,
    )

    assert result["outcome"] == "REFUTED"


def test_empty_structures_are_unknown():
    feedback = make_feedback(
        expected={},
        observed={},
    )

    result = OutcomeComparison().compare(
        feedback,
    )

    assert result["outcome"] == "UNKNOWN"


def test_comparison_returns_match_count():
    feedback = make_feedback(
        expected={
            "finding_type": "MEMORY_PRESSURE",
            "domain": "MEMORY",
            "severity": "WARNING",
        },
        observed={
            "finding_type": "MEMORY_PRESSURE",
            "domain": "MEMORY",
            "severity": "HIGH",
        },
    )

    result = OutcomeComparison().compare(
        feedback,
    )

    assert result["matched_fields"] == 2
    assert result["compared_fields"] == 3


def test_full_match_reports_all_fields_matched():
    feedback = make_feedback(
        expected={
            "finding_type": "MEMORY_PRESSURE",
            "domain": "MEMORY",
        },
        observed={
            "finding_type": "MEMORY_PRESSURE",
            "domain": "MEMORY",
        },
    )

    result = OutcomeComparison().compare(
        feedback,
    )

    assert result["matched_fields"] == 2
    assert result["compared_fields"] == 2


def test_comparison_does_not_modify_feedback():
    expected = {
        "finding_type": "MEMORY_PRESSURE",
    }

    observed = {
        "finding_type": "NETWORK_FAILURE",
    }

    feedback = make_feedback(
        expected=expected,
        observed=observed,
    )

    OutcomeComparison().compare(
        feedback,
    )

    assert feedback.expected == expected
    assert feedback.observed == observed
    assert feedback.outcome == "UNKNOWN"


def test_comparison_does_not_modify_nested_feedback():
    expected = {
        "finding": {
            "type": "MEMORY_PRESSURE",
        },
    }

    observed = {
        "finding": {
            "type": "MEMORY_PRESSURE",
        },
    }

    feedback = make_feedback(
        expected=expected,
        observed=observed,
    )

    OutcomeComparison().compare(
        feedback,
    )

    assert feedback.expected == expected
    assert feedback.observed == observed


def test_comparison_preserves_feedback_identity():
    feedback = make_feedback(
        expected={
            "finding_type": "MEMORY_PRESSURE",
        },
        observed={
            "finding_type": "MEMORY_PRESSURE",
        },
    )

    result = OutcomeComparison().compare(
        feedback,
    )

    assert result["feedback_id"] == (
        feedback.feedback_id
    )


def test_comparison_preserves_case_and_machine():
    feedback = make_feedback(
        expected={
            "finding_type": "MEMORY_PRESSURE",
        },
        observed={
            "finding_type": "MEMORY_PRESSURE",
        },
    )

    result = OutcomeComparison().compare(
        feedback,
    )

    assert result["case_id"] == "CASE-01"
    assert result["machine_id"] == "MACHINE-01"


def test_comparison_returns_expected_and_observed():
    expected = {
        "finding_type": "MEMORY_PRESSURE",
    }

    observed = {
        "finding_type": "MEMORY_PRESSURE",
    }

    feedback = make_feedback(
        expected=expected,
        observed=observed,
    )

    result = OutcomeComparison().compare(
        feedback,
    )

    assert result["expected"] == expected
    assert result["observed"] == observed


def test_comparison_result_is_defensively_copied():
    expected = {
        "finding_type": "MEMORY_PRESSURE",
    }

    observed = {
        "finding_type": "MEMORY_PRESSURE",
    }

    feedback = make_feedback(
        expected=expected,
        observed=observed,
    )

    result = OutcomeComparison().compare(
        feedback,
    )

    result["expected"]["finding_type"] = "CHANGED"
    result["observed"]["finding_type"] = "CHANGED"

    assert feedback.expected == expected
    assert feedback.observed == observed


def test_comparison_never_executes_remediation():
    feedback = make_feedback(
        expected={
            "finding_type": "MEMORY_PRESSURE",
        },
        observed={
            "finding_type": "MEMORY_PRESSURE",
        },
    )

    result = OutcomeComparison().compare(
        feedback,
    )

    assert "execute" not in result
    assert "executed" not in result
    assert "authorization" not in result
    assert "remediation" not in result


def test_comparison_never_generates_recommendations():
    feedback = make_feedback(
        expected={
            "finding_type": "MEMORY_PRESSURE",
        },
        observed={
            "finding_type": "MEMORY_PRESSURE",
        },
    )

    result = OutcomeComparison().compare(
        feedback,
    )

    assert "recommendations" not in result


def test_comparison_does_not_change_confidence():
    feedback = make_feedback(
        expected={
            "finding_type": "MEMORY_PRESSURE",
        },
        observed={
            "finding_type": "NETWORK_FAILURE",
        },
    )

    result = OutcomeComparison().compare(
        feedback,
    )

    assert result["confidence"] == "HIGH"
    assert feedback.confidence == "HIGH"
