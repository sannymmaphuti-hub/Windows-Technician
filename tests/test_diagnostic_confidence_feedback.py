from engine.diagnostic_confidence_feedback import (
    DiagnosticConfidenceFeedback,
)


def test_requires_case_id():
    try:
        DiagnosticConfidenceFeedback(
            "",
            "machine-01",
            "finding-01",
            "HIGH",
        )
        assert False
    except ValueError:
        assert True


def test_requires_machine_id():
    try:
        DiagnosticConfidenceFeedback(
            "case-01",
            "",
            "finding-01",
            "HIGH",
        )
        assert False
    except ValueError:
        assert True


def test_requires_diagnostic_id():
    try:
        DiagnosticConfidenceFeedback(
            "case-01",
            "machine-01",
            "",
            "HIGH",
        )
        assert False
    except ValueError:
        assert True


def test_requires_confidence():
    try:
        DiagnosticConfidenceFeedback(
            "case-01",
            "machine-01",
            "finding-01",
            None,
        )
        assert False
    except ValueError:
        assert True


def test_normalizes_identifiers():
    feedback = DiagnosticConfidenceFeedback(
        " case-01 ",
        " machine-01 ",
        " finding-01 ",
        " high ",
    )

    assert feedback.case_id == "CASE-01"
    assert feedback.machine_id == "MACHINE-01"
    assert feedback.diagnostic_id == "FINDING-01"


def test_normalizes_confidence():
    feedback = DiagnosticConfidenceFeedback(
        "case-01",
        "machine-01",
        "finding-01",
        " high ",
    )

    assert feedback.confidence == "HIGH"


def test_accepts_low_confidence():
    feedback = DiagnosticConfidenceFeedback(
        "case-01",
        "machine-01",
        "finding-01",
        "LOW",
    )

    assert feedback.confidence == "LOW"


def test_accepts_medium_confidence():
    feedback = DiagnosticConfidenceFeedback(
        "case-01",
        "machine-01",
        "finding-01",
        "MEDIUM",
    )

    assert feedback.confidence == "MEDIUM"


def test_accepts_high_confidence():
    feedback = DiagnosticConfidenceFeedback(
        "case-01",
        "machine-01",
        "finding-01",
        "HIGH",
    )

    assert feedback.confidence == "HIGH"


def test_accepts_none_confidence():
    feedback = DiagnosticConfidenceFeedback(
        "case-01",
        "machine-01",
        "finding-01",
        "NONE",
    )

    assert feedback.confidence == "NONE"


def test_rejects_invalid_confidence():
    try:
        DiagnosticConfidenceFeedback(
            "case-01",
            "machine-01",
            "finding-01",
            "CERTAIN",
        )
        assert False
    except ValueError:
        assert True


def test_rejects_non_string_confidence():
    try:
        DiagnosticConfidenceFeedback(
            "case-01",
            "machine-01",
            "finding-01",
            123,
        )
        assert False
    except ValueError:
        assert True


def test_expected_confidence_defaults_to_none():
    feedback = DiagnosticConfidenceFeedback(
        "case-01",
        "machine-01",
        "finding-01",
        "HIGH",
    )

    assert feedback.expected_confidence == "NONE"


def test_expected_confidence_is_normalized():
    feedback = DiagnosticConfidenceFeedback(
        "case-01",
        "machine-01",
        "finding-01",
        "HIGH",
        expected_confidence=" medium ",
    )

    assert feedback.expected_confidence == "MEDIUM"


def test_observed_confidence_defaults_to_none():
    feedback = DiagnosticConfidenceFeedback(
        "case-01",
        "machine-01",
        "finding-01",
        "HIGH",
    )

    assert feedback.observed_confidence == "NONE"


def test_observed_confidence_is_normalized():
    feedback = DiagnosticConfidenceFeedback(
        "case-01",
        "machine-01",
        "finding-01",
        "HIGH",
        observed_confidence=" low ",
    )

    assert feedback.observed_confidence == "LOW"


