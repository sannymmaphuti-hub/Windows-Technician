import pytest

from engine.correlation_engine import CorrelationEngine
from engine.correlation_rule import CorrelationRule
from engine.finding import Finding


class DummyCorrelationRule(CorrelationRule):

    def __init__(self, should_match=True):
        self.should_match = should_match

    def matches(self, findings):
        return self.should_match

    def create_correlation(self, findings):
        return "correlation"


def create_finding():
    return Finding(
        finding_type="MEMORY_PRESSURE",
        category="MEMORY",
        severity="HIGH",
        description="System memory pressure is high.",
    )


def test_correlation_engine_can_be_created():
    engine = CorrelationEngine()

    assert engine is not None


def test_correlation_engine_rejects_invalid_rule():
    engine = CorrelationEngine()

    with pytest.raises(ValueError):
        engine.register_rule("not a correlation rule")


def test_correlation_engine_accepts_correlation_rule():
    engine = CorrelationEngine()
    rule = DummyCorrelationRule()

    engine.register_rule(rule)

    assert rule in engine._rules


def test_correlation_engine_returns_no_correlations_when_no_rule_matches():
    engine = CorrelationEngine()
    engine.register_rule(DummyCorrelationRule(should_match=False))

    findings = [create_finding()]

    correlations = engine.detect(findings)

    assert correlations == []


def test_correlation_engine_creates_correlation_when_rule_matches():
    engine = CorrelationEngine()
    engine.register_rule(DummyCorrelationRule())

    findings = [create_finding()]

    correlations = engine.detect(findings)

    assert correlations == ["correlation"]


def test_correlation_engine_can_create_multiple_correlations():
    engine = CorrelationEngine()

    engine.register_rule(DummyCorrelationRule())
    engine.register_rule(DummyCorrelationRule())

    findings = [create_finding()]

    correlations = engine.detect(findings)

    assert correlations == ["correlation", "correlation"]


def test_correlation_engine_passes_findings_to_rule():
    received = []

    class RecordingCorrelationRule(CorrelationRule):

        def matches(self, findings):
            received.append(findings)
            return False

        def create_correlation(self, findings):
            return "correlation"

    engine = CorrelationEngine()
    engine.register_rule(RecordingCorrelationRule())

    findings = [create_finding()]

    engine.detect(findings)

    assert received[0] is findings