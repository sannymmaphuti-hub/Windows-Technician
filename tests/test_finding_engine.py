from engine.finding_engine import FindingEngine
from engine.finding_rule import FindingRule
from engine.signal import Signal


class DummyFindingRule(FindingRule):

    def __init__(self, signal_type, finding_type):
        self.signal_type = signal_type
        self.finding_type = finding_type

    def matches(self, signal):
        return signal.signal_type == self.signal_type

    def create_finding(self, signal):
        from engine.finding import Finding

        return Finding(
            finding_type=self.finding_type,
            category="TEST",
            severity="LOW",
            description="Test finding.",
            supporting_signals=[signal],
        )


def create_signal(signal_type):
    return Signal(
        signal_type=signal_type,
        source="test",
        subject="test_subject",
        attribute="test_attribute",
        value=1,
    )


def test_engine_can_be_created():
    engine = FindingEngine()

    assert engine is not None


def test_engine_can_register_a_finding_rule():
    engine = FindingEngine()
    rule = DummyFindingRule("TEST_SIGNAL", "TEST_FINDING")

    engine.register_rule(rule)

    signal = create_signal("TEST_SIGNAL")

    findings = engine.detect(signal)

    assert len(findings) == 1
    assert findings[0].finding_type == "TEST_FINDING"


def test_engine_returns_no_findings_when_no_rule_matches():
    engine = FindingEngine()

    engine.register_rule(
        DummyFindingRule("OTHER_SIGNAL", "OTHER_FINDING")
    )

    signal = create_signal("TEST_SIGNAL")

    findings = engine.detect(signal)

    assert findings == []


def test_engine_can_create_multiple_findings():
    engine = FindingEngine()

    engine.register_rule(
        DummyFindingRule("TEST_SIGNAL", "FINDING_ONE")
    )

    engine.register_rule(
        DummyFindingRule("TEST_SIGNAL", "FINDING_TWO")
    )

    signal = create_signal("TEST_SIGNAL")

    findings = engine.detect(signal)

    assert len(findings) == 2

    finding_types = {
        finding.finding_type
        for finding in findings
    }

    assert finding_types == {
        "FINDING_ONE",
        "FINDING_TWO",
    }


def test_engine_rejects_invalid_rule():
    engine = FindingEngine()

    try:
        engine.register_rule("not-a-rule")
    except ValueError:
        pass
    else:
        raise AssertionError(
            "FindingEngine should reject invalid rules."
        )


def test_engine_preserves_created_findings():
    engine = FindingEngine()

    engine.register_rule(
       DummyFindingRule("TEST_SIGNAL", "TEST_FINDING")
    )

    signal = create_signal("TEST_SIGNAL")

    findings = engine.detect(signal)

    assert findings[0].supporting_signals == [signal]