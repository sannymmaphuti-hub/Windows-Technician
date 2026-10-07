# ==========================================
# Windows Technician v0.9
# PHASE 7.2
# OUTCOME CAPTURE
# ==========================================

import pytest

from engine.intelligence_feedback import (
    IntelligenceFeedback,
)
from engine.outcome_capture import (
    OutcomeCapture,
)


def make_feedback():
    return IntelligenceFeedback(
        case_id="CASE-01",
        machine_id="MACHINE-01",
        source="DIAGNOSTIC",
        event="PREDICTION",
        expected={
            "finding_type": "MEMORY_PRESSURE",
        },
        confidence="HIGH",
        metadata={
            "domain": "MEMORY",
        },
    )


def test_outcome_capture_requires_feedback():
    with pytest.raises(ValueError):
        OutcomeCapture().capture(
            None,
            observed={
                "finding_type": "MEMORY_PRESSURE",
            },
        )


def test_outcome_capture_requires_intelligence_feedback():
    with pytest.raises(ValueError):
        OutcomeCapture().capture(
            "invalid",
            observed={
                "finding_type": "MEMORY_PRESSURE",
            },
        )


def test_outcome_capture_creates_feedback_record():
    original = make_feedback()

    captured = OutcomeCapture().capture(
        original,
        observed={
            "finding_type": "MEMORY_PRESSURE",
        },
    )

    assert isinstance(
        captured,
        IntelligenceFeedback,
    )


def test_outcome_capture_preserves_case_id():
    original = make_feedback()

    captured = OutcomeCapture().capture(
        original,
        observed={
            "finding_type": "MEMORY_PRESSURE",
        },
    )

    assert captured.case_id == "CASE-01"


def test_outcome_capture_preserves_machine_id():
    original = make_feedback()

    captured = OutcomeCapture().capture(
        original,
        observed={
            "finding_type": "MEMORY_PRESSURE",
        },
    )

    assert captured.machine_id == "MACHINE-01"


def test_outcome_capture_preserves_expected_value():
    original = make_feedback()

    captured = OutcomeCapture().capture(
        original,
        observed={
            "finding_type": "HIGH_PROCESS_MEMORY",
        },
    )

    assert captured.expected == {
        "finding_type": "MEMORY_PRESSURE",
    }


def test_outcome_capture_records_observed_value():
    original = make_feedback()

    observed = {
        "finding_type": "HIGH_PROCESS_MEMORY",
    }

    captured = OutcomeCapture().capture(
        original,
        observed=observed,
    )

    assert captured.observed == observed


def test_outcome_capture_defaults_to_unknown():
    original = make_feedback()

    captured = OutcomeCapture().capture(
        original,
        observed={
            "finding_type": "MEMORY_PRESSURE",
        },
    )

    assert captured.outcome == "UNKNOWN"


@pytest.mark.parametrize(
    "outcome",
    [
        "CONFIRMED",
        "PARTIAL",
        "REFUTED",
        "UNKNOWN",
    ],
)
def test_outcome_capture_accepts_explicit_outcome(
    outcome,
):
    original = make_feedback()

    captured = OutcomeCapture().capture(
        original,
        observed={
            "finding_type": "MEMORY_PRESSURE",
        },
        outcome=outcome,
    )

    assert captured.outcome == outcome


def test_outcome_capture_normalizes_outcome():
    original = make_feedback()

    captured = OutcomeCapture().capture(
        original,
        observed={
            "finding_type": "MEMORY_PRESSURE",
        },
        outcome=" confirmed ",
    )

    assert captured.outcome == "CONFIRMED"


def test_outcome_capture_rejects_invalid_outcome():
    original = make_feedback()

    with pytest.raises(ValueError):
        OutcomeCapture().capture(
            original,
            observed={
                "finding_type": "MEMORY_PRESSURE",
            },
            outcome="INVALID",
        )


