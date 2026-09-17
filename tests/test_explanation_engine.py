from engine.explanation_engine import ExplanationEngine
from engine.explanation_rule import ExplanationRule


class FakeExplanationRule(ExplanationRule):

    def __init__(self, subject, result):
        self.subject = subject
        self.result = result

    def matches(self, subject, evidence):
        return subject == self.subject

    def create_explanation(self, subject, evidence):
        return self.result


def test_engine_can_be_created():
    engine = ExplanationEngine()

    assert engine is not None


def test_engine_starts_with_no_rules():
    engine = ExplanationEngine()

    assert engine._rules == []


def test_engine_can_register_rule():
    engine = ExplanationEngine()
    rule = FakeExplanationRule(
        "MEMORY_PRESSURE",
        "memory explanation",
    )

    engine.register_rule(rule)

    assert engine._rules == [rule]


def test_engine_rejects_invalid_rule():
    engine = ExplanationEngine()

    try:
        engine.register_rule(object())
    except ValueError:
        return

    assert False


def test_engine_evaluates_matching_rule():
    engine = ExplanationEngine()

    rule = FakeExplanationRule(
        "MEMORY_PRESSURE",
        "memory explanation",
    )

    engine.register_rule(rule)

    explanations = engine.evaluate(
        "MEMORY_PRESSURE",
        [],
    )

    assert explanations == ["memory explanation"]


def test_engine_ignores_non_matching_rule():
    engine = ExplanationEngine()

    rule = FakeExplanationRule(
        "MEMORY_PRESSURE",
        "memory explanation",
    )

    engine.register_rule(rule)

    explanations = engine.evaluate(
        "CPU_PRESSURE",
        [],
    )

    assert explanations == []


def test_engine_evaluates_multiple_matching_rules():
    engine = ExplanationEngine()

    first_rule = FakeExplanationRule(
        "MEMORY_PRESSURE",
        "first explanation",
    )

    second_rule = FakeExplanationRule(
        "MEMORY_PRESSURE",
        "second explanation",
    )

    engine.register_rule(first_rule)
    engine.register_rule(second_rule)

    explanations = engine.evaluate(
        "MEMORY_PRESSURE",
        [],
    )

    assert explanations == [
        "first explanation",
        "second explanation",
    ]


def test_engine_preserves_rule_order():
    engine = ExplanationEngine()

    first_rule = FakeExplanationRule(
        "MEMORY_PRESSURE",
        "first",
    )

    second_rule = FakeExplanationRule(
        "MEMORY_PRESSURE",
        "second",
    )

    engine.register_rule(first_rule)
    engine.register_rule(second_rule)

    explanations = engine.evaluate(
        "MEMORY_PRESSURE",
        [],
    )

    assert explanations[0] == "first"
    assert explanations[1] == "second"


def test_engine_passes_evidence_to_rule():
    received = {}

    class EvidenceRule(ExplanationRule):

        def matches(self, subject, evidence):
            received["matches"] = evidence
            return True

        def create_explanation(self, subject, evidence):
            received["create"] = evidence
            return "explanation"

    engine = ExplanationEngine()
    engine.register_rule(EvidenceRule())

    evidence = ["MEMORY_PRESSURE"]

    engine.evaluate(
        "MEMORY_PRESSURE",
        evidence,
    )

    assert received["matches"] is evidence
    assert received["create"] is evidence