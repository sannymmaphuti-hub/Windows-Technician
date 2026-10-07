from engine.root_cause_feedback import RootCauseFeedback


def test_requires_case_id():
    try:
        RootCauseFeedback("", "machine-01", "cause-01", {"cause_type": "PROCESS_RESOURCE_CONSUMPTION"}, {"memory": "recovered"})
        assert False
    except ValueError:
        assert True


def test_requires_machine_id():
    try:
        RootCauseFeedback("case-01", "", "cause-01", {"cause_type": "PROCESS_RESOURCE_CONSUMPTION"}, {"memory": "recovered"})
        assert False
    except ValueError:
        assert True


def test_requires_root_cause_id():
    try:
        RootCauseFeedback("case-01", "machine-01", "", {"cause_type": "PROCESS_RESOURCE_CONSUMPTION"}, {"memory": "recovered"})
        assert False
    except ValueError:
        assert True


def test_requires_root_cause():
    try:
        RootCauseFeedback("case-01", "machine-01", "cause-01", None, {"memory": "recovered"})
        assert False
    except ValueError:
        assert True


def test_requires_expected_effect():
    try:
        RootCauseFeedback("case-01", "machine-01", "cause-01", {"cause_type": "PROCESS_RESOURCE_CONSUMPTION"}, None)
        assert False
    except ValueError:
        assert True


def test_normalizes_identifiers():
    feedback = RootCauseFeedback(
        " case-01 ",
        " machine-01 ",
        " cause-01 ",
        {"cause_type": "PROCESS_RESOURCE_CONSUMPTION"},
        {"memory": "recovered"},
    )

    assert feedback.case_id == "CASE-01"
    assert feedback.machine_id == "MACHINE-01"
    assert feedback.root_cause_id == "CAUSE-01"


def test_rejects_non_string_case_id():
    try:
        RootCauseFeedback(123, "machine-01", "cause-01", {"cause_type": "PROCESS_RESOURCE_CONSUMPTION"}, {"memory": "recovered"})
        assert False
    except ValueError:
        assert True


def test_rejects_non_string_machine_id():
    try:
        RootCauseFeedback("case-01", 123, "cause-01", {"cause_type": "PROCESS_RESOURCE_CONSUMPTION"}, {"memory": "recovered"})
        assert False
    except ValueError:
        assert True


def test_rejects_non_string_root_cause_id():
    try:
        RootCauseFeedback("case-01", "machine-01", 123, {"cause_type": "PROCESS_RESOURCE_CONSUMPTION"}, {"memory": "recovered"})
        assert False
    except ValueError:
        assert True


def test_root_cause_is_defensively_copied():
    root_cause = {
        "cause_type": "PROCESS_RESOURCE_CONSUMPTION",
        "confidence": "MEDIUM",
    }

    feedback = RootCauseFeedback(
        "case-01",
        "machine-01",
        "cause-01",
        root_cause,
        {"memory": "recovered"},
    )

    root_cause["confidence"] = "HIGH"

    assert feedback.root_cause["confidence"] == "MEDIUM"


def test_expected_effect_is_defensively_copied():
    expected = {"memory": "recovered"}

    feedback = RootCauseFeedback(
        "case-01",
        "machine-01",
        "cause-01",
        {"cause_type": "PROCESS_RESOURCE_CONSUMPTION"},
        expected,
    )

    expected["memory"] = "still_high"

    assert feedback.expected_effect["memory"] == "recovered"


def test_observed_effect_defaults_to_none():
    feedback = RootCauseFeedback(
        "case-01",
        "machine-01",
        "cause-01",
        {"cause_type": "PROCESS_RESOURCE_CONSUMPTION"},
        {"memory": "recovered"},
    )

    assert feedback.observed_effect is None


def test_observed_effect_is_defensively_copied():
    observed = {"memory": "recovered"}

    feedback = RootCauseFeedback(
        "case-01",
        "machine-01",
        "cause-01",
        {"cause_type": "PROCESS_RESOURCE_CONSUMPTION"},
        {"memory": "recovered"},
        observed_effect=observed,
    )

    observed["memory"] = "still_high"

    assert feedback.observed_effect["memory"] == "recovered"


def test_default_outcome_is_unknown():
    feedback = RootCauseFeedback(
        "case-01",
        "machine-01",
        "cause-01",
        {"cause_type": "PROCESS_RESOURCE_CONSUMPTION"},
        {"memory": "recovered"},
    )

    assert feedback.outcome == "UNKNOWN"


