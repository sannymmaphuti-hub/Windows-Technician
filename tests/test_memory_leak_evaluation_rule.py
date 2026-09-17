from engine.finding import Finding
from engine.root_cause_candidate import RootCauseCandidate
from engine.root_cause_evaluation import RootCauseEvaluation
from engine.root_cause_evaluation_rule import RootCauseEvaluationRule
from engine.memory_leak_evaluation_rule import (
    MemoryLeakEvaluationRule,
)


def create_candidate():

    return RootCauseCandidate(
        cause_type="MEMORY_LEAK",
        category="MEMORY",
        explanation=(
            "A memory leak may be contributing to the "
            "observed memory pressure."
        ),
    )


def create_memory_pressure_finding():

    return Finding(
        finding_type="MEMORY_PRESSURE",
        category="MEMORY",
        severity="HIGH",
        description="System memory pressure is high.",
        supporting_signals=[],
    )


def create_memory_growth_finding():

    return Finding(
        finding_type="MEMORY_GROWTH_OVER_TIME",
        category="MEMORY",
        severity="HIGH",
        description=(
            "A process has shown sustained memory growth "
            "over time."
        ),
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

    rule = MemoryLeakEvaluationRule()

    assert isinstance(
        rule,
        RootCauseEvaluationRule,
    )


def test_rule_matches_memory_leak_candidate_with_memory_pressure():

    rule = MemoryLeakEvaluationRule()

    assert rule.matches(
        create_candidate(),
        [create_memory_pressure_finding()],
    )


def test_rule_does_not_match_unrelated_candidate():

    rule = MemoryLeakEvaluationRule()

    candidate = RootCauseCandidate(
        cause_type="MEMORY_INTENSIVE_PROCESS",
        category="MEMORY",
        explanation=(
            "A memory-intensive process may be involved."
        ),
    )

    assert not rule.matches(
        candidate,
        [create_memory_pressure_finding()],
    )


def test_rule_does_not_match_without_memory_pressure():

    rule = MemoryLeakEvaluationRule()

    assert not rule.matches(
        create_candidate(),
        [create_cpu_finding()],
    )


def test_rule_creates_evaluation():

    rule = MemoryLeakEvaluationRule()

    evaluation = rule.create_evaluation(
        create_candidate(),
        [create_memory_pressure_finding()],
    )

    assert isinstance(
        evaluation,
        RootCauseEvaluation,
    )


def test_memory_pressure_alone_is_insufficient():

    rule = MemoryLeakEvaluationRule()

    evaluation = rule.create_evaluation(
        create_candidate(),
        [create_memory_pressure_finding()],
    )

    assert (
        evaluation.assessment
        == "INSUFFICIENT"
    )


def test_memory_growth_improves_assessment():

    rule = MemoryLeakEvaluationRule()

    findings = [
        create_memory_pressure_finding(),
        create_memory_growth_finding(),
    ]

    evaluation = rule.create_evaluation(
        create_candidate(),
        findings,
    )

    assert (
        evaluation.assessment
        == "SUPPORTED"
    )


def test_evaluation_preserves_memory_growth_evidence():

    rule = MemoryLeakEvaluationRule()

    growth_finding = create_memory_growth_finding()

    findings = [
        create_memory_pressure_finding(),
        growth_finding,
    ]

    evaluation = rule.create_evaluation(
        create_candidate(),
        findings,
    )

    assert growth_finding in evaluation.supporting_evidence


def test_evaluation_preserves_memory_pressure_evidence():

    rule = MemoryLeakEvaluationRule()

    pressure_finding = create_memory_pressure_finding()

    findings = [
        pressure_finding,
        create_memory_growth_finding(),
    ]

    evaluation = rule.create_evaluation(
        create_candidate(),
        findings,
    )

    assert pressure_finding in evaluation.supporting_evidence


def test_evaluation_explains_memory_growth():

    rule = MemoryLeakEvaluationRule()

    findings = [
        create_memory_pressure_finding(),
        create_memory_growth_finding(),
    ]

    evaluation = rule.create_evaluation(
        create_candidate(),
        findings,
    )

    explanation = evaluation.explanation.lower()

    assert "memory" in explanation
    assert "growth" in explanation
    assert "supports" in explanation


def test_evaluation_remains_uncertain():

    rule = MemoryLeakEvaluationRule()

    findings = [
        create_memory_pressure_finding(),
        create_memory_growth_finding(),
    ]

    evaluation = rule.create_evaluation(
        create_candidate(),
        findings,
    )

    explanation = evaluation.explanation.lower()

    assert (
        "may" in explanation
        or "possible" in explanation
        or "suggest" in explanation
        or "supports" in explanation
    )


def test_evaluation_does_not_select_primary_cause():

    rule = MemoryLeakEvaluationRule()

    findings = [
        create_memory_pressure_finding(),
        create_memory_growth_finding(),
    ]

    evaluation = rule.create_evaluation(
        create_candidate(),
        findings,
    )

    assert not hasattr(
        evaluation,
        "is_primary",
    )

    assert not hasattr(
        evaluation,
        "selected",
    )


def test_unrelated_cpu_finding_does_not_replace_memory_evidence():

    rule = MemoryLeakEvaluationRule()

    findings = [
        create_memory_pressure_finding(),
        create_memory_growth_finding(),
        create_cpu_finding(),
    ]

    evaluation = rule.create_evaluation(
        create_candidate(),
        findings,
    )

    assert (
        evaluation.assessment
        == "SUPPORTED"
    )


def test_rule_still_requires_memory_pressure():

    rule = MemoryLeakEvaluationRule()

    findings = [
        create_memory_growth_finding(),
    ]

    assert not rule.matches(
        create_candidate(),
        findings,
    )