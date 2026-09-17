import pytest

from engine.confidence_engine import ConfidenceEngine
from engine.confidence_rule import ConfidenceRule


def test_confidence_engine_can_be_created():

    engine = ConfidenceEngine()

    assert engine is not None


def test_confidence_engine_starts_without_rules():

    engine = ConfidenceEngine()

    assert engine._rules == []


def test_confidence_engine_rejects_invalid_rule():

    engine = ConfidenceEngine()

    with pytest.raises(ValueError):
        engine.register_rule(object())


def test_confidence_engine_accepts_confidence_rule():

    class TestConfidenceRule(ConfidenceRule):

        def matches(self, subject, evidence):
            return False

        def create_confidence(self, subject, evidence):
            return None

    engine = ConfidenceEngine()
    rule = TestConfidenceRule()

    engine.register_rule(rule)

    assert engine._rules == [rule]


def test_confidence_engine_returns_no_confidence_when_no_rule_matches():

    class TestConfidenceRule(ConfidenceRule):

        def matches(self, subject, evidence):
            return False

        def create_confidence(self, subject, evidence):
            return "confidence"

    engine = ConfidenceEngine()
    engine.register_rule(TestConfidenceRule())

    result = engine.evaluate(
        subject="MEMORY_INTENSIVE_PROCESS",
        evidence=[],
    )

    assert result == []


def test_confidence_engine_creates_confidence_when_rule_matches():

    class TestConfidenceRule(ConfidenceRule):

        def matches(self, subject, evidence):
            return True

        def create_confidence(self, subject, evidence):
            return "confidence"

    engine = ConfidenceEngine()
    engine.register_rule(TestConfidenceRule())

    result = engine.evaluate(
        subject="MEMORY_INTENSIVE_PROCESS",
        evidence=[],
    )

    assert result == ["confidence"]


def test_confidence_engine_can_generate_multiple_confidences():

    class FirstRule(ConfidenceRule):

        def matches(self, subject, evidence):
            return True

        def create_confidence(self, subject, evidence):
            return "first"

    class SecondRule(ConfidenceRule):

        def matches(self, subject, evidence):
            return True

        def create_confidence(self, subject, evidence):
            return "second"

    engine = ConfidenceEngine()

    engine.register_rule(FirstRule())
    engine.register_rule(SecondRule())

    result = engine.evaluate(
        subject="MEMORY_INTENSIVE_PROCESS",
        evidence=[],
    )

    assert result == [
        "first",
        "second",
    ]


def test_confidence_engine_passes_subject_to_rule():

    received = {}

    class TestConfidenceRule(ConfidenceRule):

        def matches(self, subject, evidence):
            received["subject"] = subject
            return False

        def create_confidence(self, subject, evidence):
            return None

    engine = ConfidenceEngine()
    engine.register_rule(TestConfidenceRule())

    engine.evaluate(
        subject="MEMORY_INTENSIVE_PROCESS",
        evidence=[],
    )

    assert received["subject"] == "MEMORY_INTENSIVE_PROCESS"


def test_confidence_engine_passes_evidence_to_rule():

    evidence = ["evidence"]
    received = {}

    class TestConfidenceRule(ConfidenceRule):

        def matches(self, subject, incoming_evidence):
            received["evidence"] = incoming_evidence
            return False

        def create_confidence(self, subject, incoming_evidence):
            return None

    engine = ConfidenceEngine()
    engine.register_rule(TestConfidenceRule())

    engine.evaluate(
        subject="MEMORY_INTENSIVE_PROCESS",
        evidence=evidence,
    )

    assert received["evidence"] is evidence