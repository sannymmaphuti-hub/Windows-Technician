import pytest

from engine.confidence import Confidence


def test_confidence_can_be_created():

    confidence = Confidence(
        subject="MEMORY_INTENSIVE_PROCESS",
        level="MEDIUM",
        explanation="Available evidence provides moderate support.",
    )

    assert confidence.subject == "MEMORY_INTENSIVE_PROCESS"
    assert confidence.level == "MEDIUM"
    assert confidence.explanation == (
        "Available evidence provides moderate support."
    )


def test_confidence_requires_subject():

    with pytest.raises(ValueError):
        Confidence(
            subject="",
            level="MEDIUM",
            explanation="Some explanation.",
        )


def test_confidence_requires_level():

    with pytest.raises(ValueError):
        Confidence(
            subject="MEMORY_INTENSIVE_PROCESS",
            level="",
            explanation="Some explanation.",
        )


def test_confidence_requires_explanation():

    with pytest.raises(ValueError):
        Confidence(
            subject="MEMORY_INTENSIVE_PROCESS",
            level="MEDIUM",
            explanation="",
        )


def test_confidence_rejects_invalid_level():

    with pytest.raises(ValueError):
        Confidence(
            subject="MEMORY_INTENSIVE_PROCESS",
            level="CERTAIN",
            explanation="Some explanation.",
        )


def test_confidence_accepts_low_medium_and_high():

    for level in {"LOW", "MEDIUM", "HIGH"}:

        confidence = Confidence(
            subject="MEMORY_INTENSIVE_PROCESS",
            level=level,
            explanation="Some explanation.",
        )

        assert confidence.level == level


def test_confidence_exports_evidence():

    confidence = Confidence(
        subject="MEMORY_INTENSIVE_PROCESS",
        level="MEDIUM",
        explanation="Available evidence provides moderate support.",
    )

    evidence = confidence.to_evidence()

    assert evidence == {
        "subject": "MEMORY_INTENSIVE_PROCESS",
        "level": "MEDIUM",
        "explanation": (
            "Available evidence provides moderate support."
        ),
    }


def test_confidence_does_not_claim_probability():

    confidence = Confidence(
        subject="MEMORY_INTENSIVE_PROCESS",
        level="MEDIUM",
        explanation="Available evidence provides moderate support.",
    )

    assert not hasattr(confidence, "probability")
    assert not hasattr(confidence, "percentage")


def test_confidence_does_not_claim_root_cause():

    confidence = Confidence(
        subject="MEMORY_INTENSIVE_PROCESS",
        level="MEDIUM",
        explanation="Available evidence provides moderate support.",
    )

    assert not hasattr(confidence, "primary_cause")
    assert not hasattr(confidence, "selected")