import pytest

from engine.finding_rule import FindingRule


class TestFindingRule(FindingRule):

    def matches(self, signal):
        return signal == "MATCH"

    def create_finding(self, signal):
        return signal


def test_finding_rule_can_be_subclassed():
    rule = TestFindingRule()

    assert rule.matches("MATCH") is True


def test_finding_rule_can_create_a_finding():
    rule = TestFindingRule()

    assert rule.create_finding("MATCH") == "MATCH"


def test_finding_rule_requires_matches_implementation():
    class IncompleteRule(FindingRule):
        def create_finding(self, signal):
            return signal

    with pytest.raises(TypeError):
        IncompleteRule()


def test_finding_rule_requires_create_finding_implementation():
    class IncompleteRule(FindingRule):
        def matches(self, signal):
            return True

    with pytest.raises(TypeError):
        IncompleteRule()