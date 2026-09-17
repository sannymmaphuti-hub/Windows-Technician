from abc import ABC

import pytest

from engine.recommendation_rule import RecommendationRule


def test_recommendation_rule_is_abstract():
    assert issubclass(RecommendationRule, ABC)


def test_recommendation_rule_requires_matches():
    with pytest.raises(TypeError):
        RecommendationRule()


def test_recommendation_rule_requires_create_recommendation():
    class IncompleteRecommendationRule(RecommendationRule):

        def matches(self, finding):
            return True

    with pytest.raises(TypeError):
        IncompleteRecommendationRule()


def test_complete_recommendation_rule_can_be_created():
    class TestRecommendationRule(RecommendationRule):

        def matches(self, finding):
            return True

        def create_recommendation(self, finding):
            return None

    rule = TestRecommendationRule()

    assert rule.matches(None) is True
    assert rule.create_recommendation(None) is None