import pytest

from engine.finding import Finding
from engine.memory_recommendation_rule import MemoryRecommendationRule
from engine.recommendation import Recommendation
from engine.recommendation_rule import RecommendationRule


def create_memory_finding(severity="MEDIUM"):
    return Finding(
        finding_type="MEMORY_PRESSURE",
        category="MEMORY",
        severity=severity,
        description="System memory pressure is high.",
        supporting_signals=[],
    )


def test_memory_recommendation_rule_is_recommendation_rule():
    rule = MemoryRecommendationRule()

    assert isinstance(rule, RecommendationRule)


@pytest.mark.parametrize(
    "severity",
    ["LOW", "MEDIUM", "HIGH", "CRITICAL"],
)
def test_rule_matches_memory_pressure(severity):
    rule = MemoryRecommendationRule()
    finding = create_memory_finding(severity)

    assert rule.matches(finding) is True


def test_rule_does_not_match_unrelated_finding():
    rule = MemoryRecommendationRule()

    finding = Finding(
        finding_type="CPU_PRESSURE",
        category="CPU",
        severity="HIGH",
        description="System CPU pressure is high.",
        supporting_signals=[],
    )

    assert rule.matches(finding) is False


def test_rule_rejects_non_finding_subject():
    rule = MemoryRecommendationRule()

    with pytest.raises(ValueError):
        rule.matches(None)


def test_rule_creates_memory_recommendation():
    rule = MemoryRecommendationRule()
    finding = create_memory_finding()

    recommendation = rule.create_recommendation(finding)

    assert isinstance(recommendation, Recommendation)
    assert recommendation.recommendation_type == "REVIEW_MEMORY"
    assert recommendation.category == "MEMORY"
    assert recommendation.description == (
        "Review memory-intensive processes."
    )


def test_memory_recommendation_has_rationale():
    rule = MemoryRecommendationRule()
    finding = create_memory_finding()

    recommendation = rule.create_recommendation(finding)

    assert recommendation.rationale == (
        "High memory pressure was detected."
    )


def test_memory_recommendation_priority_reflects_severity():
    rule = MemoryRecommendationRule()

    low = rule.create_recommendation(
        create_memory_finding("LOW")
    )
    medium = rule.create_recommendation(
        create_memory_finding("MEDIUM")
    )
    high = rule.create_recommendation(
        create_memory_finding("HIGH")
    )
    critical = rule.create_recommendation(
        create_memory_finding("CRITICAL")
    )

    assert low.priority == "LOW"
    assert medium.priority == "MEDIUM"
    assert high.priority == "HIGH"
    assert critical.priority == "CRITICAL"


def test_create_recommendation_rejects_non_finding_subject():
    rule = MemoryRecommendationRule()

    with pytest.raises(ValueError):
        rule.create_recommendation(None)