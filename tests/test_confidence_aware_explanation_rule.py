import pytest

from engine.confidence import Confidence
from engine.explanation import Explanation
from engine.explanation_rule import ExplanationRule
from engine.root_cause_candidate import RootCauseCandidate
from engine.root_cause_explanation_rule import RootCauseExplanationRule


def create_candidate():
    return RootCauseCandidate(
        cause_type="MEMORY_INTENSIVE_PROCESS",
        category="MEMORY",
        explanation=(
            "A memory-intensive process may be contributing "
            "to the memory pressure."
        ),
    )


def create_confidence(candidate, level):
    return Confidence(
        subject=candidate.cause_type,
        level=level,
        explanation=(
            f"Confidence is {level} for this root cause."
        ),
    )


def test_confidence_aware_rule_can_be_created():
    from engine.confidence_aware_explanation_rule import (
        ConfidenceAwareExplanationRule,
    )

    rule = ConfidenceAwareExplanationRule()

    assert isinstance(rule, ExplanationRule)


def test_rule_requires_root_cause_candidate():
    from engine.confidence_aware_explanation_rule import (
        ConfidenceAwareExplanationRule,
    )

    rule = ConfidenceAwareExplanationRule()

    with pytest.raises(ValueError):
        rule.matches(
            "not a candidate",
            [],
        )


def test_rule_matches_candidate_with_confidence():
    from engine.confidence_aware_explanation_rule import (
        ConfidenceAwareExplanationRule,
    )

    candidate = create_candidate()
    confidence = create_confidence(candidate, "HIGH")

    rule = ConfidenceAwareExplanationRule()

    assert rule.matches(
        candidate,
        [confidence],
    )


def test_rule_does_not_match_candidate_without_confidence():
    from engine.confidence_aware_explanation_rule import (
        ConfidenceAwareExplanationRule,
    )

    candidate = create_candidate()

    rule = ConfidenceAwareExplanationRule()

    assert not rule.matches(
        candidate,
        [],
    )


def test_low_confidence_uses_uncertain_language():
    from engine.confidence_aware_explanation_rule import (
        ConfidenceAwareExplanationRule,
    )

    candidate = create_candidate()
    confidence = create_confidence(candidate, "LOW")

    rule = ConfidenceAwareExplanationRule()

    explanation = rule.create_explanation(
        candidate,
        [confidence],
    )

    assert isinstance(explanation, Explanation)

    text = (
        explanation.summary.lower()
        + " "
        + explanation.details.lower()
    )

    assert "possible" in text
    assert "not enough evidence" in text or "uncertain" in text


def test_medium_confidence_uses_supported_language():
    from engine.confidence_aware_explanation_rule import (
        ConfidenceAwareExplanationRule,
    )

    candidate = create_candidate()
    confidence = create_confidence(candidate, "MEDIUM")

    rule = ConfidenceAwareExplanationRule()

    explanation = rule.create_explanation(
        candidate,
        [confidence],
    )

    text = (
        explanation.summary.lower()
        + " "
        + explanation.details.lower()
    )

    assert "supports" in text
    assert "possible cause" in text


def test_high_confidence_uses_strong_language_without_absolute_certainty():
    from engine.confidence_aware_explanation_rule import (
        ConfidenceAwareExplanationRule,
    )

    candidate = create_candidate()
    confidence = create_confidence(candidate, "HIGH")

    rule = ConfidenceAwareExplanationRule()

    explanation = rule.create_explanation(
        candidate,
        [confidence],
    )

    text = (
        explanation.summary.lower()
        + " "
        + explanation.details.lower()
    )

    assert "strong" in text
    assert "likely" in text

    assert "definitely" not in text
    assert "guaranteed" not in text
    assert "this is certain" not in text


def test_explanation_preserves_confidence_level():
    from engine.confidence_aware_explanation_rule import (
        ConfidenceAwareExplanationRule,
    )

    candidate = create_candidate()
    confidence = create_confidence(candidate, "HIGH")

    rule = ConfidenceAwareExplanationRule()

    explanation = rule.create_explanation(
        candidate,
        [confidence],
    )

    assert explanation.confidence == "HIGH"


def test_rule_rejects_unrelated_confidence():
    from engine.confidence_aware_explanation_rule import (
        ConfidenceAwareExplanationRule,
    )

    candidate = create_candidate()

    unrelated_candidate = RootCauseCandidate(
        cause_type="MEMORY_LEAK",
        category="MEMORY",
        explanation="A possible memory leak.",
    )

    confidence = create_confidence(
        unrelated_candidate,
        "HIGH",
    )

    rule = ConfidenceAwareExplanationRule()

    assert not rule.matches(
        candidate,
        [confidence],
    )


def test_rule_does_not_mutate_confidence():
    from engine.confidence_aware_explanation_rule import (
        ConfidenceAwareExplanationRule,
    )

    candidate = create_candidate()
    confidence = create_confidence(candidate, "MEDIUM")

    original = confidence.to_evidence().copy()

    rule = ConfidenceAwareExplanationRule()

    rule.create_explanation(
        candidate,
        [confidence],
    )

    assert confidence.to_evidence() == original