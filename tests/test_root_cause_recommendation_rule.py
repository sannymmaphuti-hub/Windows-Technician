import pytest

from engine.finding import Finding
from engine.recommendation import Recommendation
from engine.recommendation_rule import RecommendationRule
from engine.root_cause_candidate import RootCauseCandidate
from engine.root_cause_evaluation import RootCauseEvaluation
from engine.root_cause_recommendation_rule import (
    RootCauseRecommendationRule,
)


def create_candidate():
    return RootCauseCandidate(
        cause_type="MEMORY_INTENSIVE_PROCESS",
        category="MEMORY",
        explanation=(
            "A memory-intensive process may be contributing."
        ),
    )


def create_finding():
    return Finding(
        finding_type="MEMORY_PRESSURE",
        category="MEMORY",
        severity="HIGH",
        description="System memory pressure is high.",
        supporting_signals=[],
    )


def create_evaluation(candidate, assessment="SUPPORTED"):
    return RootCauseEvaluation(
        candidate=candidate,
        supporting_evidence=[],
        assessment=assessment,
        explanation="Evidence supports the possible cause.",
    )


def test_root_cause_recommendation_rule_is_recommendation_rule():
    rule = RootCauseRecommendationRule()

    assert isinstance(rule, RecommendationRule)


def test_rule_matches_supported_memory_process_cause():
    rule = RootCauseRecommendationRule()
    candidate = create_candidate()
    finding = create_finding()
    evaluation = create_evaluation(candidate)

    assert rule.matches(
        candidate,
        [evaluation, finding],
    ) is True


def test_rule_matches_strongly_supported_memory_process_cause():
    rule = RootCauseRecommendationRule()
    candidate = create_candidate()
    finding = create_finding()
    evaluation = create_evaluation(
        candidate,
        "STRONGLY_SUPPORTED",
    )

    assert rule.matches(
        candidate,
        [evaluation, finding],
    ) is True


def test_rule_does_not_match_insufficient_cause():
    rule = RootCauseRecommendationRule()
    candidate = create_candidate()
    finding = create_finding()
    evaluation = create_evaluation(
        candidate,
        "INSUFFICIENT",
    )

    assert rule.matches(
        candidate,
        [evaluation, finding],
    ) is False


def test_rule_does_not_match_unrelated_candidate():
    rule = RootCauseRecommendationRule()

    candidate = RootCauseCandidate(
        cause_type="MEMORY_LEAK",
        category="MEMORY",
        explanation="A memory leak may be contributing.",
    )

    target_candidate = create_candidate()
    evaluation = create_evaluation(target_candidate)

    assert rule.matches(
        candidate,
        [evaluation],
    ) is False


def test_rule_creates_process_review_recommendation():
    rule = RootCauseRecommendationRule()
    candidate = create_candidate()
    evaluation = create_evaluation(candidate)

    recommendation = rule.create_recommendation(
        candidate,
        [evaluation],
    )

    assert isinstance(recommendation, Recommendation)
    assert recommendation.recommendation_type == (
        "REVIEW_MEMORY_PROCESS"
    )
    assert recommendation.category == "MEMORY"
    assert recommendation.description == (
        "Review the memory-intensive process."
    )


def test_rule_rejects_invalid_candidate():
    rule = RootCauseRecommendationRule()

    with pytest.raises(ValueError):
        rule.matches(None, [])


def test_rule_rejects_invalid_evidence():
    rule = RootCauseRecommendationRule()
    candidate = create_candidate()

    with pytest.raises(ValueError):
        rule.matches(candidate, None)


def test_recommendation_rationale_mentions_root_cause():
    rule = RootCauseRecommendationRule()
    candidate = create_candidate()
    evaluation = create_evaluation(candidate)

    recommendation = rule.create_recommendation(
        candidate,
        [evaluation],
    )

    assert "memory-intensive process" in (
        recommendation.rationale.lower()
    )


def test_recommendation_priority_reflects_assessment():
    rule = RootCauseRecommendationRule()
    candidate = create_candidate()

    supported = rule.create_recommendation(
        candidate,
        [create_evaluation(candidate, "SUPPORTED")],
    )

    strongly_supported = rule.create_recommendation(
        candidate,
        [
            create_evaluation(
                candidate,
                "STRONGLY_SUPPORTED",
            )
        ],
    )

    assert supported.priority == "MEDIUM"
    assert strongly_supported.priority == "HIGH"