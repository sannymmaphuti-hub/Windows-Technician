import pytest

from engine.confidence import Confidence
from engine.recommendation import Recommendation
from engine.recommendation_rule import RecommendationRule
from engine.root_cause_candidate import RootCauseCandidate
from engine.confidence_aware_recommendation_rule import (
    ConfidenceAwareRecommendationRule,
)


def create_candidate():
    return RootCauseCandidate(
        cause_type="MEMORY_INTENSIVE_PROCESS",
        category="MEMORY",
        explanation=(
            "A memory-intensive process may be contributing."
        ),
    )


def create_confidence(level):
    return Confidence(
        subject="MEMORY_INTENSIVE_PROCESS",
        level=level,
        explanation=(
            f"Confidence is {level}."
        ),
    )


def test_rule_is_recommendation_rule():
    rule = ConfidenceAwareRecommendationRule()

    assert isinstance(rule, RecommendationRule)


@pytest.mark.parametrize(
    "level",
    ["LOW", "MEDIUM", "HIGH"],
)
def test_rule_matches_valid_confidence(level):
    rule = ConfidenceAwareRecommendationRule()
    candidate = create_candidate()
    confidence = create_confidence(level)

    assert rule.matches(
        candidate,
        [confidence],
    ) is True


def test_rule_does_not_match_unrelated_confidence():
    rule = ConfidenceAwareRecommendationRule()
    candidate = create_candidate()

    confidence = Confidence(
        subject="MEMORY_LEAK",
        level="HIGH",
        explanation="Another cause.",
    )

    assert rule.matches(
        candidate,
        [confidence],
    ) is False


def test_rule_rejects_invalid_candidate():
    rule = ConfidenceAwareRecommendationRule()

    with pytest.raises(ValueError):
        rule.matches(None, [])


def test_rule_rejects_invalid_evidence():
    rule = ConfidenceAwareRecommendationRule()
    candidate = create_candidate()

    with pytest.raises(ValueError):
        rule.matches(candidate, None)


def test_high_confidence_creates_review_recommendation():
    rule = ConfidenceAwareRecommendationRule()
    candidate = create_candidate()
    confidence = create_confidence("HIGH")

    recommendation = rule.create_recommendation(
        candidate,
        [confidence],
    )

    assert isinstance(recommendation, Recommendation)
    assert recommendation.recommendation_type == (
        "REVIEW_MEMORY_PROCESS"
    )
    assert recommendation.category == "MEMORY"
    assert recommendation.priority == "HIGH"


def test_medium_confidence_creates_cautious_recommendation():
    rule = ConfidenceAwareRecommendationRule()
    candidate = create_candidate()
    confidence = create_confidence("MEDIUM")

    recommendation = rule.create_recommendation(
        candidate,
        [confidence],
    )

    assert recommendation.recommendation_type == (
        "INVESTIGATE_MEMORY_PROCESS"
    )
    assert recommendation.category == "MEMORY"
    assert recommendation.priority == "MEDIUM"


def test_low_confidence_recommends_more_evidence():
    rule = ConfidenceAwareRecommendationRule()
    candidate = create_candidate()
    confidence = create_confidence("LOW")

    recommendation = rule.create_recommendation(
        candidate,
        [confidence],
    )

    assert recommendation.recommendation_type == (
        "GATHER_MORE_EVIDENCE"
    )
    assert recommendation.priority == "LOW"


def test_low_confidence_does_not_recommend_direct_review():
    rule = ConfidenceAwareRecommendationRule()
    candidate = create_candidate()
    confidence = create_confidence("LOW")

    recommendation = rule.create_recommendation(
        candidate,
        [confidence],
    )

    assert recommendation.recommendation_type != (
        "REVIEW_MEMORY_PROCESS"
    )


def test_recommendation_rationale_reflects_confidence():
    rule = ConfidenceAwareRecommendationRule()
    candidate = create_candidate()
    confidence = create_confidence("MEDIUM")

    recommendation = rule.create_recommendation(
        candidate,
        [confidence],
    )

    assert "MEDIUM" in recommendation.rationale


def test_create_recommendation_rejects_missing_confidence():
    rule = ConfidenceAwareRecommendationRule()
    candidate = create_candidate()

    with pytest.raises(ValueError):
        rule.create_recommendation(
            candidate,
            [],
        )