def test_accepts_confirmed():
    feedback = RootCauseFeedback(
        "case-01",
        "machine-01",
        "cause-01",
        {"cause_type": "PROCESS_RESOURCE_CONSUMPTION"},
        {"memory": "recovered"},
        outcome="CONFIRMED",
    )

    assert feedback.outcome == "CONFIRMED"


def test_accepts_partial():
    feedback = RootCauseFeedback(
        "case-01",
        "machine-01",
        "cause-01",
        {"cause_type": "PROCESS_RESOURCE_CONSUMPTION"},
        {"memory": "recovered"},
        outcome="partial",
    )

    assert feedback.outcome == "PARTIAL"


def test_accepts_refuted():
    feedback = RootCauseFeedback(
        "case-01",
        "machine-01",
        "cause-01",
        {"cause_type": "PROCESS_RESOURCE_CONSUMPTION"},
        {"memory": "recovered"},
        outcome="REFUTED",
    )

    assert feedback.outcome == "REFUTED"


def test_accepts_unknown():
    feedback = RootCauseFeedback(
        "case-01",
        "machine-01",
        "cause-01",
        {"cause_type": "PROCESS_RESOURCE_CONSUMPTION"},
        {"memory": "recovered"},
        outcome="unknown",
    )

    assert feedback.outcome == "UNKNOWN"


def test_rejects_invalid_outcome():
    try:
        RootCauseFeedback(
            "case-01",
            "machine-01",
            "cause-01",
            {"cause_type": "PROCESS_RESOURCE_CONSUMPTION"},
            {"memory": "recovered"},
            outcome="PROVEN",
        )
        assert False
    except ValueError:
        assert True


def test_rejects_non_string_outcome():
    try:
        RootCauseFeedback(
            "case-01",
            "machine-01",
            "cause-01",
            {"cause_type": "PROCESS_RESOURCE_CONSUMPTION"},
            {"memory": "recovered"},
            outcome=123,
        )
        assert False
    except ValueError:
        assert True


def test_metadata_is_preserved():
    feedback = RootCauseFeedback(
        "case-01",
        "machine-01",
        "cause-01",
        {"cause_type": "PROCESS_RESOURCE_CONSUMPTION"},
        {"memory": "recovered"},
        metadata={"source": "verification"},
    )

    assert feedback.metadata == {"source": "verification"}


def test_metadata_is_defensively_copied():
    metadata = {"source": "verification"}

    feedback = RootCauseFeedback(
        "case-01",
        "machine-01",
        "cause-01",
        {"cause_type": "PROCESS_RESOURCE_CONSUMPTION"},
        {"memory": "recovered"},
        metadata=metadata,
    )

    metadata["source"] = "changed"

    assert feedback.metadata["source"] == "verification"


def test_non_dict_metadata_defaults_to_empty():
    feedback = RootCauseFeedback(
        "case-01",
        "machine-01",
        "cause-01",
        {"cause_type": "PROCESS_RESOURCE_CONSUMPTION"},
        {"memory": "recovered"},
        metadata="invalid",
    )

    assert feedback.metadata == {}


def test_feedback_id_exists():
    feedback = RootCauseFeedback(
        "case-01",
        "machine-01",
        "cause-01",
        {"cause_type": "PROCESS_RESOURCE_CONSUMPTION"},
        {"memory": "recovered"},
    )

    assert feedback.feedback_id


def test_feedback_ids_are_unique():
    first = RootCauseFeedback(
        "case-01",
        "machine-01",
        "cause-01",
        {"cause_type": "PROCESS_RESOURCE_CONSUMPTION"},
        {"memory": "recovered"},
    )

    second = RootCauseFeedback(
        "case-01",
        "machine-01",
        "cause-01",
        {"cause_type": "PROCESS_RESOURCE_CONSUMPTION"},
        {"memory": "recovered"},
    )

    assert first.feedback_id != second.feedback_id


def test_timestamp_exists():
    feedback = RootCauseFeedback(
        "case-01",
        "machine-01",
        "cause-01",
        {"cause_type": "PROCESS_RESOURCE_CONSUMPTION"},
        {"memory": "recovered"},
    )

    assert feedback.timestamp
    assert "T" in feedback.timestamp


