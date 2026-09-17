import pytest

from engine.confidence_rule import ConfidenceRule


def test_confidence_rule_is_abstract():

    with pytest.raises(TypeError):
        ConfidenceRule()


def test_confidence_rule_requires_matches_implementation():

    class IncompleteRule(ConfidenceRule):

        def create_confidence(self, subject, evidence):
            return None

    with pytest.raises(TypeError):
        IncompleteRule()


def test_confidence_rule_requires_create_confidence_implementation():

    class IncompleteRule(ConfidenceRule):

        def matches(self, subject, evidence):
            return True

    with pytest.raises(TypeError):
        IncompleteRule()


def test_confidence_rule_can_be_implemented():

    class TestConfidenceRule(ConfidenceRule):

        def matches(self, subject, evidence):
            return True

        def create_confidence(self, subject, evidence):
            return "confidence"

    rule = TestConfidenceRule()

    assert rule.matches("MEMORY_PRESSURE", []) is True
    assert rule.create_confidence("MEMORY_PRESSURE", []) == "confidence"


def test_confidence_rule_receives_subject():

    received = {}

    class TestConfidenceRule(ConfidenceRule):

        def matches(self, subject, evidence):
            received["subject"] = subject
            return False

        def create_confidence(self, subject, evidence):
            return None

    rule = TestConfidenceRule()

    rule.matches("MEMORY_INTENSIVE_PROCESS", [])

    assert received["subject"] == "MEMORY_INTENSIVE_PROCESS"


def test_confidence_rule_receives_evidence():

    evidence = ["evidence"]

    received = {}

    class TestConfidenceRule(ConfidenceRule):

        def matches(self, subject, incoming_evidence):
            received["evidence"] = incoming_evidence
            return False

        def create_confidence(self, subject, incoming_evidence):
            return None

    rule = TestConfidenceRule()

    rule.matches("MEMORY_INTENSIVE_PROCESS", evidence)

    assert received["evidence"] is evidence


def test_confidence_rule_does_not_select_primary_cause():

    class TestConfidenceRule(ConfidenceRule):

        def matches(self, subject, evidence):
            return True

        def create_confidence(self, subject, evidence):
            return "confidence"

    rule = TestConfidenceRule()

    assert not hasattr(rule, "primary_cause")
    assert not hasattr(rule, "selected")


def test_confidence_rule_does_not_calculate_probability():

    class TestConfidenceRule(ConfidenceRule):

        def matches(self, subject, evidence):
            return True

        def create_confidence(self, subject, evidence):
            return "confidence"

    rule = TestConfidenceRule()

    assert not hasattr(rule, "probability")
    assert not hasattr(rule, "percentage")