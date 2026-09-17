import pytest

from engine.recommendation import Recommendation
from engine.recommendation_rule import RecommendationRule
from engine.root_cause_candidate import RootCauseCandidate
from engine.competing_recommendation_rule import (
    CompetingRecommendationRule,
)


def create_process_candidate():
    return RootCauseCandidate(
        cause_type="MEMORY_INTENSIVE_PROCESS",
        category="MEMORY",
        explanation=(
            "A memory-intensive process may be contributing."
        ),
    )


def create_leak_candidate():
    return RootCauseCandidate(
        cause_type="MEMORY_LEAK",
        category="MEMORY",
        explanation=(
            "A memory leak may be contributing."
        ),
    )


def test_rule_is_recommendation_rule():
    rule = CompetingRecommendationRule()

    assert isinstance(rule, RecommendationRule)


def test_rule_matches_multiple_candidates_without_primary():
    rule = CompetingRecommendationRule()

    candidates = [
        create_process_candidate(),
        create_leak_candidate(),
    ]

    assert rule.matches(
        candidates,
        None,
    ) is True


def test_rule_does_not_match_single_candidate():
    rule = CompetingRecommendationRule()

    candidates = [
        create_process_candidate(),
    ]

    assert rule.matches(
        candidates,
        None,
    ) is False


def test_rule_does_not_match_when_primary_exists():
    rule = CompetingRecommendationRule()

    candidates = [
        create_process_candidate(),
        create_leak_candidate(),
    ]

    primary = candidates[0]

    assert rule.matches(
        candidates,
        primary,
    ) is False


def test_rule_rejects_non_list_candidates():
    rule = CompetingRecommendationRule()

    with pytest.raises(ValueError):
        rule.matches(None, None)


def test_rule_rejects_invalid_candidate_objects():
    rule = CompetingRecommendationRule()

    with pytest.raises(ValueError):
        rule.matches(
            [object(), object()],
            None,
        )


def test_rule_creates_investigation_recommendation():
    rule = CompetingRecommendationRule()

    candidates = [
        create_process_candidate(),
        create_leak_candidate(),
    ]

    recommendation = rule.create_recommendation(
        candidates,
        None,
    )

    assert isinstance(recommendation, Recommendation)
    assert recommendation.recommendation_type == (
        "INVESTIGATE_COMPETING_CAUSES"
    )


def test_competing_recommendation_has_medium_priority():
    rule = CompetingRecommendationRule()

    candidates = [
        create_process_candidate(),
        create_leak_candidate(),
    ]

    recommendation = rule.create_recommendation(
        candidates,
        None,
    )

    assert recommendation.priority == "MEDIUM"


def test_competing_recommendation_uses_memory_category():
    rule = CompetingRecommendationRule()

    candidates = [
        create_process_candidate(),
        create_leak_candidate(),
    ]

    recommendation = rule.create_recommendation(
        candidates,
        None,
    )

    assert recommendation.category == "MEMORY"


def test_competing_recommendation_explains_uncertainty():
    rule = CompetingRecommendationRule()

    candidates = [
        create_process_candidate(),
        create_leak_candidate(),
    ]

    recommendation = rule.create_recommendation(
        candidates,
        None,
    )

    assert "possible causes" in (
        recommendation.description.lower()
    )


def test_competing_recommendation_does_not_select_a_cause():
    rule = CompetingRecommendationRule()

    candidates = [
        create_process_candidate(),
        create_leak_candidate(),
    ]

    recommendation = rule.create_recommendation(
        candidates,
        None,
    )

    assert "MEMORY_LEAK" not in recommendation.description
    assert "MEMORY_INTENSIVE_PROCESS" not in (
        recommendation.description
    )


def test_create_recommendation_rejects_single_candidate():
    rule = CompetingRecommendationRule()

    with pytest.raises(ValueError):
        rule.create_recommendation(
            [create_process_candidate()],
            None,
        )


def test_create_recommendation_rejects_primary_cause():
    rule = CompetingRecommendationRule()

    candidates = [
        create_process_candidate(),
        create_leak_candidate(),
    ]

    with pytest.raises(ValueError):
        rule.create_recommendation(
            candidates,
            candidates[0],
        )