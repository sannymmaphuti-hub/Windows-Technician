from engine.finding import Finding
from engine.root_cause_candidate import RootCauseCandidate
from engine.root_cause_evaluation import RootCauseEvaluation
from engine.root_cause_evaluation_rule import RootCauseEvaluationRule
from engine.memory_intensive_process_evaluation_rule import (
    MemoryIntensiveProcessEvaluationRule,
)


def create_candidate():

    return RootCauseCandidate(
        cause_type="MEMORY_INTENSIVE_PROCESS",
        category="MEMORY",
        explanation=(
            "A memory-intensive process may be contributing "
            "to the observed memory pressure."
        ),
    )


def create_memory_finding():

    return Finding(
        finding_type="MEMORY_PRESSURE",
        category="MEMORY",
        severity="HIGH",
        description="System memory pressure is high.",
        supporting_signals=[],
    )


def create_cpu_finding():

    return Finding(
        finding_type="CPU_PRESSURE",
        category="CPU",
        severity="HIGH",
        description="System CPU pressure is high.",
        supporting_signals=[],
    )


def test_rule_is_root_cause_evaluation_rule():

    rule = MemoryIntensiveProcessEvaluationRule()

    assert isinstance(
        rule,
        RootCauseEvaluationRule,
    )


def test_rule_matches_memory_candidate_with_memory_pressure():

    rule = MemoryIntensiveProcessEvaluationRule()

    assert rule.matches(
        create_candidate(),
        [create_memory_finding()],
    )


def test_rule_does_not_match_unrelated_candidate():

    rule = MemoryIntensiveProcessEvaluationRule()

    candidate = RootCauseCandidate(
        cause_type="MEMORY_LEAK",
        category="MEMORY",
        explanation="A memory leak may be involved.",
    )

    assert not rule.matches(
        candidate,
        [create_memory_finding()],
    )


def test_rule_does_not_match_without_memory_pressure():

    rule = MemoryIntensiveProcessEvaluationRule()

    assert not rule.matches(
        create_candidate(),
        [create_cpu_finding()],
    )


def test_rule_creates_evaluation():

    rule = MemoryIntensiveProcessEvaluationRule()

    evaluation = rule.create_evaluation(
        create_candidate(),
        [create_memory_finding()],
    )

    assert isinstance(
        evaluation,
        RootCauseEvaluation,
    )


def test_memory_pressure_alone_is_insufficient():

    rule = MemoryIntensiveProcessEvaluationRule()

    evaluation = rule.create_evaluation(
        create_candidate(),
        [create_memory_finding()],
    )

    assert (
        evaluation.assessment
        == "INSUFFICIENT"
    )


def test_evaluation_preserves_candidate():

    rule = MemoryIntensiveProcessEvaluationRule()

    candidate = create_candidate()

    evaluation = rule.create_evaluation(
        candidate,
        [create_memory_finding()],
    )

    assert evaluation.candidate is candidate


def test_evaluation_explains_insufficient_evidence():

    rule = MemoryIntensiveProcessEvaluationRule()

    evaluation = rule.create_evaluation(
        create_candidate(),
        [create_memory_finding()],
    )

    explanation = evaluation.explanation.lower()

    assert "insufficient" in explanation
    assert "process" in explanation


def test_evaluation_does_not_claim_primary_cause():

    rule = MemoryIntensiveProcessEvaluationRule()

    evaluation = rule.create_evaluation(
        create_candidate(),
        [create_memory_finding()],
    )

    assert not hasattr(
        evaluation,
        "is_primary",
    )

    assert not hasattr(
        evaluation,
        "selected",
    )