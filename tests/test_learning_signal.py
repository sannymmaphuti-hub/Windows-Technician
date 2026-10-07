from engine.learning_signal import LearningSignal


def test_requires_case_id():
    try:
        LearningSignal(
            "",
            "machine-01",
            "ROOT_CAUSE",
            "cause-01",
            "CONFIRMED",
        )
        assert False
    except ValueError:
        assert True


def test_requires_machine_id():
    try:
        LearningSignal(
            "case-01",
            "",
            "ROOT_CAUSE",
            "cause-01",
            "CONFIRMED",
        )
        assert False
    except ValueError:
        assert True


def test_requires_signal_type():
    try:
        LearningSignal(
            "case-01",
            "machine-01",
            "",
            "cause-01",
            "CONFIRMED",
        )
        assert False
    except ValueError:
        assert True


def test_requires_subject_id():
    try:
        LearningSignal(
            "case-01",
            "machine-01",
            "ROOT_CAUSE",
            "",
            "CONFIRMED",
        )
        assert False
    except ValueError:
        assert True


def test_requires_outcome():
    try:
        LearningSignal(
            "case-01",
            "machine-01",
            "ROOT_CAUSE",
            "cause-01",
            "",
        )
        assert False
    except ValueError:
        assert True


def test_normalizes_identifiers():
    signal = LearningSignal(
        " case-01 ",
        " machine-01 ",
        " root_cause ",
        " cause-01 ",
        " confirmed ",
    )

    assert signal.case_id == "CASE-01"
    assert signal.machine_id == "MACHINE-01"
    assert signal.signal_type == "ROOT_CAUSE"
    assert signal.subject_id == "CAUSE-01"
    assert signal.outcome == "CONFIRMED"


def test_accepts_prediction_signal():
    signal = LearningSignal(
        "case-01",
        "machine-01",
        "PREDICTION",
        "prediction-01",
        "CONFIRMED",
    )

    assert signal.signal_type == "PREDICTION"


def test_accepts_recommendation_signal():
    signal = LearningSignal(
        "case-01",
        "machine-01",
        "RECOMMENDATION",
        "recommendation-01",
        "CONFIRMED",
    )

    assert signal.signal_type == "RECOMMENDATION"


def test_accepts_root_cause_signal():
    signal = LearningSignal(
        "case-01",
        "machine-01",
        "ROOT_CAUSE",
        "cause-01",
        "CONFIRMED",
    )

    assert signal.signal_type == "ROOT_CAUSE"


def test_accepts_confidence_signal():
    signal = LearningSignal(
        "case-01",
        "machine-01",
        "CONFIDENCE",
        "finding-01",
        "PARTIAL",
    )

    assert signal.signal_type == "CONFIDENCE"


def test_rejects_invalid_signal_type():
    try:
        LearningSignal(
            "case-01",
            "machine-01",
            "MAGIC",
            "subject-01",
            "CONFIRMED",
        )
        assert False
    except ValueError:
        assert True


def test_accepts_confirmed():
    signal = LearningSignal(
        "case-01",
        "machine-01",
        "ROOT_CAUSE",
        "cause-01",
        "CONFIRMED",
    )

    assert signal.outcome == "CONFIRMED"


def test_accepts_partial():
    signal = LearningSignal(
        "case-01",
        "machine-01",
        "ROOT_CAUSE",
        "cause-01",
        "PARTIAL",
    )

    assert signal.outcome == "PARTIAL"


def test_accepts_refuted():
    signal = LearningSignal(
        "case-01",
        "machine-01",
        "ROOT_CAUSE",
        "cause-01",
        "REFUTED",
    )

    assert signal.outcome == "REFUTED"


def test_accepts_unknown():
    signal = LearningSignal(
        "case-01",
        "machine-01",
        "ROOT_CAUSE",
        "cause-01",
        "UNKNOWN",
    )

    assert signal.outcome == "UNKNOWN"


def test_rejects_invalid_outcome():
    try:
        LearningSignal(
            "case-01",
            "machine-01",
            "ROOT_CAUSE",
            "cause-01",
            "PROVEN",
        )
        assert False
    except ValueError:
        assert True


def test_evidence_defaults_to_empty_dict():
    signal = LearningSignal(
        "case-01",
        "machine-01",
        "ROOT_CAUSE",
        "cause-01",
        "CONFIRMED",
    )

    assert signal.evidence == {}


def test_evidence_is_defensively_copied():
    evidence = {
        "feedback_id": "FB-01",
        "observed": {"memory": "recovered"},
    }

    signal = LearningSignal(
        "case-01",
        "machine-01",
        "ROOT_CAUSE",
        "cause-01",
        "CONFIRMED",
        evidence=evidence,
    )

    evidence["observed"]["memory"] = "changed"

    assert signal.evidence["observed"]["memory"] == "recovered"


def test_metadata_defaults_to_empty_dict():
    signal = LearningSignal(
        "case-01",
        "machine-01",
        "ROOT_CAUSE",
        "cause-01",
        "CONFIRMED",
    )

    assert signal.metadata == {}


def test_metadata_is_defensively_copied():
    metadata = {"source": "feedback"}

    signal = LearningSignal(
        "case-01",
        "machine-01",
        "ROOT_CAUSE",
        "cause-01",
        "CONFIRMED",
        metadata=metadata,
    )

    metadata["source"] = "changed"

    assert signal.metadata["source"] == "feedback"


