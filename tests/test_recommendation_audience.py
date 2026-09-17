import pytest

from engine.finding import Finding
from engine.recommendation import Recommendation
from engine.recommendation_rule import RecommendationRule
from engine.audience_recommendation_rule import (
    AudienceRecommendationRule,
)


def create_memory_finding():
    return Finding(
        finding_type="MEMORY_PRESSURE",
        category="MEMORY",
        severity="HIGH",
        description="System memory pressure is high.",
    )


def test_rule_is_recommendation_rule():
    rule = AudienceRecommendationRule()

    assert isinstance(rule, RecommendationRule)


def test_user_audience_matches_memory_finding():
    rule = AudienceRecommendationRule()

    finding = create_memory_finding()

    assert rule.matches(
        finding,
        "USER",
    ) is True


def test_technician_audience_matches_memory_finding():
    rule = AudienceRecommendationRule()

    finding = create_memory_finding()

    assert rule.matches(
        finding,
        "TECHNICIAN",
    ) is True


def test_rule_does_not_match_unsupported_audience():
    rule = AudienceRecommendationRule()

    finding = create_memory_finding()

    with pytest.raises(ValueError):
        rule.matches(
            finding,
            "ADMIN",
        )


def test_rule_rejects_invalid_finding():
    rule = AudienceRecommendationRule()

    with pytest.raises(ValueError):
        rule.matches(
            object(),
            "USER",
        )


def test_user_recommendation_is_created():
    rule = AudienceRecommendationRule()

    finding = create_memory_finding()

    recommendation = rule.create_recommendation(
        finding,
        "USER",
    )

    assert isinstance(recommendation, Recommendation)


def test_technician_recommendation_is_created():
    rule = AudienceRecommendationRule()

    finding = create_memory_finding()

    recommendation = rule.create_recommendation(
        finding,
        "TECHNICIAN",
    )

    assert isinstance(recommendation, Recommendation)


def test_user_recommendation_uses_plain_language():
    rule = AudienceRecommendationRule()

    finding = create_memory_finding()

    recommendation = rule.create_recommendation(
        finding,
        "USER",
    )

    assert (
        "memory" in recommendation.description.lower()
    )


def test_user_recommendation_is_action_oriented():
    rule = AudienceRecommendationRule()

    finding = create_memory_finding()

    recommendation = rule.create_recommendation(
        finding,
        "USER",
    )

    assert any(
        word in recommendation.description.lower()
        for word in (
            "review",
            "check",
            "close",
            "look",
        )
    )


def test_technician_recommendation_contains_technical_context():
    rule = AudienceRecommendationRule()

    finding = create_memory_finding()

    recommendation = rule.create_recommendation(
        finding,
        "TECHNICIAN",
    )

    assert any(
        term in recommendation.description.lower()
        for term in (
            "process",
            "memory pressure",
            "usage",
        )
    )


def test_user_and_technician_recommendations_differ():
    rule = AudienceRecommendationRule()

    finding = create_memory_finding()

    user_recommendation = rule.create_recommendation(
        finding,
        "USER",
    )

    technician_recommendation = (
        rule.create_recommendation(
            finding,
            "TECHNICIAN",
        )
    )

    assert (
        user_recommendation.description
        != technician_recommendation.description
    )


def test_audience_does_not_change_recommendation_category():
    rule = AudienceRecommendationRule()

    finding = create_memory_finding()

    user_recommendation = rule.create_recommendation(
        finding,
        "USER",
    )

    technician_recommendation = (
        rule.create_recommendation(
            finding,
            "TECHNICIAN",
        )
    )

    assert user_recommendation.category == "MEMORY"
    assert technician_recommendation.category == "MEMORY"


def test_audience_does_not_change_priority():
    rule = AudienceRecommendationRule()

    finding = create_memory_finding()

    user_recommendation = rule.create_recommendation(
        finding,
        "USER",
    )

    technician_recommendation = (
        rule.create_recommendation(
            finding,
            "TECHNICIAN",
        )
    )

    assert user_recommendation.priority == "HIGH"
    assert technician_recommendation.priority == "HIGH"


def test_create_recommendation_rejects_invalid_audience():
    rule = AudienceRecommendationRule()

    finding = create_memory_finding()

    with pytest.raises(ValueError):
        rule.create_recommendation(
            finding,
            "ADMIN",
        )


def test_create_recommendation_rejects_invalid_finding():
    rule = AudienceRecommendationRule()

    with pytest.raises(ValueError):
        rule.create_recommendation(
            object(),
            "USER",
        )