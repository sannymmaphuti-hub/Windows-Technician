# ==========================================
# Windows Technician v0.9
# INTELLIGENCE FEEDBACK ARCHITECTURE
# ==========================================

import pytest

from engine.intelligence_feedback import (
    IntelligenceFeedback,
)


def test_feedback_requires_case_id():
    with pytest.raises(ValueError):
        IntelligenceFeedback(
            case_id="",
            machine_id="MACHINE-01",
            source="DIAGNOSTIC",
            event="PREDICTION",
        )


def test_feedback_requires_machine_id():
    with pytest.raises(ValueError):
        IntelligenceFeedback(
            case_id="CASE-01",
            machine_id="",
            source="DIAGNOSTIC",
            event="PREDICTION",
        )


def test_feedback_requires_source():
    with pytest.raises(ValueError):
        IntelligenceFeedback(
            case_id="CASE-01",
            machine_id="MACHINE-01",
            source="",
            event="PREDICTION",
        )


def test_feedback_requires_event():
    with pytest.raises(ValueError):
        IntelligenceFeedback(
            case_id="CASE-01",
            machine_id="MACHINE-01",
            source="DIAGNOSTIC",
            event="",
        )


def test_feedback_normalizes_identifiers():
    feedback = IntelligenceFeedback(
        case_id=" CASE-01 ",
        machine_id=" machine-01 ",
        source=" diagnostic ",
        event=" prediction ",
    )

    assert feedback.case_id == "CASE-01"
    assert feedback.machine_id == "MACHINE-01"
    assert feedback.source == "DIAGNOSTIC"
    assert feedback.event == "PREDICTION"


def test_feedback_accepts_expected_and_observed_values():
    feedback = IntelligenceFeedback(
        case_id="CASE-01",
        machine_id="MACHINE-01",
        source="DIAGNOSTIC",
        event="PREDICTION",
        expected={
            "finding_type": "MEMORY_PRESSURE",
        },
        observed={
            "finding_type": "MEMORY_PRESSURE",
        },
    )

    assert feedback.expected == {
        "finding_type": "MEMORY_PRESSURE",
    }

    assert feedback.observed == {
        "finding_type": "MEMORY_PRESSURE",
    }


def test_feedback_defaults_to_unknown_outcome():
    feedback = IntelligenceFeedback(
        case_id="CASE-01",
        machine_id="MACHINE-01",
        source="DIAGNOSTIC",
        event="PREDICTION",
    )

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
def test_feedback_accepts_supported_outcomes(
    outcome,
):
    feedback = IntelligenceFeedback(
        case_id="CASE-01",
        machine_id="MACHINE-01",
        source="DIAGNOSTIC",
        event="PREDICTION",
        outcome=outcome,
    )

    assert feedback.outcome == outcome


def test_feedback_normalizes_outcome():
    feedback = IntelligenceFeedback(
        case_id="CASE-01",
        machine_id="MACHINE-01",
        source="DIAGNOSTIC",
        event="PREDICTION",
        outcome=" confirmed ",
    )

    assert feedback.outcome == "CONFIRMED"


def test_invalid_outcome_is_rejected():
    with pytest.raises(ValueError):
        IntelligenceFeedback(
            case_id="CASE-01",
            machine_id="MACHINE-01",
            source="DIAGNOSTIC",
            event="PREDICTION",
            outcome="INVALID",
        )


@pytest.mark.parametrize(
    "confidence",
    [
        "LOW",
        "MEDIUM",
        "HIGH",
        "NONE",
    ],
)
def test_feedback_accepts_supported_confidence(
    confidence,
):
    feedback = IntelligenceFeedback(
        case_id="CASE-01",
        machine_id="MACHINE-01",
        source="DIAGNOSTIC",
        event="PREDICTION",
        confidence=confidence,
    )

    assert feedback.confidence == confidence


def test_invalid_confidence_is_rejected():
    with pytest.raises(ValueError):
        IntelligenceFeedback(
            case_id="CASE-01",
            machine_id="MACHINE-01",
            source="DIAGNOSTIC",
            event="PREDICTION",
            confidence="INVALID",
        )


def test_feedback_defaults_confidence_to_none():
    feedback = IntelligenceFeedback(
        case_id="CASE-01",
        machine_id="MACHINE-01",
        source="DIAGNOSTIC",
        event="PREDICTION",
    )

    assert feedback.confidence == "NONE"


