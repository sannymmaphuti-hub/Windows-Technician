from engine.finding import Finding
from engine.root_cause_candidate import RootCauseCandidate
from engine.root_cause_engine import RootCauseEngine
from engine.root_cause_rule import RootCauseRule


def create_memory_finding():

    return Finding(
        finding_type="MEMORY_PRESSURE",
        category="MEMORY",
        severity="HIGH",
        description="System memory pressure is high.",
        supporting_signals=[],
    )


class MatchingRule(RootCauseRule):

    def matches(self, findings):
        return True

    def create_candidate(self, findings):
        return RootCauseCandidate(
            cause_type="TEST_CAUSE",
            category="TEST",
            explanation="A test cause may be involved.",
        )


class NonMatchingRule(RootCauseRule):

    def matches(self, findings):
        return False

    def create_candidate(self, findings):
        return RootCauseCandidate(
            cause_type="SHOULD_NOT_APPEAR",
            category="TEST",
            explanation="This candidate should not be created.",
        )


def test_root_cause_engine_can_be_created():

    engine = RootCauseEngine()

    assert engine is not None


def test_root_cause_engine_starts_without_rules():

    engine = RootCauseEngine()

    assert engine._rules == []


def test_root_cause_engine_rejects_invalid_rule():

    engine = RootCauseEngine()

    try:
        engine.register_rule(object())
        assert False
    except ValueError:
        assert True


def test_root_cause_engine_accepts_root_cause_rule():

    engine = RootCauseEngine()
    rule = MatchingRule()

    engine.register_rule(rule)

    assert engine._rules == [rule]


def test_root_cause_engine_returns_no_candidates_when_no_rule_matches():

    engine = RootCauseEngine()

    engine.register_rule(
        NonMatchingRule()
    )

    candidates = engine.detect(
        [create_memory_finding()]
    )

    assert candidates == []


def test_root_cause_engine_creates_candidate_when_rule_matches():

    engine = RootCauseEngine()

    engine.register_rule(
        MatchingRule()
    )

    candidates = engine.detect(
        [create_memory_finding()]
    )

    assert len(candidates) == 1
    assert isinstance(
        candidates[0],
        RootCauseCandidate,
    )


def test_root_cause_engine_can_generate_multiple_candidates():

    class SecondMatchingRule(RootCauseRule):

        def matches(self, findings):
            return True

        def create_candidate(self, findings):
            return RootCauseCandidate(
                cause_type="SECOND_TEST_CAUSE",
                category="TEST",
                explanation="Another possible cause.",
            )

    engine = RootCauseEngine()

    engine.register_rule(MatchingRule())
    engine.register_rule(SecondMatchingRule())

    candidates = engine.detect(
        [create_memory_finding()]
    )

    assert len(candidates) == 2

    assert candidates[0].cause_type == "TEST_CAUSE"
    assert candidates[1].cause_type == "SECOND_TEST_CAUSE"


def test_root_cause_engine_passes_findings_to_rule():

    class InspectingRule(RootCauseRule):

        def __init__(self):
            self.received_findings = None

        def matches(self, findings):
            self.received_findings = findings
            return False

        def create_candidate(self, findings):
            raise AssertionError(
                "create_candidate should not be called."
            )

    engine = RootCauseEngine()
    rule = InspectingRule()

    findings = [
        create_memory_finding()
    ]

    engine.register_rule(rule)
    engine.detect(findings)

    assert rule.received_findings is findings