def test_to_dict_contains_canonical_fields():
    feedback = RootCauseFeedback(
        "case-01",
        "machine-01",
        "cause-01",
        {"cause_type": "PROCESS_RESOURCE_CONSUMPTION"},
        {"memory": "recovered"},
        {"memory": "normal"},
        "CONFIRMED",
    )

    data = feedback.to_dict()

    assert data["feedback_id"] == feedback.feedback_id
    assert data["case_id"] == "CASE-01"
    assert data["machine_id"] == "MACHINE-01"
    assert data["root_cause_id"] == "CAUSE-01"
    assert data["root_cause"]["cause_type"] == "PROCESS_RESOURCE_CONSUMPTION"
    assert data["expected_effect"]["memory"] == "recovered"
    assert data["observed_effect"]["memory"] == "normal"
    assert data["outcome"] == "CONFIRMED"
    assert data["timestamp"] == feedback.timestamp


def test_to_dict_returns_defensive_copies():
    feedback = RootCauseFeedback(
        "case-01",
        "machine-01",
        "cause-01",
        {"cause_type": "PROCESS_RESOURCE_CONSUMPTION"},
        {"memory": "recovered"},
        {"memory": "normal"},
    )

    data = feedback.to_dict()

    data["root_cause"]["cause_type"] = "CHANGED"
    data["expected_effect"]["memory"] = "CHANGED"
    data["observed_effect"]["memory"] = "CHANGED"

    assert feedback.root_cause["cause_type"] == "PROCESS_RESOURCE_CONSUMPTION"
    assert feedback.expected_effect["memory"] == "recovered"
    assert feedback.observed_effect["memory"] == "normal"


def test_unknown_remains_unknown_without_observation():
    feedback = RootCauseFeedback(
        "case-01",
        "machine-01",
        "cause-01",
        {"cause_type": "PROCESS_RESOURCE_CONSUMPTION"},
        {"memory": "recovered"},
    )

    assert feedback.observed_effect is None
    assert feedback.outcome == "UNKNOWN"


def test_no_execution_surface():
    feedback = RootCauseFeedback(
        "case-01",
        "machine-01",
        "cause-01",
        {"cause_type": "PROCESS_RESOURCE_CONSUMPTION"},
        {"memory": "recovered"},
    )

    assert not hasattr(feedback, "execute")
    assert not hasattr(feedback, "executed")
    assert not hasattr(feedback, "authorize")
    assert not hasattr(feedback, "remediate")


def test_no_recommendation_surface():
    feedback = RootCauseFeedback(
        "case-01",
        "machine-01",
        "cause-01",
        {"cause_type": "PROCESS_RESOURCE_CONSUMPTION"},
        {"memory": "recovered"},
    )

    assert not hasattr(feedback, "recommend")
    assert not hasattr(feedback, "recommendations")


def test_no_diagnostic_mutation_surface():
    feedback = RootCauseFeedback(
        "case-01",
        "machine-01",
        "cause-01",
        {"cause_type": "PROCESS_RESOURCE_CONSUMPTION"},
        {"memory": "recovered"},
    )

    assert not hasattr(feedback, "diagnostic_case")
    assert not hasattr(feedback, "root_causes")


def test_does_not_claim_root_cause_proven():
    feedback = RootCauseFeedback(
        "case-01",
        "machine-01",
        "cause-01",
        {
            "cause_type": "PROCESS_RESOURCE_CONSUMPTION",
            "explanation": "candidate explanation",
        },
        {"memory": "recovered"},
        outcome="CONFIRMED",
    )

    assert feedback.root_cause["explanation"] == "candidate explanation"
    assert not hasattr(feedback, "proven")
    assert not hasattr(feedback, "certainty")


def test_original_root_cause_is_not_mutated():
    root_cause = {
        "cause_type": "PROCESS_RESOURCE_CONSUMPTION",
        "supporting_relationships": [
            {"relationship_type": "RESOURCE_INTERACTION"}
        ],
    }

    feedback = RootCauseFeedback(
        "case-01",
        "machine-01",
        "cause-01",
        root_cause,
        {"memory": "recovered"},
    )

    root_cause["supporting_relationships"][0]["relationship_type"] = "CHANGED"

    assert (
        feedback.root_cause["supporting_relationships"][0]["relationship_type"]
        == "RESOURCE_INTERACTION"
    )