def test_feedback_id_can_be_recorded():
    signal = LearningSignal(
        "case-01",
        "machine-01",
        "ROOT_CAUSE",
        "cause-01",
        "CONFIRMED",
        feedback_id="feedback-01",
    )

    assert signal.feedback_id == "FEEDBACK-01"


def test_feedback_id_defaults_to_none():
    signal = LearningSignal(
        "case-01",
        "machine-01",
        "ROOT_CAUSE",
        "cause-01",
        "CONFIRMED",
    )

    assert signal.feedback_id is None


def test_feedback_id_must_be_non_empty_when_supplied():
    try:
        LearningSignal(
            "case-01",
            "machine-01",
            "ROOT_CAUSE",
            "cause-01",
            "CONFIRMED",
            feedback_id="",
        )
        assert False
    except ValueError:
        assert True


def test_signal_id_exists():
    signal = LearningSignal(
        "case-01",
        "machine-01",
        "ROOT_CAUSE",
        "cause-01",
        "CONFIRMED",
    )

    assert signal.signal_id


def test_signal_ids_are_unique():
    first = LearningSignal(
        "case-01",
        "machine-01",
        "ROOT_CAUSE",
        "cause-01",
        "CONFIRMED",
    )

    second = LearningSignal(
        "case-01",
        "machine-01",
        "ROOT_CAUSE",
        "cause-01",
        "CONFIRMED",
    )

    assert first.signal_id != second.signal_id


def test_timestamp_exists():
    signal = LearningSignal(
        "case-01",
        "machine-01",
        "ROOT_CAUSE",
        "cause-01",
        "CONFIRMED",
    )

    assert signal.timestamp
    assert "T" in signal.timestamp


def test_to_dict_contains_canonical_fields():
    signal = LearningSignal(
        "case-01",
        "machine-01",
        "ROOT_CAUSE",
        "cause-01",
        "CONFIRMED",
        feedback_id="feedback-01",
        evidence={"source": "verification"},
        metadata={"stage": "7.7"},
    )

    data = signal.to_dict()

    assert data["signal_id"] == signal.signal_id
    assert data["feedback_id"] == "FEEDBACK-01"
    assert data["case_id"] == "CASE-01"
    assert data["machine_id"] == "MACHINE-01"
    assert data["signal_type"] == "ROOT_CAUSE"
    assert data["subject_id"] == "CAUSE-01"
    assert data["outcome"] == "CONFIRMED"
    assert data["evidence"]["source"] == "verification"
    assert data["metadata"]["stage"] == "7.7"
    assert data["timestamp"] == signal.timestamp


def test_to_dict_returns_defensive_copies():
    signal = LearningSignal(
        "case-01",
        "machine-01",
        "ROOT_CAUSE",
        "cause-01",
        "CONFIRMED",
        evidence={"status": "healthy"},
        metadata={"source": "feedback"},
    )

    data = signal.to_dict()

    data["evidence"]["status"] = "changed"
    data["metadata"]["source"] = "changed"

    assert signal.evidence["status"] == "healthy"
    assert signal.metadata["source"] == "feedback"


def test_non_dict_evidence_defaults_to_empty():
    signal = LearningSignal(
        "case-01",
        "machine-01",
        "ROOT_CAUSE",
        "cause-01",
        "CONFIRMED",
        evidence="invalid",
    )

    assert signal.evidence == {}


def test_non_dict_metadata_defaults_to_empty():
    signal = LearningSignal(
        "case-01",
        "machine-01",
        "ROOT_CAUSE",
        "cause-01",
        "CONFIRMED",
        metadata="invalid",
    )

    assert signal.metadata == {}


def test_learning_signal_does_not_execute():
    signal = LearningSignal(
        "case-01",
        "machine-01",
        "ROOT_CAUSE",
        "cause-01",
        "CONFIRMED",
    )

    assert not hasattr(signal, "execute")
    assert not hasattr(signal, "executed")
    assert not hasattr(signal, "remediate")
    assert not hasattr(signal, "authorize")


def test_learning_signal_does_not_generate_recommendations():
    signal = LearningSignal(
        "case-01",
        "machine-01",
        "ROOT_CAUSE",
        "cause-01",
        "CONFIRMED",
    )

    assert not hasattr(signal, "recommend")
    assert not hasattr(signal, "recommendations")


def test_learning_signal_does_not_modify_diagnosis():
    signal = LearningSignal(
        "case-01",
        "machine-01",
        "ROOT_CAUSE",
        "cause-01",
        "REFUTED",
    )

    assert not hasattr(signal, "diagnostic_case")
    assert not hasattr(signal, "root_cause")
    assert not hasattr(signal, "root_causes")
    assert not hasattr(signal, "confidence")


def test_learning_signal_is_observational():
    signal = LearningSignal(
        "case-01",
        "machine-01",
        "ROOT_CAUSE",
        "cause-01",
        "REFUTED",
    )

    assert signal.outcome == "REFUTED"
    assert signal.signal_type == "ROOT_CAUSE"


def test_original_evidence_is_not_mutated():
    evidence = {
        "relationships": [
            {"type": "RESOURCE_INTERACTION"}
        ]
    }

    signal = LearningSignal(
        "case-01",
        "machine-01",
        "ROOT_CAUSE",
        "cause-01",
        "CONFIRMED",
        evidence=evidence,
    )

    evidence["relationships"][0]["type"] = "CHANGED"

    assert (
        signal.evidence["relationships"][0]["type"]
        == "RESOURCE_INTERACTION"
    )
