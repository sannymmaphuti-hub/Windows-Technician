import pytest

from engine.recommendation import Recommendation
from engine.recommendation_engine import RecommendationEngine
from engine.recommendation_rule import RecommendationRule


class MatchingRecommendationRule(RecommendationRule):

    def matches(self, finding):
        return True

    def create_recommendation(self, finding):
        return Recommendation(
            recommendation_type="REVIEW_MEMORY",
            category="MEMORY",
            priority="MEDIUM",
            description="Review memory-intensive processes.",
            rationale="High memory pressure was detected.",
        )


class NonMatchingRecommendationRule(RecommendationRule):

    def matches(self, finding):
        return False

    def create_recommendation(self, finding):
        return Recommendation(
            recommendation_type="DO_NOTHING",
            category="MEMORY",
            priority="LOW",
            description="No action is recommended.",
            rationale="The rule should not match.",
        )


def test_engine_can_be_created():
    engine = RecommendationEngine()

    assert engine is not None


def test_engine_starts_with_no_rules():
    engine = RecommendationEngine()

    assert engine._rules == []


def test_engine_registers_recommendation_rule():
    engine = RecommendationEngine()
    rule = MatchingRecommendationRule()

    engine.register_rule(rule)

    assert engine._rules == [rule]


def test_engine_rejects_non_recommendation_rule():
    engine = RecommendationEngine()

    with pytest.raises(ValueError):
        engine.register_rule(object())


def test_engine_returns_matching_recommendations():
    engine = RecommendationEngine()
    engine.register_rule(MatchingRecommendationRule())

    recommendations = engine.evaluate(None)

    assert len(recommendations) == 1
    assert isinstance(recommendations[0], Recommendation)
    assert recommendations[0].recommendation_type == "REVIEW_MEMORY"


def test_engine_does_not_return_non_matching_recommendations():
    engine = RecommendationEngine()
    engine.register_rule(NonMatchingRecommendationRule())

    recommendations = engine.evaluate(None)

    assert recommendations == []


def test_engine_evaluates_all_registered_rules():
    engine = RecommendationEngine()

    first_rule = MatchingRecommendationRule()
    second_rule = MatchingRecommendationRule()

    engine.register_rule(first_rule)
    engine.register_rule(second_rule)

    recommendations = engine.evaluate(None)

    assert len(recommendations) == 2


def test_engine_preserves_recommendation_objects():
    recommendation = Recommendation(
        recommendation_type="REVIEW_MEMORY",
        category="MEMORY",
        priority="MEDIUM",
        description="Review memory-intensive processes.",
        rationale="High memory pressure was detected.",
    )

    class ExistingRecommendationRule(RecommendationRule):

        def matches(self, finding):
            return True

        def create_recommendation(self, finding):
            return recommendation

    engine = RecommendationEngine()
    engine.register_rule(ExistingRecommendationRule())

    recommendations = engine.evaluate(None)

    assert recommendations[0] is recommendation


def test_engine_returns_empty_list_when_no_rules_match():
    engine = RecommendationEngine()

    engine.register_rule(NonMatchingRecommendationRule())

    assert engine.evaluate(None) == []

def test_engine_preserves_legacy_cpu_recommendations():

    engine = RecommendationEngine()

    findings = [
        {
            "category": "CPU",
            "severity": "WARNING",
        },
        {
            "category": "CPU",
            "severity": "CRITICAL",
        },
    ]

    recommendations = engine.get_recommendations(findings)

    assert len(recommendations) == 2

    assert recommendations[0]["category"] == "CPU"
    assert recommendations[0]["severity"] == "WARNING"

    assert recommendations[1]["category"] == "CPU"
    assert recommendations[1]["severity"] == "CRITICAL"


def test_engine_preserves_legacy_storage_recommendations():

    engine = RecommendationEngine()

    findings = [
        {
            "category": "STORAGE",
            "severity": "WARNING",
        },
        {
            "category": "STORAGE",
            "severity": "CRITICAL",
        },
    ]

    recommendations = engine.get_recommendations(findings)

    assert len(recommendations) == 2

    assert recommendations[0]["category"] == "STORAGE"
    assert recommendations[1]["category"] == "STORAGE"


def test_engine_legacy_recommendations_require_supported_severity():

    engine = RecommendationEngine()

    findings = [
        {
            "category": "CPU",
            "severity": "INFO",
        }
    ]

    recommendations = engine.get_recommendations(findings)

    assert recommendations == []

def test_engine_ignores_unsupported_legacy_category_without_failing():

    engine = RecommendationEngine()

    findings = [
        {
            "category": "GPU",
            "severity": "WARNING",
        }
    ]

    recommendations = engine.get_recommendations(findings)

    assert recommendations == []


def test_engine_preserves_supported_legacy_categories_when_unsupported_category_exists():

    engine = RecommendationEngine()

    findings = [
        {
            "category": "GPU",
            "severity": "WARNING",
        },
        {
            "category": "CPU",
            "severity": "WARNING",
        },
    ]

    recommendations = engine.get_recommendations(findings)

    assert len(recommendations) == 1
    assert recommendations[0]["category"] == "CPU"
    assert recommendations[0]["severity"] == "WARNING"