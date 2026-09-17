import pytest

from engine.correlation_rule import CorrelationRule


def test_correlation_rule_requires_matches_implementation():
    with pytest.raises(TypeError):
        CorrelationRule()


def test_correlation_rule_requires_create_correlation_implementation():
    class MatchesOnlyRule(CorrelationRule):

        def matches(self, findings):
            return True

    with pytest.raises(TypeError):
        MatchesOnlyRule()


def test_correlation_rule_can_be_implemented():
    class DummyCorrelationRule(CorrelationRule):

        def matches(self, findings):
            return True

        def create_correlation(self, findings):
            return "correlation"

    rule = DummyCorrelationRule()

    assert rule.matches([]) is True
    assert rule.create_correlation([]) == "correlation"