import pytest

from engine.finding import Finding
from engine.recommendation import Recommendation
from engine.recommendation_rule import RecommendationRule
from engine.risk_aware_recommendation_rule import (
    RiskAwareRecommendationRule,
)


def create_finding(severity):
    return Finding(
        finding_type="MEMORY_PRESSURE",
        category="MEMORY",
        severity=severity,
        description="System memory pressure is high.",
        supporting_signals=[],
    )


def test_rule_is_recommendation_rule():
    rule = RiskAwareRecommendationRule()

    assert isinstance(rule, RecommendationRule)


@pytest.mark.parametrize(
    "severity",
    ["LOW", "MEDIUM", "HIGH", "CRITICAL"],
)
def test_rule_matches_memory_pressure(severity):
    rule = RiskAwareRecommendationRule()

    assert rule.matches(create_finding(severity)) is True


def test_rule_does_not_match_unrelated_finding():
    rule = RiskAwareRecommendationRule()

    finding = Finding(
        finding_type="CPU_PRESSURE",
        category="CPU",
        severity="HIGH",
        description="System CPU pressure is high.",
        supporting_signals=[],
    )

    assert rule.matches(finding) is False


def test_rule_rejects_non_finding():
    rule = RiskAwareRecommendationRule()

    with pytest.raises(ValueError):
        rule.matches(None)


@pytest.mark.parametrize(
    "severity,expected_priority",
    [
        ("LOW", "LOW"),
        ("MEDIUM", "MEDIUM"),
        ("HIGH", "HIGH"),
        ("CRITICAL", "CRITICAL"),
    ],
)
def test_priority_reflects_severity(
    severity,
    expected_priority,
):
    rule = RiskAwareRecommendationRule()

    recommendation = rule.create_recommendation(
        create_finding(severity)
    )

    assert recommendation.priority == expected_priority


def test_low_severity_recommends_normal_review():
    rule = RiskAwareRecommendationRule()

    recommendation = rule.create_recommendation(
        create_finding("LOW")
    )

    assert isinstance(recommendation, Recommendation)
    assert recommendation.recommendation_type == (
        "REVIEW_MEMORY"
    )


def test_medium_severity_recommends_review():
    rule = RiskAwareRecommendationRule()

    recommendation = rule.create_recommendation(
        create_finding("MEDIUM")
    )

    assert recommendation.recommendation_type == (
        "REVIEW_MEMORY"
    )


def test_high_severity_recommends_priority_review():
    rule = RiskAwareRecommendationRule()

    recommendation = rule.create_recommendation(
        create_finding("HIGH")
    )

    assert recommendation.recommendation_type == (
        "PRIORITIZE_MEMORY_REVIEW"
    )


def test_critical_severity_recommends_careful_escalation():
    rule = RiskAwareRecommendationRule()

    recommendation = rule.create_recommendation(
        create_finding("CRITICAL")
    )

    assert recommendation.recommendation_type == (
        "ESCALATE_MEMORY_ISSUE"
    )


def test_critical_recommendation_does_not_perform_remediation():
    rule = RiskAwareRecommendationRule()

    recommendation = rule.create_recommendation(
        create_finding("CRITICAL")
    )

    assert recommendation.recommendation_type != (
        "REMEDIATE_MEMORY"
    )


def test_recommendation_contains_rationale():
    rule = RiskAwareRecommendationRule()

    recommendation = rule.create_recommendation(
        create_finding("HIGH")
    )

    assert recommendation.rationale
    assert "HIGH" in recommendation.rationale


def test_create_recommendation_rejects_non_finding():
    rule = RiskAwareRecommendationRule()

    with pytest.raises(ValueError):
        rule.create_recommendation(None)