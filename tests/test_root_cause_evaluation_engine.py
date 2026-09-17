from engine.finding import Finding
from engine.root_cause_candidate import RootCauseCandidate
from engine.root_cause_evaluation import RootCauseEvaluation
from engine.root_cause_evaluation_engine import (
    RootCauseEvaluationEngine,
)
from engine.root_cause_evaluation_rule import (
    RootCauseEvaluationRule,
)


def create_candidate():

    return RootCauseCandidate(
        cause_type="MEMORY_LEAK",
        category="MEMORY",
        explanation="A memory leak may be involved.",
    )


def create_finding():

    return Finding(
        finding_type="MEMORY_PRESSURE",
        category="MEMORY",
        severity="HIGH",
        description="System memory pressure is high.",
        supporting_signals=[],
    )


class MatchingRule(RootCauseEvaluationRule):

    def matches(self, candidate, findings):
        return True

    def create_evaluation(self, candidate, findings):
        return RootCauseEvaluation(
            candidate=candidate,
            supporting_evidence=[
                "MEMORY_PRESSURE",
            ],
            assessment="SUPPORTED",
            explanation=(
                "The available evidence supports "
                "this possible cause."
            ),
        )


class NonMatchingRule(RootCauseEvaluationRule):

    def matches(self, candidate, findings):
        return False

    def create_evaluation(self, candidate, findings):
        raise AssertionError(
            "create_evaluation should not be called."
        )


def test_evaluation_engine_can_be_created():

    engine = RootCauseEvaluationEngine()

    assert engine is not None


def test_evaluation_engine_starts_without_rules():

    engine = RootCauseEvaluationEngine()

    assert engine._rules == []


def test_evaluation_engine_rejects_invalid_rule():

    engine = RootCauseEvaluationEngine()

    try:
        engine.register_rule(object())
        assert False
    except ValueError:
        assert True


def test_evaluation_engine_accepts_evaluation_rule():

    engine = RootCauseEvaluationEngine()
    rule = MatchingRule()

    engine.register_rule(rule)

    assert engine._rules == [rule]


def test_evaluation_engine_returns_no_evaluations_when_no_rule_matches():

    engine = RootCauseEvaluationEngine()

    engine.register_rule(
        NonMatchingRule()
    )

    evaluations = engine.evaluate(
        create_candidate(),
        [create_finding()],
    )

    assert evaluations == []


def test_evaluation_engine_creates_evaluation_when_rule_matches():

    engine = RootCauseEvaluationEngine()

    engine.register_rule(
        MatchingRule()
    )

    evaluations = engine.evaluate(
        create_candidate(),
        [create_finding()],
    )

    assert len(evaluations) == 1

    assert isinstance(
        evaluations[0],
        RootCauseEvaluation,
    )


def test_evaluation_engine_can_generate_multiple_evaluations():

    class SecondMatchingRule(RootCauseEvaluationRule):

        def matches(self, candidate, findings):
            return True

        def create_evaluation(self, candidate, findings):
            return RootCauseEvaluation(
                candidate=candidate,
                supporting_evidence=[],
                assessment="INSUFFICIENT",
                explanation=(
                    "More evidence is required."
                ),
            )

    engine = RootCauseEvaluationEngine()

    engine.register_rule(
        MatchingRule()
    )

    engine.register_rule(
        SecondMatchingRule()
    )

    evaluations = engine.evaluate(
        create_candidate(),
        [create_finding()],
    )

    assert len(evaluations) == 2


def test_evaluation_engine_passes_candidate_to_rule():

    class InspectingRule(RootCauseEvaluationRule):

        def __init__(self):
            self.received_candidate = None

        def matches(self, candidate, findings):
            self.received_candidate = candidate
            return False

        def create_evaluation(self, candidate, findings):
            raise AssertionError(
                "create_evaluation should not be called."
            )

    engine = RootCauseEvaluationEngine()

    rule = InspectingRule()

    candidate = create_candidate()

    engine.register_rule(rule)

    engine.evaluate(
        candidate,
        [create_finding()],
    )

    assert rule.received_candidate is candidate


def test_evaluation_engine_passes_findings_to_rule():

    class InspectingRule(RootCauseEvaluationRule):

        def __init__(self):
            self.received_findings = None

        def matches(self, candidate, findings):
            self.received_findings = findings
            return False

        def create_evaluation(self, candidate, findings):
            raise AssertionError(
                "create_evaluation should not be called."
            )

    engine = RootCauseEvaluationEngine()

    rule = InspectingRule()

    findings = [
        create_finding()
    ]

    engine.register_rule(rule)

    engine.evaluate(
        create_candidate(),
        findings,
    )

    assert rule.received_findings is findings