from abc import ABC

from engine.finding import Finding
from engine.root_cause_candidate import RootCauseCandidate
from engine.root_cause_evaluation import RootCauseEvaluation
from engine.root_cause_evaluation_rule import RootCauseEvaluationRule


def create_candidate():

    return RootCauseCandidate(
        cause_type="MEMORY_LEAK",
        category="MEMORY",
        explanation=(
            "A memory leak may be contributing to "
            "the observed memory pressure."
        ),
    )


def create_finding():

    return Finding(
        finding_type="MEMORY_PRESSURE",
        category="MEMORY",
        severity="HIGH",
        description="System memory pressure is high.",
        supporting_signals=[],
    )


class MatchingEvaluationRule(RootCauseEvaluationRule):

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
                "The observed memory pressure "
                "supports this possible cause."
            ),
        )


class NonMatchingEvaluationRule(RootCauseEvaluationRule):

    def matches(self, candidate, findings):
        return False

    def create_evaluation(self, candidate, findings):
        raise AssertionError(
            "create_evaluation should not be called."
        )


def test_root_cause_evaluation_rule_is_abstract():

    assert issubclass(
        RootCauseEvaluationRule,
        ABC,
    )


def test_root_cause_evaluation_rule_requires_matches():

    assert hasattr(
        RootCauseEvaluationRule,
        "matches",
    )


def test_root_cause_evaluation_rule_requires_create_evaluation():

    assert hasattr(
        RootCauseEvaluationRule,
        "create_evaluation",
    )


def test_matching_evaluation_rule_can_be_implemented():

    rule = MatchingEvaluationRule()

    candidate = create_candidate()
    findings = [
        create_finding()
    ]

    assert rule.matches(
        candidate,
        findings,
    )


def test_matching_rule_creates_root_cause_evaluation():

    rule = MatchingEvaluationRule()

    candidate = create_candidate()
    findings = [
        create_finding()
    ]

    evaluation = rule.create_evaluation(
        candidate,
        findings,
    )

    assert isinstance(
        evaluation,
        RootCauseEvaluation,
    )


def test_evaluation_rule_receives_candidate():

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

    rule = InspectingRule()
    candidate = create_candidate()

    rule.matches(
        candidate,
        [create_finding()],
    )

    assert rule.received_candidate is candidate


def test_evaluation_rule_receives_findings():

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

    rule = InspectingRule()

    findings = [
        create_finding()
    ]

    rule.matches(
        create_candidate(),
        findings,
    )

    assert rule.received_findings is findings


def test_evaluation_rule_does_not_make_candidate_primary():

    rule = MatchingEvaluationRule()

    candidate = create_candidate()

    evaluation = rule.create_evaluation(
        candidate,
        [create_finding()],
    )

    assert not hasattr(
        evaluation,
        "is_primary",
    )

    assert not hasattr(
        evaluation,
        "selected",
    )


def test_non_matching_rule_does_not_create_evaluation():

    rule = NonMatchingEvaluationRule()

    candidate = create_candidate()

    assert not rule.matches(
        candidate,
        [create_finding()],
    )