def test_feedback_preserves_metadata():
    metadata = {
        "domain": "MEMORY",
        "finding_id": "FINDING-01",
    }

    feedback = IntelligenceFeedback(
        case_id="CASE-01",
        machine_id="MACHINE-01",
        source="DIAGNOSTIC",
        event="PREDICTION",
        metadata=metadata,
    )

    assert feedback.metadata == metadata


def test_feedback_metadata_is_defensively_copied():
    metadata = {
        "domain": "MEMORY",
    }

    feedback = IntelligenceFeedback(
        case_id="CASE-01",
        machine_id="MACHINE-01",
        source="DIAGNOSTIC",
        event="PREDICTION",
        metadata=metadata,
    )

    metadata["domain"] = "PROCESS"

    assert feedback.metadata == {
        "domain": "MEMORY",
    }


def test_feedback_has_feedback_id():
    feedback = IntelligenceFeedback(
        case_id="CASE-01",
        machine_id="MACHINE-01",
        source="DIAGNOSTIC",
        event="PREDICTION",
    )

    assert isinstance(
        feedback.feedback_id,
        str,
    )

    assert feedback.feedback_id


def test_feedback_ids_are_unique():
    first = IntelligenceFeedback(
        case_id="CASE-01",
        machine_id="MACHINE-01",
        source="DIAGNOSTIC",
        event="PREDICTION",
    )

    second = IntelligenceFeedback(
        case_id="CASE-01",
        machine_id="MACHINE-01",
        source="DIAGNOSTIC",
        event="PREDICTION",
    )

    assert first.feedback_id != second.feedback_id


def test_feedback_has_timestamp():
    feedback = IntelligenceFeedback(
        case_id="CASE-01",
        machine_id="MACHINE-01",
        source="DIAGNOSTIC",
        event="PREDICTION",
    )

    assert feedback.timestamp is not None


def test_feedback_to_dict_exposes_canonical_surface():
    feedback = IntelligenceFeedback(
        case_id="CASE-01",
        machine_id="MACHINE-01",
        source="DIAGNOSTIC",
        event="PREDICTION",
        expected={
            "finding_type": "MEMORY_PRESSURE",
        },
        observed={
            "finding_type": "MEMORY_PRESSURE",
        },
        outcome="CONFIRMED",
        confidence="HIGH",
        metadata={
            "domain": "MEMORY",
        },
    )

    result = feedback.to_dict()

    assert result["feedback_id"] == (
        feedback.feedback_id
    )
    assert result["case_id"] == "CASE-01"
    assert result["machine_id"] == "MACHINE-01"
    assert result["source"] == "DIAGNOSTIC"
    assert result["event"] == "PREDICTION"
    assert result["expected"] == {
        "finding_type": "MEMORY_PRESSURE",
    }
    assert result["observed"] == {
        "finding_type": "MEMORY_PRESSURE",
    }
    assert result["outcome"] == "CONFIRMED"
    assert result["confidence"] == "HIGH"
    assert result["metadata"] == {
        "domain": "MEMORY",
    }
    assert result["timestamp"] == feedback.timestamp


def test_feedback_does_not_contain_remediation_state():
    feedback = IntelligenceFeedback(
        case_id="CASE-01",
        machine_id="MACHINE-01",
        source="DIAGNOSTIC",
        event="PREDICTION",
    )

    result = feedback.to_dict()

    assert "execute" not in result
    assert "executed" not in result
    assert "authorization" not in result
    assert "remediation" not in result


def test_feedback_does_not_modify_expected_or_observed():
    expected = {
        "finding_type": "MEMORY_PRESSURE",
    }

    observed = {
        "finding_type": "HIGH_PROCESS_MEMORY",
    }

    feedback = IntelligenceFeedback(
        case_id="CASE-01",
        machine_id="MACHINE-01",
        source="DIAGNOSTIC",
        event="PREDICTION",
        expected=expected,
        observed=observed,
    )

    expected["finding_type"] = "CHANGED"
    observed["finding_type"] = "CHANGED"

    assert feedback.expected == {
        "finding_type": "MEMORY_PRESSURE",
    }

    assert feedback.observed == {
        "finding_type": "HIGH_PROCESS_MEMORY",
    }