def test_outcome_capture_preserves_original_feedback():
    original = make_feedback()

    original_expected = {
        "finding_type": "MEMORY_PRESSURE",
    }

    captured = OutcomeCapture().capture(
        original,
        observed={
            "finding_type": "HIGH_PROCESS_MEMORY",
        },
        outcome="REFUTED",
    )

    assert original.expected == original_expected
    assert original.observed is None
    assert original.outcome == "UNKNOWN"


def test_outcome_capture_creates_new_feedback_id():
    original = make_feedback()

    captured = OutcomeCapture().capture(
        original,
        observed={
            "finding_type": "MEMORY_PRESSURE",
        },
    )

    assert captured.feedback_id != (
        original.feedback_id
    )


def test_outcome_capture_links_original_feedback():
    original = make_feedback()

    captured = OutcomeCapture().capture(
        original,
        observed={
            "finding_type": "MEMORY_PRESSURE",
        },
    )

    assert captured.metadata[
        "source_feedback_id"
    ] == original.feedback_id


def test_outcome_capture_preserves_original_metadata():
    original = make_feedback()

    captured = OutcomeCapture().capture(
        original,
        observed={
            "finding_type": "MEMORY_PRESSURE",
        },
    )

    assert captured.metadata["domain"] == (
        "MEMORY"
    )


def test_outcome_capture_metadata_is_defensively_copied():
    original = make_feedback()

    metadata = {
        "operator": "TECHNICIAN",
    }

    captured = OutcomeCapture().capture(
        original,
        observed={
            "finding_type": "MEMORY_PRESSURE",
        },
        metadata=metadata,
    )

    metadata["operator"] = "CHANGED"

    assert captured.metadata[
        "operator"
    ] == "TECHNICIAN"


def test_outcome_capture_observed_value_is_defensively_copied():
    original = make_feedback()

    observed = {
        "finding_type": "MEMORY_PRESSURE",
        "severity": "WARNING",
    }

    captured = OutcomeCapture().capture(
        original,
        observed=observed,
    )

    observed["severity"] = "CRITICAL"

    assert captured.observed == {
        "finding_type": "MEMORY_PRESSURE",
        "severity": "WARNING",
    }


def test_outcome_capture_does_not_execute_remediation():
    original = make_feedback()

    captured = OutcomeCapture().capture(
        original,
        observed={
            "finding_type": "MEMORY_PRESSURE",
        },
    )

    result = captured.to_dict()

    assert "execute" not in result
    assert "executed" not in result
    assert "authorization" not in result
    assert "remediation" not in result


def test_outcome_capture_does_not_change_original_confidence():
    original = make_feedback()

    captured = OutcomeCapture().capture(
        original,
        observed={
            "finding_type": "HIGH_PROCESS_MEMORY",
        },
        outcome="REFUTED",
    )

    assert original.confidence == "HIGH"
    assert captured.confidence == "HIGH"


def test_outcome_capture_sets_event_to_outcome():
    original = make_feedback()

    captured = OutcomeCapture().capture(
        original,
        observed={
            "finding_type": "MEMORY_PRESSURE",
        },
    )

    assert captured.event == "OUTCOME"


def test_outcome_capture_uses_outcome_capture_source():
    original = make_feedback()

    captured = OutcomeCapture().capture(
        original,
        observed={
            "finding_type": "MEMORY_PRESSURE",
        },
    )

    assert captured.source == "OUTCOME_CAPTURE"


def test_outcome_capture_requires_observed_argument():
    original = make_feedback()

    with pytest.raises(ValueError):
        OutcomeCapture().capture(
            original,
        )


def test_outcome_capture_accepts_none_observed_as_unknown():
    original = make_feedback()

    captured = OutcomeCapture().capture(
        original,
        observed=None,
    )

    assert captured.observed is None
    assert captured.outcome == "UNKNOWN"


def test_outcome_capture_does_not_compare_expected_and_observed():
    original = make_feedback()

    captured = OutcomeCapture().capture(
        original,
        observed={
            "finding_type": "MEMORY_PRESSURE",
        },
    )

    assert captured.outcome == "UNKNOWN"