def test_accepts_all_expected_confidence_values():
    for value in ["LOW", "MEDIUM", "HIGH", "NONE"]:
        feedback = DiagnosticConfidenceFeedback(
            "case-01",
            "machine-01",
            "finding-01",
            "HIGH",
            expected_confidence=value,
        )

        assert feedback.expected_confidence == value


def test_accepts_all_observed_confidence_values():
    for value in ["LOW", "MEDIUM", "HIGH", "NONE"]:
        feedback = DiagnosticConfidenceFeedback(
            "case-01",
            "machine-01",
            "finding-01",
            "HIGH",
            observed_confidence=value,
        )

        assert feedback.observed_confidence == value


def test_rejects_invalid_expected_confidence():
    try:
        DiagnosticConfidenceFeedback(
            "case-01",
            "machine-01",
            "finding-01",
            "HIGH",
            expected_confidence="CERTAIN",
        )
        assert False
    except ValueError:
        assert True


def test_rejects_invalid_observed_confidence():
    try:
        DiagnosticConfidenceFeedback(
            "case-01",
            "machine-01",
            "finding-01",
            "HIGH",
            observed_confidence="CERTAIN",
        )
        assert False
    except ValueError:
        assert True


def test_outcome_defaults_to_unknown():
    feedback = DiagnosticConfidenceFeedback(
        "case-01",
        "machine-01",
        "finding-01",
        "HIGH",
    )

    assert feedback.outcome == "UNKNOWN"


def test_accepts_confirmed_outcome():
    feedback = DiagnosticConfidenceFeedback(
        "case-01",
        "machine-01",
        "finding-01",
        "HIGH",
        outcome="CONFIRMED",
    )

    assert feedback.outcome == "CONFIRMED"


def test_accepts_partial_outcome():
    feedback = DiagnosticConfidenceFeedback(
        "case-01",
        "machine-01",
        "finding-01",
        "HIGH",
        outcome="partial",
    )

    assert feedback.outcome == "PARTIAL"


def test_accepts_refuted_outcome():
    feedback = DiagnosticConfidenceFeedback(
        "case-01",
        "machine-01",
        "finding-01",
        "HIGH",
        outcome="REFUTED",
    )

    assert feedback.outcome == "REFUTED"


def test_rejects_invalid_outcome():
    try:
        DiagnosticConfidenceFeedback(
            "case-01",
            "machine-01",
            "finding-01",
            "HIGH",
            outcome="PROVEN",
        )
        assert False
    except ValueError:
        assert True


def test_evidence_is_defensively_copied():
    evidence = {
        "source": "verification",
        "status": "healthy",
    }

    feedback = DiagnosticConfidenceFeedback(
        "case-01",
        "machine-01",
        "finding-01",
        "HIGH",
        evidence=evidence,
    )

    evidence["status"] = "changed"

    assert feedback.evidence["status"] == "healthy"


def test_evidence_defaults_to_empty_dict():
    feedback = DiagnosticConfidenceFeedback(
        "case-01",
        "machine-01",
        "finding-01",
        "HIGH",
    )

    assert feedback.evidence == {}


def test_metadata_is_preserved():
    feedback = DiagnosticConfidenceFeedback(
        "case-01",
        "machine-01",
        "finding-01",
        "HIGH",
        metadata={"source": "verification"},
    )

    assert feedback.metadata == {
        "source": "verification"
    }


def test_metadata_is_defensively_copied():
    metadata = {"source": "verification"}

    feedback = DiagnosticConfidenceFeedback(
        "case-01",
        "machine-01",
        "finding-01",
        "HIGH",
        metadata=metadata,
    )

    metadata["source"] = "changed"

    assert feedback.metadata["source"] == "verification"


def test_feedback_id_exists():
    feedback = DiagnosticConfidenceFeedback(
        "case-01",
        "machine-01",
        "finding-01",
        "HIGH",
    )

    assert feedback.feedback_id


