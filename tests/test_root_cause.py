# ==========================================
# Windows Technician v0.5
# ROOT CAUSE CANDIDATE TESTS
# ==========================================

import pytest

from engine.root_cause import RootCauseCandidate


def test_root_cause_candidate_creation():

    candidate = RootCauseCandidate(
        cause="Application-driven memory pressure",
        category="MEMORY",
        confidence=0.91,
        evidence=[
            "Memory usage: 92%",
            "Chrome using 1.7 GB"
        ],
        reason="Multiple applications are consuming most available memory."
    )

    assert candidate.cause == (
        "Application-driven memory pressure"
    )

    assert candidate.category == "MEMORY"

    assert candidate.confidence == 0.91

    assert candidate.confidence_level() == "HIGH"


def test_root_cause_candidate_to_dict():

    candidate = RootCauseCandidate(
        cause="Insufficient physical RAM",
        category="MEMORY",
        confidence=0.76
    )

    result = candidate.to_dict()

    assert result["cause"] == (
        "Insufficient physical RAM"
    )

    assert result["category"] == "MEMORY"

    assert result["confidence"] == 0.76

    assert result["confidence_level"] == "MEDIUM"

    assert result["evidence"] == []

    assert result["reason"] == ""


def test_low_confidence():

    candidate = RootCauseCandidate(
        cause="Background process activity",
        category="PROCESS",
        confidence=0.35
    )

    assert candidate.confidence_level() == "LOW"


def test_invalid_confidence():

    with pytest.raises(ValueError):

        RootCauseCandidate(
            cause="Test cause",
            category="SYSTEM",
            confidence=1.5
        )


def test_negative_confidence():

    with pytest.raises(ValueError):

        RootCauseCandidate(
            cause="Test cause",
            category="SYSTEM",
            confidence=-0.1
        )


def test_empty_cause():

    with pytest.raises(ValueError):

        RootCauseCandidate(
            cause="",
            category="SYSTEM",
            confidence=0.50
        )


def test_invalid_evidence():

    with pytest.raises(ValueError):

        RootCauseCandidate(
            cause="Test cause",
            category="SYSTEM",
            confidence=0.50,
            evidence="not a list"
        )