def test_feedback_ids_are_unique():
    first = DiagnosticConfidenceFeedback(
        "case-01",
        "machine-01",
        "finding-01",
        "HIGH",
    )

    second = DiagnosticConfidenceFeedback(
        "case-01",
        "machine-01",
        "finding-01",
        "HIGH",
    )

    assert first.feedback_id != second.feedback_id


def test_timestamp_exists():
    feedback = DiagnosticConfidenceFeedback(
        "case-01",
        "machine-01",
        "finding-01",
        "HIGH",
    )

    assert feedback.timestamp
    assert "T" in feedback.timestamp


def test_to_dict_contains_canonical_fields():
    feedback = DiagnosticConfidenceFeedback(
        "case-01",
        "machine-01",
        "finding-01",
        "HIGH",
        expected_confidence="MEDIUM",
        observed_confidence="LOW",
        outcome="PARTIAL",
        evidence={"status": "changed"},
        metadata={"source": "verification"},
    )

    data = feedback.to_dict()

    assert data["feedback_id"] == feedback.feedback_id
    assert data["case_id"] == "CASE-01"
    assert data["machine_id"] == "MACHINE-01"
    assert data["diagnostic_id"] == "FINDING-01"
    assert data["confidence"] == "HIGH"
    assert data["expected_confidence"] == "MEDIUM"
    assert data["observed_confidence"] == "LOW"
    assert data["outcome"] == "PARTIAL"
    assert data["evidence"]["status"] == "changed"
    assert data["metadata"]["source"] == "verification"
    assert data["timestamp"] == feedback.timestamp


def test_to_dict_returns_defensive_copies():
    feedback = DiagnosticConfidenceFeedback(
        "case-01",
        "machine-01",
        "finding-01",
        "HIGH",
        evidence={"status": "healthy"},
        metadata={"source": "verification"},
    )

    data = feedback.to_dict()

    data["evidence"]["status"] = "changed"
    data["metadata"]["source"] = "changed"

    assert feedback.evidence["status"] == "healthy"
    assert feedback.metadata["source"] == "verification"


def test_does_not_change_original_confidence():
    feedback = DiagnosticConfidenceFeedback(
        "case-01",
        "machine-01",
        "finding-01",
        "HIGH",
        observed_confidence="LOW",
        outcome="REFUTED",
    )

    assert feedback.confidence == "HIGH"
    assert feedback.observed_confidence == "LOW"


def test_no_learning_surface():
    feedback = DiagnosticConfidenceFeedback(
        "case-01",
        "machine-01",
        "finding-01",
        "HIGH",
        outcome="CONFIRMED",
    )

    assert not hasattr(feedback, "learn")
    assert not hasattr(feedback, "learning_signal")
    assert not hasattr(feedback, "learning_signals")


def test_no_diagnostic_mutation_surface():
    feedback = DiagnosticConfidenceFeedback(
        "case-01",
        "machine-01",
        "finding-01",
        "HIGH",
        outcome="REFUTED",
    )

    assert not hasattr(feedback, "diagnostic_case")
    assert not hasattr(feedback, "root_cause")
    assert not hasattr(feedback, "root_causes")


def test_no_recommendation_or_remediation_surface():
    feedback = DiagnosticConfidenceFeedback(
        "case-01",
        "machine-01",
        "finding-01",
        "HIGH",
    )

    assert not hasattr(feedback, "recommend")
    assert not hasattr(feedback, "recommendations")
    assert not hasattr(feedback, "execute")
    assert not hasattr(feedback, "remediate")


def test_none_observation_can_remain_unknown():
    feedback = DiagnosticConfidenceFeedback(
        "case-01",
        "machine-01",
        "finding-01",
        "HIGH",
        observed_confidence="NONE",
    )

    assert feedback.observed_confidence == "NONE"
    assert feedback.outcome == "UNKNOWN"
